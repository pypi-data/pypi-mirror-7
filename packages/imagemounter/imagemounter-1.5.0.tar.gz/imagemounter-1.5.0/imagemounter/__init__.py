from __future__ import print_function
from __future__ import unicode_literals

__ALL__ = ['Volume', 'Disk', 'ImageParser']
__version__ = '1.5.0'

BLOCK_SIZE = 512
VOLUME_SYSTEM_TYPES = ('detect', 'dos', 'bsd', 'sun', 'mac', 'gpt', 'dbfiller')
FILE_SYSTEM_TYPES = ('ext', 'ufs', 'ntfs', 'luks', 'lvm', 'unknown')

import sys
import os

from imagemounter import util
from imagemounter.disk import Disk
from imagemounter.volume import Volume


class ImageParser(object):
    def __init__(self, paths, out=sys.stdout, verbose=False, color=False, **args):
        # Python 3 compatibility
        if sys.version_info[0] == 2:
            string_types = basestring
        else:
            string_types = str

        if isinstance(paths, string_types):
            self.paths = [paths]
        else:
            self.paths = paths
        self.out = out
        self.verbose = verbose
        self.verbose_color = color
        self.args = args

        self.disks = []
        for path in self.paths:
            self.disks.append(Disk(self, path, **self.args))

    def _debug(self, val):
        if self.verbose:
            if self.verbose_color:
                from termcolor import colored
                print(colored(val, "cyan"), file=self.out)
            else:
                print(val, file=self.out)

    def init(self, single=None, raid=True):
        for d in self.disks:
            for v in d.init(single, raid):
                yield v

    def mount_disks(self):
        """Mounts all disks in the parser."""

        result = True
        for disk in self.disks:
            result = disk.mount() and result
        return result

    def rw_active(self):
        """Indicates whether any RW cache is active."""
        result = False
        for disk in self.disks:
            result = disk.rw_active() or result
        return result

    mount_base = mount_disks  # backwards compatibility

    def mount_raid(self):
        """Crates a RAID device and adds all devices to the RAID. Returns True if all devices were added
        successfully. Should be called before mount_disks.
        """

        result = True
        for disk in self.disks:
            result = disk.add_to_raid() and result
        return result

    def mount_single_volume(self):
        """Mounts all disks as single volume."""

        for disk in self.disks:
            self._debug("    Mounting volumes in {0}".format(disk))
            for volume in disk.mount_single_volume():
                yield volume

    def mount_multiple_volumes(self):
        """Mounts all disks as volume system"""

        for disk in self.disks:
            self._debug("    Mounting volumes in {0}".format(disk))
            for volume in disk.mount_multiple_volumes():
                yield volume

    def mount_volumes(self, single=None):
        """Mounts all volumes in all disks. Call mount_disks first."""

        for disk in self.disks:
            self._debug("    Mounting volumes in {0}".format(disk))
            for volume in disk.mount_volumes(single):
                yield volume

    def get_volumes(self):
        volumes = []
        for disk in self.disks:
            volumes.extend(disk.get_volumes())
        return volumes

    def clean(self, remove_rw=False):
        """Cleans everything."""

        # To ensure clean unmount after reconstruct, we sort across all volumes in all our disks to provide a proper
        # order
        volumes = list(sorted(self.get_volumes(), key=lambda v: v.mountpoint or "", reverse=True))
        for v in volumes:
            if not v.unmount():
                self._debug("[-] Error unmounting volume {0}".format(v.mountpoint))

        # Now just clean the rest.
        for disk in self.disks:
            if not disk.unmount(remove_rw):
                self._debug("[-] Error unmounting {0}".format(disk))
                return False

        return True

    def reconstruct(self):
        """Reconstructs the filesystem of all volumes mounted by the parser by inspecting the last mount point and
        bind mounting everything.
        """
        volumes = list(sorted((v for v in self.get_volumes() if v.mountpoint and v.lastmountpoint),
                              key=lambda v: v.mountpoint or "", reverse=True))

        try:
            root = list(filter(lambda x: x.lastmountpoint == '/', volumes))[0]
        except IndexError:
            self._debug("[-] Could not find / while reconstructing, aborting!")
            return None

        volumes.remove(root)

        for v in volumes:
            v.bindmount(os.path.join(root.mountpoint, v.lastmountpoint[1:]))
        return root

    @staticmethod
    def force_clean(execute=True):
        return util.force_clean(execute)

