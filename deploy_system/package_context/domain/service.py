# coding=utf-8
"""Domain services of package context."""

# Import local context domain objects
from entity import Package
from value_object import VersionNumber


class DuplicatedPackageNameError(Exception):
    pass


class ValidatePackageService(object):
    def __init__(self, version_repo):
        self.version_repo = version_repo

    def validate(self, package_name, package_type):
        if not self.version_repo.validate(package_name, package_type):
            existing_type = 'internal'
            if package_type == 'internal':
                existing_type = 'external'
            msg = ('Package {} already exists in {}, '
                   'you can not deploy in {}.').format(package_name,
                                                       existing_type,
                                                       package_type)
            raise DuplicatedPackageNameError(msg)


class CreatePackageService(object):
    def __init__(self, code_repo, version_repo, package_repo):
        self.code_repo = code_repo
        self.version_repo = version_repo
        self.package_repo = package_repo

    def create_package(self, package_name, package_type):
        package = Package(package_name)
        if package_type == 'internal':
            current_version = GetCurrentVersionService(
                self.version_repo).get_current_version(package_name)
            package.current_version = current_version
        self.code_repo.get_code(package_name, package_type)
        package.build_module = self.code_repo.get_build_module(package_name)
        self.package_repo.update(package)


class DeployPackageService(object):
    def __init__(self, code_repo, version_repo, package_repo,):
        self.code_repo = code_repo
        self.version_repo = version_repo
        self.package_repo = package_repo

    def deploy(self, package_name, package_type, level='', version_number=''):
        deploy_version_service = GetDeployVersionService(self.package_repo,
                                                         self.version_repo)
        version = deploy_version_service.get_deploy_version(package_name,
                                                            package_type,
                                                            level,
                                                            version_number)

        return self._deploy(package_name, package_type, version)

    def _deploy(self, package_name, package_type, version_number):
        self.code_repo.deploy(package_name, package_type, version_number)


class GetDeployVersionService(object):
    def __init__(self, package_repo, version_repo):
        self.package_repo = package_repo
        self.version_repo = version_repo

    def get_deploy_version(self, package_name, package_type, level, version):
        if version and level:
            level = ''

        package = self.package_repo.get(package_name)

        if package_type == 'internal':
            if level:
                assert level in ('major', 'minor', 'fix'), \
                    "level should be one of 'major', 'minor', 'fix'."
                package.upgrade_version(level)
                version = package.new_version
            assert version != '', \
                "You should specify the deployment level or version number."
            assert VersionNumber.validate_internal(version)
        elif package_type == 'external':
            assert version != '', \
                "You should specify the version number."
            package.new_version = VersionNumber(version)

        self.package_repo.update(package)
        self.version_repo.update(package_name, package_type)
        self.version_repo.write()
        return version


class GetCurrentVersionService(object):
    def __init__(self, version_repo):
        self.version_repo = version_repo

    def get_current_version(self, package_name):
        return self.version_repo.get_package_version(package_name)
