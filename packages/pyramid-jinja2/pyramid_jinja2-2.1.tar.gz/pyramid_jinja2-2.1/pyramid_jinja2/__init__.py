import inspect
import os
import posixpath
import sys
import threading

from jinja2 import Environment as _Jinja2Environment

from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import FileSystemLoader
from jinja2.utils import open_if_exists

from pyramid.asset import abspath_from_asset_spec
from pyramid.path import DottedNameResolver

from zope.deprecation import deprecated
from zope.interface import Interface

from .compat import text_type
from .settings import (
    parse_env_options_from_settings,
    parse_loader_options_from_settings,
    parse_multiline,
)


ENV_CONFIG_PHASE = 0
EXTRAS_CONFIG_PHASE = 1


class IJinja2Environment(Interface):
    pass


class Environment(_Jinja2Environment):
    def join_path(self, uri, parent):
        if os.path.isabs(uri) or ':' in uri:
            # we have an asset spec or absolute path
            return uri

        # make template lookup parent-relative
        if not os.path.isabs(parent) and ':' in parent:
            # parent is an asset spec
            ppkg, ppath = parent.split(':', 1)
            reluri = posixpath.join(posixpath.dirname(ppath), uri)
            return '{0}:{1}'.format(ppkg, reluri)

        # parent is just a normal path
        return posixpath.join(posixpath.dirname(parent), uri)


class FileInfo(object):
    open_if_exists = staticmethod(open_if_exists)
    getmtime = staticmethod(os.path.getmtime)

    def __init__(self, filename, encoding='utf-8'):
        self.filename = filename
        self.encoding = encoding

    def _delay_init(self):
        if '_mtime' in self.__dict__:
            return

        f = self.open_if_exists(self.filename)
        if f is None:
            raise TemplateNotFound(self.filename)
        self._mtime = self.getmtime(self.filename)

        data = ''
        try:
            data = f.read()
        finally:
            f.close()

        if not isinstance(data, text_type):
            data = data.decode(self.encoding)
        self._contents = data

    @property
    def contents(self):
        self._delay_init()
        return self._contents

    @property
    def mtime(self):
        self._delay_init()
        return self._mtime

    def uptodate(self):
        try:
            return os.path.getmtime(self.filename) == self.mtime
        except OSError:
            return False


class _PackageFinder(object):
    inspect = staticmethod(inspect)

    def caller_package(self, excludes=()):
        """A list of excluded patterns, optionally containing a `.` suffix.
        For example, ``'pyramid.'`` would exclude exclude ``'pyramid.config'``
        but not ``'pyramid'``.
        """
        f = None
        for t in self.inspect.stack():
            f = t[0]
            name = f.f_globals.get('__name__')
            if name:
                excluded = False
                for pattern in excludes:
                    if pattern[-1] == '.' and name.startswith(pattern):
                        excluded = True
                        break
                    elif name == pattern:
                        excluded = True
                        break
                if not excluded:
                    break

        if f is None:
            return None

        pname = f.f_globals.get('__name__') or '__main__'
        m = sys.modules[pname]
        f = getattr(m, '__file__', '')
        if (('__init__.py' in f) or ('__init__$py' in f)):  # empty at >>>
            return m

        pname = m.__name__.rsplit('.', 1)[0]

        return sys.modules[pname]


_caller_package = _PackageFinder().caller_package


class SmartAssetSpecLoader(FileSystemLoader):
    '''A Jinja2 template loader that knows how to handle
    asset specifications.
    '''

    def __init__(self, searchpath=(), encoding='utf-8', debug=False):
        FileSystemLoader.__init__(self, searchpath, encoding)
        self.debug = debug

    def list_templates(self):
        raise TypeError('this loader cannot iterate over all templates')

    def get_source(self, environment, template):
        # keep legacy asset: prefix checking that bypasses
        # source path checking altogether
        if template.startswith('asset:'):
            template = template[6:]

        # load template directly from the filesystem
        filename = abspath_from_asset_spec(template)
        fi = FileInfo(filename, self.encoding)
        if os.path.isfile(fi.filename):
            return fi.contents, fi.filename, fi.uptodate

        # fallback to search-path lookup
        try:
            return FileSystemLoader.get_source(self, environment, template)
        except TemplateNotFound as ex:
            message = ex.message
            message += ('; asset=%s; searchpath=%r'
                        % (template, self.searchpath))
            raise TemplateNotFound(name=ex.name, message=message)


