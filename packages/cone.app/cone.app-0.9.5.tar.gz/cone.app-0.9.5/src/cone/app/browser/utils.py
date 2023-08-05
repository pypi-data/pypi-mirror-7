import re
import datetime
import types
from pyramid.security import authenticated_userid
from ..utils import app_config


def authenticated(request):
    """XXX: remove this. use ``authenticated_userid`` directly.
    """
    return authenticated_userid(request)


def nodepath(node):
    return [p for p in node.path if p is not None]


def make_query(**kw):
    query = list()
    for name, param in kw.items():
        if param is None:
            continue
        if isinstance(param, basestring):
            param = [param]
        if type(param) is types.IntType:
            param = [str(param)]
        for p in param:
            query.append('%s=%s' % (name, p))
    return '?%s' % '&'.join(query)


def make_url(request, path=None, node=None, resource=None, query=None):
    # if path=[] in signature, path gets aggregated in recursive calls ???
    # happens on icon lookup in navtree.
    # ^^^ that is because the [] (a list, mutable) is generated at compile
    # time. mutable values should not be in function signatures to avoid this.
    if path is None:
        path = []
    if node is not None:
        path = nodepath(node)
    if resource is not None:
        path.append(resource)
    url = '%s/%s' % (request.application_url, '/'.join(path))
    if not query:
        return url
    return '%s%s' % (url, query)


def choose_name(container, name):
    name = re.sub(
        r'-{2,}', '-',
        re.sub('^\w-|-\w-|-\w$', '-',
               re.sub(r'\W', '-', name.strip()))).strip('-').lower()
    n = name
    i = 0
    while n in container:
        i += 1
        n = u'%s-%s' % (name, i)
    return n.replace('/', '-').lstrip('+@')


def format_date(dt, long=True):
    if not isinstance(dt, datetime.datetime):
        return 'unknown'
    return long and dt.strftime('%d.%m.%Y %H:%M') or dt.strftime('%d.%m.%Y')


def node_icon_url(request, node):
    if node.properties.icon:
        return make_url(request, resource=node.properties.icon)
    info = node.nodeinfo
    if not info.icon:
        return make_url(request, resource=app_config().default_node_icon)
    return make_url(request, resource=info.icon)


def request_property(func):
    """Decorator like ``property``, but underlying function is only called once
    per request.

    Cache attribute on request.environ under key
    ``instanceid.classname.funcname``.

    Works only on instances providing a request attribute.
    """
    def wrapper(self):
        cache_key = '%s.%s.%s' \
            % (str(id(self)), self.__class__.__name__, func.__name__)
        try:
            return self.request.environ[cache_key]
        except KeyError:
            val = self.request.environ[cache_key] = func(self)
            return val
    wrapper.__doc__ = func.__doc__
    return property(wrapper)


class AppUtil(object):
    """Instance of this object gets Passed to main template when rendering.
    """

    def authenticated(self, request):
        return authenticated(request)

    def nodepath(self, node):
        return nodepath(node)

    def make_url(self, request, path=None, node=None, resource=None,
        query=None):
        if path is None:
            path = []
        return make_url(request, path, node, resource, query)

    def make_query(self, **kw):
        return make_query(**kw)

    def format_date(self, dt, long=True):
        return format_date(dt, long)
