import os
from django.contrib.staticfiles.finders import AppDirectoriesFinder
from django.core.files.storage import FileSystemStorage
from django.utils.importlib import import_module
from django.utils._os import upath
from django.conf import settings


project_name = settings.SETTINGS_MODULE.split(".")[0]


class CustomStaticStorage(FileSystemStorage):
    """
    A file system storage backend that takes an app module and works
    for the ``static`` directory of it.
    """
    prefix = None
    source_dir = 'static'

    def __init__(self, app, *args, **kwargs):
        """
        Returns a static file storage if available in the given app.
        """
        # app is the actual app module

        mod = import_module(app)
        mod_path = os.path.dirname(upath(mod.__file__))
        location = os.path.join(
            mod_path, project_name
            )
        super(CustomStaticStorage, self).__init__(location, *args, **kwargs)


class CustomFinder(AppDirectoriesFinder):
    storage_class = CustomStaticStorage