class Jinja2TemplateRenderer(object):
    '''Renderer for a jinja2 template'''
    def __init__(self, template_loader):
        self.template_loader = template_loader

    def __call__(self, value, system):
        try:
            system.update(value)
        except (TypeError, ValueError) as ex:
            raise ValueError('renderer was passed non-dictionary '
                             'as value: %s' % str(ex))
        template = self.template_loader()
        return template.render(system)


class Jinja2RendererFactory(object):
    environment = None

    def __call__(self, info):
        name, package = info.name, info.package

        def template_loader():
            # first try a caller-relative template if possible
            try:
                if ':' not in name and package is not None:
                    name_with_package = '%s:%s' % (package.__name__, name)
                    return self.environment.get_template(name_with_package)
            except TemplateNotFound:
                pass

            # fallback to search path
            return self.environment.get_template(name)

        return Jinja2TemplateRenderer(template_loader)


_factory_lock = threading.Lock()


def renderer_factory(info):
    _factory_lock.acquire()
    try:
        registry = info.registry
        env = registry.queryUtility(IJinja2Environment)
        if env is None:
            resolver = DottedNameResolver(package=info.package)
            loader_opts = parse_loader_options_from_settings(
                registry.settings,
                'jinja2.',
                resolver.maybe_resolve,
                info.package,
            )
            env_opts = parse_env_options_from_settings(
                registry.settings,
                'jinja2.',
                resolver.maybe_resolve,
                info.package
            )
            env = create_environment_from_options(env_opts, loader_opts)
            registry.registerUtility(env, IJinja2Environment)
    finally:
        _factory_lock.release()

    factory = Jinja2RendererFactory()
    factory.environment = env
    return factory(info)


deprecated(
    'renderer_factory',
    'The pyramid_jinja2.renderer_factory was deprecated in version 2.0 and '
    'will be removed in the future. You should upgrade to the newer '
    'config.add_jinja2_renderer() API.')


def add_jinja2_search_path(config, searchpath, name='.jinja2'):
    """
    This function is added as a method of a :term:`Configurator`, and
    should not be called directly.  Instead it should be called like so after
    ``pyramid_jinja2`` has been passed to ``config.include``:

    .. code-block:: python

       config.add_jinja2_search_path('anotherpackage:templates/')

    It will add the directory or :term:`asset specification` passed as
    ``searchpath`` to the current search path of the
    :class:`jinja2.Environment` used by the renderer identified by ``name``.

    """
    def register():
        env = get_jinja2_environment(config, name)
        searchpaths = parse_multiline(searchpath)
        for folder in searchpaths:
            env.loader.searchpath.append(
                abspath_from_asset_spec(folder, config.package))
    config.action(None, register, order=EXTRAS_CONFIG_PHASE)


def add_jinja2_extension(config, ext, name='.jinja2'):
    """
    This function is added as a method of a :term:`Configurator`, and
    should not be called directly.  Instead it should be called like so after
    ``pyramid_jinja2`` has been passed to ``config.include``:

    .. code-block:: python

       config.add_jinja2_extension(myext)

    It will add the Jinja2 extension passed as ``ext`` to the current
    :class:`jinja2.Environment` used by the renderer named ``name``.

    """
    ext = config.maybe_dotted(ext)
    def register():
        env = get_jinja2_environment(config, name)
        env.add_extension(ext)
    config.action(None, register, order=EXTRAS_CONFIG_PHASE)


