# -*- coding: utf-8 -*-

"""Helper module to work with files."""

import re
import os
import logging
import fnmatch
from .exceptions import FileNotFoundError

MAXLEN = 120
ILEGAL = r'<>:"/\|?*'
LOGGER = logging.getLogger(__name__)


class File(object):

    """Easy manipulation of files on the SAME directory."""

    def __init__(self, fp):
        """Set and validate the basic properties."""
        if not self.exists(fp):
            raise FileNotFoundError(fp)
        self.path = os.path.dirname(fp) or os.getcwd()
        self.basename = os.path.basename(fp)
        self.name, self.ext = os.path.splitext(self.basename)

    def siblings(self):
        """Collect files and folders in the same folder."""
        return [f for f in os.listdir(self.path) if f != self.basename]

    @staticmethod
    def exists(fp):
        """Check if a given filepath exists."""
        return True if os.path.isfile(fp) else False

    @staticmethod
    def mkwinsafe(name, space=' '):
        """Delete most common characters not allowed in Windows filenames."""
        space = space if space not in ILEGAL else ' '
        name = ''.join(c for c in name if c not in ILEGAL)\
               .replace(' ', space).strip()
        name = re.sub(r'\s\s+', ' ', name) if space == ' ' else name
        return name[:MAXLEN]

    @staticmethod
    def validate(basename):
        """Check for a proper basename."""
        if basename != os.path.basename(basename):
            LOGGER.critical("This (%s) is not a basename!", basename)
            return False
        name, ext = os.path.splitext(basename)
        if len(name) == 0:
            LOGGER.critical("Not a valid name (lenght 0)!")
            return False
        if len(ext) == 0:
            LOGGER.critical("Not a valid extension (lenght 0)!")
            return False
        return True

    def baserename(self, new_basename):
        """Rename the file to a 'safe' basename."""
        if not self.validate(new_basename):
            return False
        name, ext = os.path.splitext(new_basename)
        name = self.mkwinsafe(name)
        new_basename = name + ext
        if new_basename == self.basename:
            return True
        if new_basename not in self.siblings():
            try:
                os.rename(self.basename, new_basename)
            except OSError as e:
                LOGGER.critical("%s", e.message)
                return False
            self.basename = new_basename
            self.name = name
            self.ext = ext
            return True
        else:
            LOGGER.info("The file (%s) already exists in the directory!",
                        new_basename)
            return True


def cwdfiles(pattern='*'):
    """List the files in current directory that match a given pattern."""
    return fnmatch.filter(os.listdir('.'), pattern)
