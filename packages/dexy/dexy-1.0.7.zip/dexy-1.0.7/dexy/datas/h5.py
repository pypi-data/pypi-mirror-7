from dexy.data import Generic
from dexy.storage import GenericStorage
try:
    import tables
    AVAILABLE = True
except ImportError:
    AVAILABLE = False

class H5(Generic):
    """
    Data type for reading HDF5 files using pytables.
    """
    aliases = ['h5']
    _settings = {
            'storage-type' : 'h5storage'
            }

    def is_active(self):
        return AVAILABLE

    def root(self):
        return self.data().root

    def walk_groups(self, path=None):
        if path:
            return self.data().walk_groups(path)
        else:
            return self.data().walk_groups()

    def walk_nodes(self, path=None, node_type=None):
        if path and node_type:
            return self.data().walk_nodes(path, node_type)
        elif path:
            return self.data().walk_nodes(path)
        else:
            return self.data().walk_nodes()

class H5Storage(GenericStorage):
    """
    Storage backend representing HDF5 files.
    """
    aliases = ['h5storage']

    def is_active(self):
        return AVAILABLE

    def read_data(self):
        return tables.open_file(self.data_file(read=True), "r")

if AVAILABLE:
    # Set custom exit hook so messages about closing files don't get printed to
    # stderr, per http://www.pytables.org/moin/UserDocuments/AtexitHooks
    def my_close_open_files(verbose):
        open_files = tables.file._open_files
        are_open_files = len(open_files) > 0
        if verbose and are_open_files:
            print >> sys.stderr, "Closing remaining open files:",
        for fileh in open_files.keys():
            if verbose:
                print >> sys.stderr, "%s..." % (open_files[fileh].filename,),
            open_files[fileh].close()
            if verbose:
                print >> sys.stderr, "done",
        if verbose and are_open_files:
            print >> sys.stderr
    import sys, atexit
    atexit.register(my_close_open_files, False)
