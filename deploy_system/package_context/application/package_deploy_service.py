# coding=utf-8
"""Application service module applies deploying package service."""

# Import framework utilities
from deploy_system.utils.ioc import dependency

# Import local context domain services
from deploy_system.package_context.domain.service import (CreatePackageService,
                                                          DeployPackageService)


class PackageDeployService(object):
    """Package deploy service class.

    Main function for this class is deploy(), it will call build() and clear().

    """

    # Dependency injection
    @dependency('code_repo')
    @dependency('version_repo')
    @dependency('package_repo')
    def __init__(self, code_repo=None, version_repo=None, package_repo=None):
        """Initialize the service.

        Use dependency injection technique to get actual implementation class
        of code repository, version repository and package repository.

        """
        self.code_repo = code_repo()
        self.version_repo = version_repo()
        self.package_repo = package_repo()
        self.package_service = CreatePackageService(self.code_repo,
                                                    self.version_repo,
                                                    self.package_repo)
        self.deploy_service = DeployPackageService(self.code_repo,
                                                   self.version_repo,
                                                   self.package_repo)

    def build(self, package_name):
        """Prepare staging area of specific package and build the package."""
        self.code_repo.prepare_staging(package_name)
        # In DDD tactical design, we do not directly transfer an entity from
        # one context into another, but we use unique identify to get the entity
        # from its repository.
        package = self.package_repo.get(package_name)
        package.build()

    def deploy(self, package_name, package_type, level='', version_number=''):
        """Public interface of this service.

        It will arrange the full user case of deployment.

        """
        assert package_type in ('internal', 'external'), \
            "package_type should be either 'internal' or 'external'."
        self.package_service.create_package(package_name, package_type)
        self.build(package_name)
        self.deploy_service.deploy(package_name,
                                   package_type,
                                   level,
                                   version_number)
        self.clear(package_name)

    def clear(self, package_name):
        """Remove specific package from source and staging area."""
        self.code_repo.clear(package_name)
