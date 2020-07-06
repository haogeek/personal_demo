"""Module to add this tool into Nuke menubar."""

# Import third-party modules
import nuke

# Import local modules
from view import PackageToolUI
from controller import NukePackageController


ui = PackageToolUI()
controller = NukePackageController(ui)
nuke.menu('Nodes').addCommand('Custom/Packaging', 'controller.view.show()')
