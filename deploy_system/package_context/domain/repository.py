# coding=utf-8

from abc import ABCMeta, abstractmethod


class CodeRepository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_code(self):
        pass

    @abstractmethod
    def get_build_module(self, package_name):
        pass

    @abstractmethod
    def deploy(self, package_name, version_number, package_type):
        pass


class VersionRepository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_package_version(self, package_name):
        pass

    @abstractmethod
    def update(self, package_name, new_version):
        pass


class PackageRepository(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self, package_name):
        pass

    @abstractmethod
    def update(self, package):
        pass
