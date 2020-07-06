# coding=utf-8
"""Implementation of package related operator."""

# Import framework utilities
from deploy_system.utils.ioc import register

# Import local context domain objects
from deploy_system.package_context.domain.repository import PackageRepository


# Register this class as the implementation of package repository.
@register('package_repo')
class PackagePersistence(PackageRepository):
    """Implementation of package repository."""

    # Storage of packages.
    __packages__ = {}

    @classmethod
    def get(cls, package_name):
        """Get a package entity from storage with given package name.

        Args:
            package_name (str): Name of a package.

        Returns (Package): The package entity relevant to the given name.

        """
        return cls.__packages__.get(package_name)

    @classmethod
    def update(cls, package):
        """Update a package in storage.

        If the package doesn't exist in storage, it will be inserted to.

        Args:
            package (Package): A package entity.

        """
        cls.__packages__[package.name] = package
