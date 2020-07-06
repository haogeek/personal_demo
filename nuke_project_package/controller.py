"""Module includes the controller class of this tool."""

# Import built-in modules
import os
from functools import partial

# Import local modules
from threads import CollectThread, SingleCopyThread, SequenceCopyThread, \
    FinishThread


class NukePackageController(object):
    """Controller class of this tool.

    This class adds behaviors to the UI, arranges and manages all threads and
    timers during the packaging process.

    """

    def __init__(self, view):
        """Initialize the controller instance and connect to view instance.

        Args:
            view (QtWidgets.QWidget): View instance of this tool.
        """
        self.view = view
        self.finish_log = []
        self.copy_count = 0
        self.total_copy_amount = 0
        self.package_wrapper = None
        self.connect_slots()

    def connect_slots(self):
        """Connect GUI signals to slots."""
        self.view.folder_button.clicked.connect(self.select_destination)
        self.view.run_button.clicked.connect(self.run_packaging)
        self.view.close_timer.timeout.connect(self.check_thread_pool)

    def select_destination(self):
        """Fill destination folder path in the UI.

        Open an explorer dialog to select a folder and update the folder path
        widget.
        """
        dest_folder = self.view.folder_explorer.getExistingDirectory()
        # PySide
        if isinstance(dest_folder, list) and os.path.isdir(dest_folder[0]):
            self.view.folder_line.setText(dest_folder[0])
        # PySide2
        if os.path.isdir(dest_folder):
            self.view.folder_line.setText(dest_folder)

    def check_thread_pool(self):
        """Check if there's any worker thread remains in thread pool.

        This function will be triggered by the close_timer, if there's no worker
        thread remains, it will set the close_flag to True, otherwise it will
        restart the close_timer.
        """
        if len(self.view.thread_pool) <= 1:
            self.view.close_flag = True
            self.view.close_timer.stop()
            self.save_copying_log()
            self.view.refresh_ui()
            self.view.close()
        else:
            self.view.close_timer.start(1000)

    def run_packaging(self):
        """Start packaging process by creating and running collect thread."""
        if self.check_dest_root():
            self.view.show_message('Collecting source files...')
            collect_thread = CollectThread(self.view.folder_line.text())
            collect_thread.finish.connect(
                partial(self.collect_finish, collect_thread))
            self.view.thread_pool.append(collect_thread)
            collect_thread.start()

    def check_dest_root(self):
        """Check if the folder line edit in UI holds a valid folder path.

        Will try to create the folder path if it not exists.

        Return:
            bool: True if get a valid folder path, False otherwise.
        """
        dest_root = self.view.folder_line.text()
        if not os.path.isdir(dest_root):
            try:
                os.makedirs(dest_root)
            except (WindowsError, TypeError):
                self.view.message.setText('Please input a valid folder path.')
                return False
        return True

    def collect_finish(self, thread):
        """Get sources collection result and prepare the copying process.

        Save nuke script to destination folder and modify file knobs to
        use relative paths, remove collection thread from thread pool, start
        copying process.

        Args:
            thread (QtCore.QThread): Collector thread instance.
        """
        index = thread.index
        self.package_wrapper = thread.package_wrapper
        self.total_copy_amount = self.package_wrapper.copy_files_count
        self.thread_finish(thread)
        if index == len(self.package_wrapper.nodes):
            self.package_wrapper.modify_nodes_path()
            self.copy_process()

    def thread_finish(self, thread):
        """Remove worker thread from thread pool when it finish running.

        Args:
            thread (QtCore.QThread): Worker thread instance.
        """
        if thread in self.view.thread_pool:
            self.finish_log.extend(thread.log)
            self.view.thread_pool.remove(thread)

    def copy_process(self):
        """Create, store and run worker threads."""
        self.view.show_message('Starting packaging, please wait.')

        single_copy_thread = SingleCopyThread(
            self.package_wrapper.single_results,
            self.package_wrapper.dest_root)
        single_copy_thread.finish.connect(
            partial(self.thread_finish, single_copy_thread))
        single_copy_thread.copy_one_file.connect(self.show_copy_status)
        self.view.thread_pool.append(single_copy_thread)

        for basename in self.package_wrapper.sequence_results:
            sequence_copy_thread = SequenceCopyThread(
                basename,
                self.package_wrapper.sequence_results[basename],
                self.package_wrapper.dest_root)
            sequence_copy_thread.finish.connect(
                partial(self.thread_finish, sequence_copy_thread))
            sequence_copy_thread.copy_one_file.connect(self.show_copy_status)
            self.view.thread_pool.append(sequence_copy_thread)

        finish_thread = FinishThread(self.view)
        finish_thread.finish.connect(self.finish_copy)
        self.view.thread_pool.append(finish_thread)

        for thread in self.view.thread_pool:
            thread.start()

    def show_copy_status(self, source):
        """Show the file been copying and update percentage of the process bar.

        Args:
            source (str): Absolute path of the source file been copying.

        """
        self.view.show_message('Copy {}...'.format(os.path.basename(source)))
        self.copy_count += 1
        process = int(
            (float(self.copy_count) / float(self.total_copy_amount)) * 100)
        self.view.progress_bar.setValue(process)

    def finish_copy(self):
        """Save the copying log and show finishing message."""
        self.save_copying_log()
        self.view.show_message('Finish packaging all sources.')

    def save_copying_log(self):
        """Save copying log to destination root folder."""
        if self.package_wrapper and self.finish_log:
            with open(
                    '{}/copy_log.log'.format(self.package_wrapper.dest_root),
                    'w') as log_file:
                self.finish_log[0] = self.finish_log[0].replace('\n\n', '')
                log_file.writelines(self.finish_log)
