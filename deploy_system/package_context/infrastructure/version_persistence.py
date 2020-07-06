# coding=utf-8

# Import built-in modules
from collections import OrderedDict
import json

# Import framework utilities
from deploy_system.utils.ioc import register, dependency

# Import local context domain objects
from deploy_system.package_context.domain.repository import VersionRepository
from deploy_system.package_context.domain.value_object import VersionNumber

# Import local modules
from constants import PACKAGE_VERSION_DB


# Register this class as the implementation of version repository.
@register('version_repo')
class VersionPersistence(VersionRepository):
    """Implementation of version repository."""

    def __init__(self):
        """Load data of package versions from database file."""
        try:
            with open(PACKAGE_VERSION_DB, 'r') as db:
                self.package_version_data = json.load(db)
        except Exception as exc:
            raise IOError('Can\'t open database file {}, '
                          'see detail:\n{}'.format(PACKAGE_VERSION_DB,
                                                   exc.message))

    def validate(self, package_name, package_type):
        if package_name in self.package_version_data and \
                self.package_version_data[package_name]['type'] != package_type:
            return False
        return True

    def get_package_version(self, package_name):
        """Get current deployed version of specific package.

        If the package doesn't exist in database, it will return an initial
        version number '0.0.0'.

        Args:
            package_name (str): Name of the package.

        Returns (VersionNumber): Value object represents current version of the
            package.

        """
        try:
            version_string = self.package_version_data[package_name]['version']
            return VersionNumber(version_string)
        except KeyError:
            return VersionNumber('0.0.0')

    @dependency('package_repo')
    def update(self, package_name, package_type, package_repo=None):
        """Update version information of a package in package version data.

        Args:
            package_name (str): Name of the package.
            package_repo (PackageRepository): Implementation class of package
                repository.

        """
        package = package_repo.get(package_name)
        new_version = package.new_version
        try:
            self.package_version_data[package_name]['version'] = new_version
        except (KeyError, TypeError):
            self.package_version_data[package_name] = {
                'version': new_version,
                'type': package_type
            }

    def write(self):
        """Store updated package version information into database."""
        with open(PACKAGE_VERSION_DB, 'w') as db:
            json.dump(self.package_version_data, db, indent=4)
