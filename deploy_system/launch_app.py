import imp
import os
import subprocess
import sys
from copy import deepcopy

production_dir = 'P:/pipeline/internal'
thirdparty_dir = 'P:/pipeline/external'


class SysPath(object):
    def __init__(self, path):
        self.path = path
        self.original_sys_path = []

    def __enter__(self):
        self.original_sys_path = sys.path[:]
        sys.path = [self.path]

    def __exit__(self, exc_type, exc_value, traceback):
        sys.path = self.original_sys_path


class SysModules(object):
    def __enter__(self):
        self.original_sys_modules = sys.modules.copy()

    def __exit__(self, exc_type, exc_value, traceback):
        sys.modules = self.original_sys_modules


def resolve(package_name, package_path):
    with SysPath(package_path), SysModules():
        requirements = []
        command = None
        package = imp.load_module(package_name, *imp.find_module('package'))
        if package:
            if hasattr(package, 'requirements'):
                requirements = getattr(package, 'requirements')
            if hasattr(package, 'command'):
                command = getattr(package, 'command')
            if command:
                command()
    return requirements


def add_package(package_name):
    package_dir = None
    for root in [production_dir, thirdparty_dir]:
        if package_name in os.listdir(root):
            package_dir = os.path.join(root, package_name)
    if not package_dir:
        raise ValueError('Package {} doesn\'t exist in internal or external area.'.format(package_name))
    latest = sorted(os.listdir(package_dir))[-1]

    require_packages = resolve(package_name, os.path.join(package_dir, latest))
    for package in require_packages:
        add_package(package)


class Run(object):

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        pass


if __name__ == '__main__':
    argv = sys.argv[1:]
    if 'run' in argv:
        packages = argv[:argv.index('run')]
        command = argv[argv.index('run')+1:]
    else:
        packages = argv
        command = ['{}.bat'.format(argv[0])]
    for package in packages:
        add_package(package)

    with Run():
        cxt = deepcopy(os.environ)
        subprocess.call(command, env=cxt, shell=True, close_fds=True)
