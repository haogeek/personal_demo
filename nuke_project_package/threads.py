"""Module includes custom thread classes for this tool."""

# Import built-in modules
import os
import shutil

# Import third-party modules
try:
    from PySide import QtCore
except ImportError:
    from PySide2 import QtCore

# Import local modules
from model import NukePackageWrapper
import utils


class CollectThread(QtCore.QThread):
    """Worker thread to collect sources' information from node tree."""

    # Qt signal emitted when finish or stop this copy process.
    finish = QtCore.Signal()

    def __init__(self, dest_root):
        """Initialize collector thread.

        Args:
            dest_root (str): Destination root folder path.
        """
        super(CollectThread, self).__init__()
        self.package_wrapper = None
        self.dest_root = dest_root
        self.run_flag = True
        self.index = 0
        self.log = []

    def run(self):
        """Collect all source information from current nuke scene."""
        self.package_wrapper = NukePackageWrapper(self.dest_root)

        while self.run_flag and self.index < len(self.package_wrapper.nodes):
            self.package_wrapper.grab_source(self.index)
            self.index += 1

        if self.package_wrapper.error_nodes:
            self.log.append('\n\nNodes with error:')

        for node in self.package_wrapper.error_nodes:
            self.log.append('\n{}'.format(node.name()))

        self.finish.emit()


class SingleCopyThread(QtCore.QThread):
    """Worker thread to copy a list of single file."""

    # Qt signal emitted when finish or stop this copy process.
    finish = QtCore.Signal()
    # Qt signal emitted when one file been copied.
    copy_one_file = QtCore.Signal(str)

    def __init__(self, source_list, dest_folder):
        """Initialize single file copy worker thread.

        Args:
            source_list (list): List of single file.
            dest_folder (str): Destination root folder path.
        """
        super(SingleCopyThread, self).__init__()
        self.source_list = source_list
        self.dest_folder = '{}/sources'.format(dest_folder)
        self.run_flag = True
        self._mutex = QtCore.QMutex()
        self.log = []

    def run(self):
        """Copy every single file into destination folder."""
        source_count = len(self.source_list)
        copy_count = 0
        source_iter = iter(self.source_list)

        while self.run_flag and copy_count < source_count:
            node_name, source = source_iter.next()
            shutil.copy2(source, self.dest_folder)
            self._mutex.lock()
            self.copy_one_file.emit(source)
            self.log.append('\n\n{}\n{}'.format(node_name, source))
            self._mutex.unlock()
            copy_count += 1

        self.finish.emit()


class SequenceCopyThread(QtCore.QThread):
    """Worker thread to copy an image sequence."""

    # Qt signal emitted when finish or stop this copy process.
    finish = QtCore.Signal()
    # Qt signal emitted when one file been copied.
    copy_one_file = QtCore.Signal(str)

    def __init__(self, basename, sequence_info, dest_folder):
        """Initialize sequence copy worker thread.

        Args:
            basename (str): Image basename without frame count and format.
            sequence_info (tuple):
                (
                    image_sequence_folder_path,
                    first_frame_number,
                    last_frame_number,
                    file_format
                )
            dest_folder (str): Destination root folder path.
        """
        super(SequenceCopyThread, self).__init__()
        self.node_name = sequence_info[0]
        self.source_files = sequence_info[1]
        self.first = sequence_info[2]
        self.last = sequence_info[3]
        self.basename = basename
        self.dest_folder = '{}/sources/{}'.format(dest_folder, basename)
        self.run_flag = True
        self._mutex = QtCore.QMutex()
        self.log = []
        self.index = 0

    def run(self):
        """Copy every frame into destination folder."""
        sequence_length = len(self.source_files)
        if sequence_length < self.last - self.first + 1:
            self.log.append('\n\n{} (missing frame)'.format(self.node_name))
        else:
            self.log.append('\n\n{}'.format(self.node_name))
        if not os.path.isdir(self.dest_folder):
            os.makedirs(self.dest_folder)

        while self.run_flag and self.index < sequence_length:
            source = self.source_files[self.index]
            shutil.copy2(source, self.dest_folder)
            self._mutex.lock()
            self.copy_one_file.emit(source)
            self._mutex.unlock()
            self.index += 1

        if self.index == sequence_length - 1:
            self.log.append('\n{} {}-{}'.format(
                utils.frame_to_pattern(self.source_files[0]),
                self.first,
                self.last))
        elif self.index > 0:
            self.log.append('\n{} {}-{}'.format(
                utils.frame_to_pattern(self.source_files[0]),
                self.first,
                self.first + self.index))

        self.finish.emit()


class FinishThread(QtCore.QThread):
    """Monitor thread to check whether all copy processes are complete."""

    # Qt signal emitted when finish or stop this copy process.
    finish = QtCore.Signal()

    def __init__(self, view):
        """Initialize monitor thread.

        Args:
            view (QtGui.QWidget): Tool's main UI instance.
        """
        super(FinishThread, self).__init__()
        self.run_flag = True
        self.view = view

    def run(self):
        """Check whether all copy processes are complete."""
        while self.run_flag and len(self.view.thread_pool) > 1:
            continue

        self.finish.emit()
