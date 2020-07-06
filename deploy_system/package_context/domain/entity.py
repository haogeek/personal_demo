# coding=utf-8
"""Entities of package context."""

# Import built-in modules
from collections import OrderedDict

# Import local context domain objects
from value_object import VersionNumber


class Package(object):
    """Package entity of package context. Work as aggregate root."""

    def __init__(self, package_name, version_number=''):
        """Initialize package entity.

        Args:
            package_name (str): Name of the package. Only works when code
            repository can find a source with this name.
            version_number (VersionNumber): Current version of this package.
        """
        self.name = package_name
        self.build_module = None
        self.current_version = version_number
        self.new_version = None
        self.builder = None

    def build(self):
        """Call builder to build this package."""
        self.builder.build()

    def upgrade_version(self, level):
        """

        Args:
            level (str): Level name of the version number string.

        Returns (VersionNumber): New version of this package to be used for
            deployment.

        """
        version_digits = self.current_version.split('.')
        version_dict = OrderedDict([('major', version_digits[0]),
                                    ('minor', version_digits[1]),
                                    ('fix', version_digits[2])])

        flag = False
        for key in version_dict.keys():
            if flag:
                version_dict[key] = '0'
            if key == level:
                version_dict[key] = str(int(version_dict[key]) + 1)
                flag = True
        self.new_version = VersionNumber('.'.join(version_dict.values()))
