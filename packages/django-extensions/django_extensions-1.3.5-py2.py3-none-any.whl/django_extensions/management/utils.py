from django.conf import settings
import os
import sys
import logging

try:
    from importlib import import_module
except ImportError:
    try:
        from django.utils.importlib import import_module
    except ImportError:
        def import_module(module):
            return __import__(module, {}, {}, [''])


def get_project_root():
    """ get the project root directory """
    django_settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
    if not django_settings_module:
        module_str = settings.SETTINGS_MODULE
    else:
        module_str = django_settings_module.split(".")[0]
    mod = import_module(module_str)
    return os.path.dirname(os.path.abspath(mod.__file__))


def _make_writeable(filename):
    """
    Make sure that the file is writeable. Useful if our source is
    read-only.

    """
    import stat
    if sys.platform.startswith('java'):
        # On Jython there is no os.access()
        return
    if not os.access(filename, os.W_OK):
        st = os.stat(filename)
        new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
        os.chmod(filename, new_permissions)


def setup_logger(logger, stream, filename=None, fmt=None):
    """Sets up a logger (if no handlers exist) for console output,
    and file 'tee' output if desired."""
    if len(logger.handlers) < 1:
        console = logging.StreamHandler(stream)
        console.setLevel(logging.DEBUG)
        console.setFormatter(logging.Formatter(fmt))
        logger.addHandler(console)
        logger.setLevel(logging.DEBUG)

        if filename:
            outfile = logging.FileHandler(filename)
            outfile.setLevel(logging.INFO)
            outfile.setFormatter(logging.Formatter("%(asctime)s " + (fmt if fmt else '%(message)s')))
            logger.addHandler(outfile)


class RedirectHandler(logging.Handler):
    """Redirect logging sent to one logger (name) to another."""
    def __init__(self, name, level=logging.DEBUG):
        # Contemplate feasibility of copying a destination (allow original handler) and redirecting.
        logging.Handler.__init__(self, level)
        self.name = name
        self.logger = logging.getLogger(name)

    def emit(self, record):
        self.logger.handle(record)