def get_jinja2_environment(config, name='.jinja2'):
    """
    This function is added as a method of a :term:`Configurator`, and
    should not be called directly.  Instead it should be called like so after
    ``pyramid_jinja2`` has been passed to ``config.include``:

    .. code-block:: python

       config.get_jinja2_environment()

    It will return the configured ``jinja2.Environment`` for the
    renderer named ``name``. Configuration is delayed until a call to
    ``config.commit()`` or ``config.make_wsgi_app()``. As such, if this
    method is called prior to committing the changes, it may return ``None``.

    """
    registry = config.registry
    return registry.queryUtility(IJinja2Environment, name=name)


def create_environment_from_options(env_opts, loader_opts):
    loader = SmartAssetSpecLoader(**loader_opts)

    newstyle = env_opts.pop('newstyle', False)
    gettext = env_opts.pop('gettext', None)
    filters = env_opts.pop('filters', {})
    tests = env_opts.pop('tests', {})
    globals = env_opts.pop('globals', {})

    env = Environment(
        loader=loader,
        **env_opts
    )

    env.install_gettext_callables(
        gettext.gettext, gettext.ngettext, newstyle=newstyle)

    env.filters.update(filters)
    env.tests.update(tests)
    env.globals.update(globals)

    return env


def add_jinja2_renderer(config, name, settings_prefix='jinja2.', package=None):
    """
    This function is added as a method of a :term:`Configurator`, and
    should not be called directly.  Instead it should be called like so after
    ``pyramid_jinja2`` has been passed to ``config.include``:

    .. code-block:: python

       config.add_jinja2_renderer('.html', settings_prefix='jinja2.')

    It will register a new renderer, loaded from settings at the specified
    ``settings_prefix`` prefix. This renderer will be active for files using
    the specified extension ``name``.

    """
    renderer_factory = Jinja2RendererFactory()
    config.add_renderer(name, renderer_factory)

    package = package or config.package
    resolver = DottedNameResolver(package=package)

    def register():
        registry = config.registry
        settings = config.get_settings()

        loader_opts = parse_loader_options_from_settings(
            settings,
            settings_prefix,
            resolver.maybe_resolve,
            package,
        )
        env_opts = parse_env_options_from_settings(
            settings,
            settings_prefix,
            resolver.maybe_resolve,
            package,
        )
        env = create_environment_from_options(env_opts, loader_opts)
        renderer_factory.environment = env

        registry.registerUtility(env, IJinja2Environment, name=name)

    config.action(
        ('jinja2-renderer', name), register, order=ENV_CONFIG_PHASE)


def includeme(config):
    """Set up standard configurator registrations.  Use via:

    .. code-block:: python

       config = Configurator()
       config.include('pyramid_jinja2')

    Once this function has been invoked, the ``.jinja2`` renderer is
    available for use in Pyramid and these new directives are available as
    methods of the configurator:

    - ``add_jinja2_renderer``: Add a new Jinja2 renderer, with a different
      file extension and/or settings.

    - ``add_jinja2_search_path``: Add a new location to the search path
      for the specified renderer.

    - ``add_jinja2_extension``: Add a list of extensions to the Jinja2
      environment used by the specified renderer.

    - ``get_jinja2_environment``: Return the :class:`jinja2.Environment`
      used by the specified renderer.

    """
    config.add_directive('add_jinja2_renderer', add_jinja2_renderer)
    config.add_directive('add_jinja2_search_path', add_jinja2_search_path)
    config.add_directive('add_jinja2_extension', add_jinja2_extension)
    config.add_directive('get_jinja2_environment', get_jinja2_environment)

    package = _caller_package(('pyramid', 'pyramid.', 'pyramid_jinja2'))
    config.add_jinja2_renderer('.jinja2', package=package)

    # always insert default search path relative to package
    default_search_path = '%s:' % (package.__name__,)
    config.add_jinja2_search_path(default_search_path, name='.jinja2')
