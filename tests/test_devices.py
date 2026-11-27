"""Tests of the list of devices handed to Daniel's container.

The class Devices works on a fake /dev. The class StackedDevices builds real
devices on this machine, as a system installed on a logical volume, an
encrypted volume or a RAID array has them.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fixed"))
import daniel_devices  # noqa: E402


@unittest.skipUnless(os.geteuid() == 0, "creating device nodes requires root")
class Devices(unittest.TestCase):
    def handed(self, names, disks):
        dev = tempfile.mkdtemp()
        sys_dir = tempfile.mkdtemp()
        for name in names:
            path = os.path.join(dev, name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            os.mknod(path, 0o600 | (0o060000 if name.startswith(("sd", "nvme0n", "mmc")) else 0o020000), os.makedev(1, 3))
        os.symlink("sda1", os.path.join(dev, "root"))
        generic = os.path.join(sys_dir, "class/block/sda/device/scsi_generic/sg0")
        os.makedirs(generic)
        protected = daniel_devices.protected_names(set(disks), sys_dir)
        return {os.path.relpath(p, dev) for p in daniel_devices.devices(dev, protected)}

    def test_system_disk_and_clock_are_excluded(self):
        handed = self.handed(
            ["sda", "sda1", "sda2", "sdb", "sdb1", "sg0", "sg1", "mem", "kmem", "port",
             "rtc0", "zram0", "null", "pts/0", "video0", "snd/pcmC0D0p", "i2c-1", "ttyUSB0"],
            ["sda"])
        self.assertEqual(handed, {"sdb", "sdb1", "sg1", "mem", "kmem", "port", "zram0", "video0", "snd/pcmC0D0p", "i2c-1", "ttyUSB0"})

    def test_nvme_system_disk(self):
        handed = self.handed(["nvme0", "nvme0n1", "nvme0n1p1", "ng0n1", "nvme1", "nvme1n1"], ["nvme0n1"])
        self.assertEqual(handed, {"nvme1", "nvme1n1"})

    def test_nodes_that_docker_cannot_be_given_are_left_out(self):
        handed = self.handed(["bsg/0:0:0:0", "bsg/1:0:0:0", "odd name", "video0"], ["sda"])
        self.assertEqual(handed, {"video0"})

    def test_another_name_for_a_protected_device_is_left_out(self):
        dev = tempfile.mkdtemp()
        for name, kind, numbers in [("root", 0o060000, (8, 1)), ("dm-0", 0o060000, (253, 0)),
                                    ("dm-1", 0o060000, (253, 1)), ("ttyS1", 0o020000, (8, 1))]:
            os.mknod(os.path.join(dev, name), 0o600 | kind, os.makedev(*numbers))
        handed = daniel_devices.devices(dev, (set(), set()), {(8, 1), (253, 0)})
        # dm-1 is another volume; ttyS1 is a character device that only shares the numbers
        self.assertEqual({os.path.relpath(path, dev) for path in handed}, {"dm-1", "ttyS1"})

    def test_sd_card_system_disk(self):
        handed = self.handed(["mmcblk0", "mmcblk0p1", "mmcblk0p2", "mmcblk0boot0", "mmcblk0rpmb",
                              "mmcblk1", "mmcblk1p1", "gpiochip0"], ["mmcblk0"])
        self.assertEqual(handed, {"mmcblk1", "mmcblk1p1", "gpiochip0"})


CAN_STACK = os.geteuid() == 0 and all(shutil.which(tool) for tool in ["losetup", "dmsetup", "mkfs.ext4"])


@unittest.skipUnless(CAN_STACK, "building a device on another requires root, losetup, dmsetup and mkfs.ext4")
class StackedDevices(unittest.TestCase):
    """A filesystem on a device that is built on a disk and has a name of its own."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        image = os.path.join(self.tmp, "disk.img")
        with open(image, "wb") as f:
            f.truncate(64 << 20)
        run = lambda *command: subprocess.run(command, capture_output=True, text=True, check=True).stdout.strip()
        self.disk = run("losetup", "--find", "--show", image)        # stands for the system disk
        self.addCleanup(subprocess.run, ["losetup", "--detach", self.disk], capture_output=True)
        name = f"danieltest{os.getpid()}"
        run("dmsetup", "create", name, "--table", f"0 {run('blockdev', '--getsz', self.disk)} linear {self.disk} 0")
        self.addCleanup(subprocess.run, ["dmsetup", "remove", "--retry", name], capture_output=True)
        self.volume = os.path.realpath("/dev/mapper/" + name)        # /dev/dm-N, built on the disk
        run("mkfs.ext4", "-q", self.volume)
        self.mounted = os.path.join(self.tmp, "mounted")
        os.mkdir(self.mounted)
        run("mount", self.volume, self.mounted)
        self.addCleanup(subprocess.run, ["umount", self.mounted], capture_output=True)

    def test_a_device_built_on_the_protected_disk_is_not_handed_over(self):
        listed = subprocess.run([sys.executable, os.path.join(HERE, "..", "fixed", "daniel_devices.py"),
                                 "--protect", self.mounted], capture_output=True, text=True)
        self.assertEqual(listed.returncode, 0, listed.stderr)
        handed = {line.split("=", 1)[1].split(":")[0] for line in listed.stdout.split()}
        self.assertIn("/dev/loop-control", handed)   # the other devices are still handed over
        self.assertNotIn(self.disk, handed)
        self.assertNotIn(self.volume, handed)


if __name__ == "__main__":
    unittest.main()
