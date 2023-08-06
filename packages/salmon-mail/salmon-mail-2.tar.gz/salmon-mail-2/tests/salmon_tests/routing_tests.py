from salmon.routing import *
from salmon.mail import MailRequest
from salmon import queue, routing, encoding
from setup_env import setup_salmon_dirs, teardown_salmon_dirs

from nose.tools import *
from mock import *


def setup():
    Router.clear_states()
    Router.clear_routes()

def teardown():
    setup()

def test_MemoryStorage():
    store = MemoryStorage()
    store.set(test_MemoryStorage.__module__, "tester@localhost", "TESTED")

    assert store.get(test_MemoryStorage.__module__, "tester@localhost") == "TESTED"

    assert store.get(test_MemoryStorage.__module__, "tester2@localhost") == "START"

    store.clear()

    assert store.get(test_MemoryStorage.__module__, "tester@localhost") == "START"

def test_ShelveStorage():
    store = ShelveStorage("tests/states.db")

    store.set(test_ShelveStorage.__module__, "tester@localhost", "TESTED")
    assert store.get(test_MemoryStorage.__module__, "tester@localhost") == "TESTED"

    assert store.get(test_MemoryStorage.__module__, "tester2@localhost") == "START"

    store.clear()
    assert store.get(test_MemoryStorage.__module__, "tester@localhost") == "START"


@with_setup(setup_salmon_dirs, teardown_salmon_dirs)
def test_RoutingBase():
    assert len(Router.ORDER) == 0
    assert len(Router.REGISTERED) == 0

    Router.load(['salmon_tests.simple_fsm_mod'])
    import simple_fsm_mod

    assert len(Router.ORDER) > 0
    assert len(Router.REGISTERED) > 0

    message = MailRequest('fakepeer', 'zedshaw@localhost', 'users-subscribe@localhost', "")
    Router.deliver(message)
    assert Router.in_state(simple_fsm_mod.CONFIRM, message)

    confirm = MailRequest('fakepeer', '"Zed Shaw" <zedshaw@localhost>',  'users-confirm-1@localhost', "")
    Router.deliver(confirm)
    assert Router.in_state(simple_fsm_mod.POSTING, message)

    Router.deliver(message)
    assert Router.in_state(simple_fsm_mod.NEXT, message)

    Router.deliver(message)
    assert Router.in_state(simple_fsm_mod.END, message)

    Router.deliver(message)
    assert Router.in_state(simple_fsm_mod.START, message)

    Router.clear_states()
    explosion = MailRequest('fakepeer',  '<hacker@localhost>',   'start-explode@localhost', "")
    Router.LOG_EXCEPTIONS=True
    Router.deliver(explosion)

    assert Router.in_error(simple_fsm_mod.END, explosion)

    Router.clear_states()
    Router.LOG_EXCEPTIONS=False
    explosion = MailRequest('fakepeer',  'hacker@localhost',   'start-explode@localhost', "")
    assert_raises(RuntimeError, Router.deliver, explosion)

    Router.reload()
    assert 'salmon_tests.simple_fsm_mod' in Router.HANDLERS
    assert len(Router.ORDER)
    assert len(Router.REGISTERED)


    message = MailRequest('fakepeer', 'zedshaw@localhost',
                          ['users-subscribe@localhost',
                           'users-confirm-1@localhost'], "Fake body.")

    Router.deliver(message)

    assert Router.in_state(simple_fsm_mod.POSTING, message), "Router state: %r" % Router.get_state('simple_fsm_mod', message)


def test_Router_undeliverable_queue():
    Router.clear_routes()
    Router.clear_states()

    Router.UNDELIVERABLE_QUEUE = Mock()
    msg = MailRequest('fakepeer', 'from@localhost', 'to@localhost', "Nothing")

    Router.deliver(msg)
    assert Router.UNDELIVERABLE_QUEUE.push.called



@raises(NotImplementedError)
def test_StateStorage_get_raises():
    s = StateStorage()
    s.get("raises", "raises")

@raises(NotImplementedError)
def test_StateStorage_set_raises():
    s = StateStorage()
    s.set("raises", "raises", "raises")

@raises(NotImplementedError)
def test_StateStorage_clear_raises():
    s = StateStorage()
    s.clear()

@raises(TypeError)
def test_route___get___raises():
    class BadRoute(object):

        @route("test")
        def wont_work(message, **kw):
            pass

    br = BadRoute()
    br.wont_work("raises")

@patch('__builtin__.reload', new=Mock(side_effect=ImportError))
@patch('salmon.routing.LOG', new=Mock())
def test_reload_raises():
    Router.LOG_EXCEPTIONS=True
    Router.reload()
    assert routing.LOG.exception.called

    Router.LOG_EXCEPTIONS=False
    routing.LOG.exception.reset_mock()
    assert_raises(ImportError, Router.reload)
    assert not routing.LOG.exception.called

    routing.LOG.exception.reset_mock()
    Router.LOG_EXCEPTIONS=True
    Router.load(['fake.handler'])
    assert routing.LOG.exception.called

    Router.LOG_EXCEPTIONS=False
    routing.LOG.exception.reset_mock()
    assert_raises(ImportError, Router.load, ['fake.handler'])
    assert not routing.LOG.exception.called


