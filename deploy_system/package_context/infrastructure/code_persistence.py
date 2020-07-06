# coding=utf-8
"""Implementation of source code related operators."""

# Import built-in modules
from contextlib import contextmanager
from importlib import import_module
import os
import shutil
import subprocess
import sys

# Import framework utilities
from deploy_system.utils.ioc import dependency, register
from deploy_system.utils.path import handle_remove_readonly, hotfix

# Import local context domain objects
from deploy_system.package_context.domain.repository import CodeRepository

# Import local modules
from constants import EXTERNAL_REPO_PATTERN, INTERNAL_REPO_PATTERN, INTERNAL_DEPLOY_DIR, \
    SOURCE_DIR, STAGING_DIR, EXTERNAL_DEPLOY_DIR


def gitlab_puller(package_name, package_type):
    """Pull source code from Gitlab with given repo name.

    Args:
        package_name (str): Name of a Gitlab repo.
        package_type (str): Either 'internal' or 'external'.

    Returns:

    """
    if package_type == 'internal':
        url = INTERNAL_REPO_PATTERN.format(package_name)
    elif package_type == 'external':
        url = EXTERNAL_REPO_PATTERN.format(package_name)
    else:
        raise AssertionError("package_type should be either 'internal' or "
                             "'external'.")
    os.environ['PATH'] = r'C:\Program Files\Git\cmd'
    cmd = [
        'git',
        '-C',
        SOURCE_DIR,
        'clone',
        url
    ]
    subprocess.check_call(cmd, env=os.environ)


@contextmanager
def temp_env(path):
    """Context manager to temporarily specify sys.path.

    Args:
        path (str): Absolute path of a folder.

    """
    original_paths = sys.path
    original_modules = sys.modules.copy()
    sys.path = [path]
    yield
    sys.path = original_paths
    sys.modules = original_modules


class Builder(object):
    """Builder to be used in for package."""

    def __init__(self, source_dir, staging_dir, build_module):
        """Initialize the builder for specific package.

        Args:
            source_dir (str): Absolute path of package source folder.
            staging_dir (str): Absolute path of package staging folder.
            build_module (module object): Build module of the package.

        """
        self.config = {
            'source_dir': source_dir,
            'staging_dir': staging_dir
        }
        self.build_module = build_module

    def build(self):
        """Call the run() function from the build module.

        Returns:

        """
        self.build_module.run(self.config)


# Register this class as the implementation of code repository.
@register('code_repo')
class CodePersistence(CodeRepository):
    """Implementation of code repository."""

    @staticmethod
    def get_code(package_name, package_type):
        """Pull latest source code of specific package from Gitlab.

        Args:
            package_name (str): Name of a Gitlab repo.

        Returns:

        """
        if package_name in os.listdir(SOURCE_DIR):
            shutil.rmtree('{}/{}'.format(SOURCE_DIR, package_name),
                          onerror=handle_remove_readonly)
        gitlab_puller(package_name, package_type)

    @staticmethod
    @dependency('package_repo')
    def prepare_staging(package_name, package_repo=None):
        """Prepare staging area for a package.

        This function will check if the source code of the package exists, then
        it will clear staging area and config builder for the package, finally
        save the updated package into package repository.

        Args:
            package_name (str): Name of the package.
            package_repo (PackageRepository): Package repository implementation
                class.

        Raises:
            RuntimeError: If source code of the given package name not exists
                in source area.

        """
        source_dir = '{}/{}'.format(SOURCE_DIR, package_name)
        staging_dir = '{}/{}'.format(STAGING_DIR, package_name)
        if os.path.isdir(source_dir):
            if os.path.isdir(staging_dir):
                shutil.rmtree(staging_dir, onerror=handle_remove_readonly)
        else:
            raise RuntimeError(
                'You should get source code of {} first.'.format(package_name))
        package = package_repo.get(package_name)
        package.builder = Builder(source_dir, staging_dir, package.build_module)
        package_repo.update(package)

    @staticmethod
    def get_build_module(package_name):
        """Get the build module of given package in a temporary environment.

        Args:
            package_name (str): Name of a package inside source area.

        Returns (model object): The build module of the package.

        """
        with temp_env('{}/{}'.format(SOURCE_DIR, package_name)):
            build_module = import_module('build')
        return build_module

    @staticmethod
    def deploy(package_name, package_type, version_number):
        """Copy package contents into production area with given version number.

        Args:
            package_name (str): Name of a package inside staging area.
            version_number (str): New version number to be used for the path of
                deployment destination.
            package_type (str): Either 'internal' or 'external'.

        """
        if package_type == 'internal':
            dest_dir = '{}/{}/{}'.format(INTERNAL_DEPLOY_DIR,
                                         package_name,
                                         version_number)
        elif package_type == 'external':
            dest_dir = '{}/{}/{}'.format(EXTERNAL_DEPLOY_DIR,
                                         package_name,
                                         version_number)
        if os.path.isdir(dest_dir):
            hotfix('{}/{}'.format(STAGING_DIR, package_name), dest_dir)
        else:
            shutil.copytree('{}/{}'.format(STAGING_DIR, package_name), dest_dir)


    @staticmethod
    def clear(package_name):
        """Remove package from source and staging area.

        Args:
            package_name (str): Name of a package.

        """
        source_dir = '{}/{}'.format(SOURCE_DIR, package_name)
        staging_dir = '{}/{}'.format(STAGING_DIR, package_name)
        if os.path.isdir(source_dir):
            shutil.rmtree(source_dir, onerror=handle_remove_readonly)
        if os.path.isdir(staging_dir):
            shutil.rmtree(staging_dir, onerror=handle_remove_readonly)
