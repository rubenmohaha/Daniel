#!/usr/bin/env python3
"""List the devices that the fixed part hands to Ipse's container.

Every character and block device that Linux exposes under /dev is handed to
the container, without interpretation, except:

* the disk that holds the robot's Linux system and the mind account, with
  its partitions and the other device nodes that reach the same disk;
* the devices that hold swapped-out working memory (swap partitions, swap
  files' disks and compressed swap in memory such as zram);
* the devices that give direct access to the machine's working memory
  (/dev/mem, /dev/kmem, /dev/port, and every zram device, swap or not);
* the real-time clocks (/dev/rtc*), so that Ipse cannot change the clock.

The means of controlling Docker is not a device and is never handed over.

Usage: ipse_devices.py [--dev DIR] [--sys DIR] [--protect PATH ...]
Prints one `--device=...` argument per line, ready for `docker run`.
"""

import argparse
import os
import stat
import subprocess
import sys

# Directories that Docker already provides inside every container.
SKIPPED_DIRS = {"pts", "shm", "mqueue", "hugepages"}

# Device nodes that Docker already provides inside every container.
PROVIDED = {"null", "zero", "full", "random", "urandom", "tty", "console", "ptmx"}

# Direct access to working memory and I/O ports.
MEMORY_DEVICES = {"mem", "kmem", "port"}


def disk_of_path(path):
    """Return the names of the whole disks that hold the filesystem at `path`."""
    source = subprocess.run(
        ["findmnt", "-n", "-o", "SOURCE", "--target", path],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    source = source.split("[")[0]  # btrfs subvolumes: /dev/sda2[/@]
    return disk_of_device(source)


def disk_of_device(source):
    """Return the names of the whole disks under a block device."""
    ancestors = subprocess.run(
        ["lsblk", "-n", "-r", "-s", "-o", "NAME,TYPE", source],
        capture_output=True, text=True, check=True,
    ).stdout.split("\n")
    return {
        line.split()[0] for line in ancestors
        if len(line.split()) == 2 and line.split()[1] == "disk"
    }


def swap_disks(swaps_file="/proc/swaps"):
    """Return the names of the disks that hold swapped-out working memory."""
    disks = set()
    try:
        with open(swaps_file) as f:
            lines = f.read().splitlines()[1:]
    except OSError:
        return disks
    for line in lines:
        fields = line.split()
        if len(fields) < 2:
            continue
        name, kind = fields[0], fields[1]
        disks |= disk_of_device(name) if kind == "partition" else disk_of_path(name)
    return disks


def protected_names(disks, sys_dir="/sys"):
    """Return (name prefixes, exact names) of the device nodes that reach the given disks."""
    prefixes, exact = set(), set()
    for disk in disks:
        prefixes.add(disk)  # the disk and its partitions (sda1, nvme0n1p1, mmcblk0p1)
        if disk.startswith("nvme") and "n" in disk[4:]:
            controller, namespace = disk[4:].split("n", 1)
            prefixes.add("nvme" + controller)          # controller character device
            prefixes.add("ng" + controller + "n" + namespace)  # generic character device
        generic = os.path.join(sys_dir, "class", "block", disk, "device", "scsi_generic")
        if os.path.isdir(generic):
            exact.update(os.listdir(generic))         # sg0 and similar
    return prefixes, exact


def is_excluded(name, protected):
    prefixes, exact = protected
    if name in PROVIDED or name in MEMORY_DEVICES or name.startswith("zram") or name.startswith("rtc") or name in exact:
        return True
    for prefix in prefixes:
        if name == prefix:
            return True
        if name.startswith(prefix):
            rest = name[len(prefix):]
            # sda -> sda1 ; nvme0n1 -> nvme0n1p1 ; mmcblk0 -> mmcblk0p1, mmcblk0boot0
            if rest[0].isdigit() or rest[0] in "pn" or rest.startswith(("boot", "rpmb")):
                return True
    return False


def devices(dev_dir, protected):
    """Yield the absolute paths of the device nodes to hand to the container."""
    for root, dirs, files in os.walk(dev_dir):
        if root == dev_dir:
            dirs[:] = [d for d in dirs if d not in SKIPPED_DIRS]
        dirs.sort()
        for name in sorted(files):
            path = os.path.join(root, name)
            try:
                mode = os.lstat(path).st_mode
            except OSError:
                continue
            if not (stat.S_ISCHR(mode) or stat.S_ISBLK(mode)):
                continue  # symbolic links, sockets and ordinary files
            if is_excluded(name, protected):
                continue
            yield path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dev", default="/dev")
    parser.add_argument("--sys", default="/sys")
    parser.add_argument("--protect", nargs="*", default=["/", "/var/lib/ipse", "/var/lib/docker"],
                        help="paths whose disks are never handed to the container")
    parser.add_argument("--disk", nargs="*", default=None,
                        help="name the protected disks directly instead of finding them")
    parser.add_argument("--print-protected", action="store_true",
                        help="print the names of the protected disks and stop")
    args = parser.parse_args(argv)

    if args.disk is not None:
        disks = set(args.disk)
    else:
        disks = set()
        for path in args.protect:
            if os.path.exists(path):
                disks |= disk_of_path(path)
        if not disks:
            sys.exit("ipse_devices: could not find the system disk; refusing to continue")
        disks |= swap_disks()
    if args.print_protected:
        print("\n".join(sorted(disks)))
        return
    protected = protected_names(disks, args.sys)
    for path in devices(args.dev, protected):
        inside = "/dev/" + os.path.relpath(path, args.dev)
        print(f"--device={path}:{inside}")


if __name__ == "__main__":
    main()
