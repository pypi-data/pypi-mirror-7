from .reporting.null_reporter import NullReporter

__all__ = ["context", "session", "test", "test_id", "g", "internal_globals"]


class GlobalStorage(object):
    pass


class Context(object):
    session = test = test_id = None

    def __init__(self):
        super(Context, self).__init__()
        self.g = GlobalStorage()
        self.internal_globals = GlobalStorage()

    @property
    def test_filename(self):
        return self._get_fqn_field("abspath")

    @property
    def test_classname(self):
        return self._get_fqn_module_address_field("factory_name")

    @property
    def test_methodname(self):
        return self._get_fqn_module_address_field("method_name")

    @property
    def reporter(self):
        if self.session is None:
            return NullReporter()
        return self.session.reporter

    def _get_fqn_module_address_field(self, field_name):
        current_test = self.test
        if current_test is None:
            return None
        return getattr(current_test.__slash__.fqn.address_in_module, field_name)

    def _get_fqn_field(self, field_name):
        return getattr(getattr(self.test.__slash__, "fqn", None), field_name, None)


class NullContext(object):

    def __setattr__(self, attr, value):
        raise AttributeError(
            "Cannot set attribute {0!r} on null context".format(attr))

    @property
    def _always_none(self):
        pass

    session = test = test_id = g = internal_globals = \
        test_filename = test_classname = test_methodname = _always_none

    reporter = NullReporter()


class _ContextStack(object):

    def __init__(self):
        super(_ContextStack, self).__init__()
        self._stack = [NullContext()]

    def __getattr__(self, attr):
        if not self._stack:
            raise AttributeError(attr)
        return getattr(self._stack[-1], attr)

    def __setattr__(self, attr, value):
        if attr.startswith("_"):
            return super(_ContextStack, self).__setattr__(attr, value)
        setattr(self._stack[-1], attr, value)

    def push(self, ctx):
        self._stack.append(ctx)
        return ctx

    def pop(self):
        assert len(self._stack) != 0
        if len(self._stack) == 1:
            raise RuntimeError("No more contexts to pop")
        return self._stack.pop(-1)

context = _ContextStack()


class ContextAttributeProxy(object):

    def __init__(self, name):
        super(ContextAttributeProxy, self).__init__()
        self._proxy__name = name

    @property
    def _obj(self):
        return getattr(context, self._proxy__name)

    def __getattr__(self, attr):
        return getattr(self._obj, attr)

    def __setattr__(self, attr, value):
        if attr == "_proxy__name":
            return super(ContextAttributeProxy, self).__setattr__(attr, value)
        setattr(self._obj, attr, value)

    def __eq__(self, other):
        return self._obj == other

    def __ne__(self, other):
        return self._obj != other

    def __call__(self, *args, **kwargs):
        return self._obj(*args, **kwargs)

    def __repr__(self):
        return repr(self._obj)

    def __str__(self):
        return str(self._obj)


session = ContextAttributeProxy("session")
test = ContextAttributeProxy("test")
test_id = ContextAttributeProxy("test_id")
g = ContextAttributeProxy("g")
internal_globals = ContextAttributeProxy("internal_globals")
reporter = ContextAttributeProxy("reporter")


def push_context():
    context.push(Context())

def pop_context():
    context.pop()
