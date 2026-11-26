"""Tests of the list of devices handed to Daniel's container, on a fake /dev."""
import os
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

    def test_sd_card_system_disk(self):
        handed = self.handed(["mmcblk0", "mmcblk0p1", "mmcblk0p2", "mmcblk0boot0", "mmcblk0rpmb",
                              "mmcblk1", "mmcblk1p1", "gpiochip0"], ["mmcblk0"])
        self.assertEqual(handed, {"mmcblk1", "mmcblk1p1", "gpiochip0"})


if __name__ == "__main__":
    unittest.main()
