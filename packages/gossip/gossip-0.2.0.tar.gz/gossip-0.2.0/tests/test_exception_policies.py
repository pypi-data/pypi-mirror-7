import gossip
from gossip.exception_policy import Inherit
import pytest


@pytest.mark.parametrize("invalid_policy", [object(), 1, None, gossip.RaiseImmediately])
def test_cannot_set_invalid_policy(invalid_policy):
    with pytest.raises(ValueError):
        gossip.set_exception_policy(invalid_policy)

def test_global_cannot_be_inherit():
    with pytest.raises(RuntimeError):
        gossip.set_exception_policy(Inherit())

def test_default_global_group_policy():
    assert isinstance(gossip.get_global_group().get_exception_policy(), gossip.RaiseImmediately)

def test_inherit_policy(exception_handling_policy):
    group = gossip.group.Group("some_group", parent=gossip.get_global_group())
    gossip.set_exception_policy(exception_handling_policy)
    group.set_exception_policy(Inherit())
    assert group.get_exception_policy() is exception_handling_policy

def test_inherit_policy_changing_parent():
    gossip.define("group.hook")
    group = gossip.get_group_by_name("group")
    for policy in (gossip.RaiseImmediately(), gossip.RaiseDefer(), gossip.IgnoreExceptions()):
        gossip.set_exception_policy(policy)
        assert group.get_exception_policy() is policy

def test_group_returns_to_default_after_reset():
    gossip.get_global_group().set_exception_policy(gossip.IgnoreExceptions())
    gossip.get_global_group().reset()
    test_default_global_group_policy()

def test_get_exception_policy(exception_handling_policy):
    group = gossip.group.Group("some_group", parent=gossip.get_global_group())
    group.set_exception_policy(exception_handling_policy)
    assert group.get_exception_policy() is exception_handling_policy

def test_exception_handling(error_handling_hook, error_prone_handlers, exception_handling_policy):
    error_handling_hook.group.set_exception_policy(exception_handling_policy)
    if isinstance(exception_handling_policy, gossip.IgnoreExceptions):
        error_handling_hook()
    else:
        with pytest.raises(HandlerException) as error:
            error_handling_hook()

        assert error.value.args[0] is error_prone_handlers[0]
    assert error_prone_handlers[0].called
    for handler in error_prone_handlers[1:]:
        assert handler.called == (not isinstance(exception_handling_policy, gossip.RaiseImmediately))

@pytest.fixture(
    params=[gossip.RaiseDefer, gossip.RaiseImmediately, gossip.IgnoreExceptions])
def exception_handling_policy(request):
    return request.param()

@pytest.fixture
def error_handling_hook(hook_name):
    return gossip.define(hook_name)

@pytest.fixture
def error_prone_handlers(error_handling_hook):
    returned = []
    num_handlers = 10
    for handler_index in range(num_handlers):
        handler = ErrorProneHandler()
        if handler_index in (0, 5, num_handlers - 1):
            handler.fail_when_called()
        returned.append(handler)
        error_handling_hook.register(returned[-1].func)

    return returned

class ErrorProneHandler(object):

    def __init__(self):
        super(ErrorProneHandler, self).__init__()

        self.called = False
        self._fail = False

        def func():
            self.called = True
            if self._fail:
                raise HandlerException(self)

        self.func = func

    def fail_when_called(self):
        self._fail = True

class HandlerException(Exception):
    pass
