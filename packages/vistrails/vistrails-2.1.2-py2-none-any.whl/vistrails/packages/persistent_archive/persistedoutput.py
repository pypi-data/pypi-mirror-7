from datetime import datetime
import os

from vistrails.core.modules.basic_modules import Directory, File, Path
from vistrails.core.modules.config import IPort, OPort, ModuleSettings
from vistrails.core.modules.vistrails_module import Module, ModuleError

from .common import KEY_TYPE, TYPE_OUTPUT, \
    KEY_SIGNATURE, KEY_TIME, KEY_WORKFLOW, KEY_MODULE_ID, \
    get_default_store, wrap_path
from .queries import Metadata


class PersistedPath(Module):
    """Records a file in the file store.
    """

    _input_ports = [
            IPort('path', Path),
            IPort('metadata', Metadata, optional=True)]
    _output_ports = [
            OPort('path', Path)]

    _cached = None

    def updateUpstream(self):
        """A modified version of the updateUpstream method.

        Only updates upstream if the file is not found in the store.
        """
        if not hasattr(self, 'signature'):
            raise ModuleError(self, "Module has no signature")
        file_store = get_default_store()
        entries = file_store.query({KEY_SIGNATURE: self.signature})
        best = None
        for entry in entries:
            if best is None or entry[KEY_TIME] > best[KEY_TIME]:
                best = entry
        if best is not None:
            self._cached = best.filename
        else:
            super(PersistedPath, self).updateUpstream()

    def compute(self):
        if self._cached is not None:
            self._set_result(self._cached)
        else:
            file_store = get_default_store()
            newpath = self.get_input('path').name
            self.check_path_type(newpath)
            metadata = self.get_input_list('metadata')
            metadata = dict(m.metadata for m in metadata)
            metadata[KEY_TYPE] = TYPE_OUTPUT
            metadata[KEY_TIME] = datetime.strftime(datetime.utcnow(),
                                                   '%Y-%m-%d %H:%M:%S')
            metadata[KEY_SIGNATURE] = self.signature
            locator = self.moduleInfo.get('locator')
            if locator is not None:
                metadata[KEY_WORKFLOW] = "%s:%s" % (
                        locator.name,
                        self.moduleInfo['version'])
            metadata[KEY_MODULE_ID] = self.moduleInfo['moduleId']
            entry = file_store.add(newpath, metadata)
            self.annotate({'added_file': entry['hash']})
            self._set_result(entry.filename)

    def check_path_type(self, path):
        pass

    def _set_result(self, path):
        self.set_output('path', wrap_path(path))


class PersistedFile(PersistedPath):
    _input_ports = [
            IPort('path', File),
            IPort('metadata', Metadata, optional=True)]
    _output_ports = [
            OPort('path', File)]
    _settings = ModuleSettings(configure_widget=
            'vistrails.packages.persistent_archive.widgets:SetMetadataWidget')

    def check_path_type(self, path):
        if not os.path.isfile(path):
            raise ModuleError(self, "Path is not a file")


class PersistedDir(PersistedPath):
    _input_ports = [
            IPort('path', Directory),
            IPort('metadata', Metadata, optional=True)]
    _output_ports = [
            OPort('path', Directory)]
    _settings = ModuleSettings(configure_widget=
            'vistrails.packages.persistent_archive.widgets:SetMetadataWidget')

    def check_path_type(self, path):
        if not os.path.isdir(path):
            raise ModuleError(self, "Path is not a directory")
