from __future__ import unicode_literals
from future import standard_library  # noqa
import threading
from reg.implicit import implicit
from reg.registry import Registry
from reg.generic import generic


def setup_function(f):
    implicit.initialize(Registry())


def teardown_function(f):
    implicit.clear()


def test_lookup_in_main():
    assert implicit.lookup is implicit.base_lookup


def test_lookup_in_thread_uses_default():
    log = []

    def f():
        log.append(implicit.lookup)

    thread = threading.Thread(target=f)
    thread.start()
    thread.join()
    assert len(log) == 1
    assert log[0] is implicit.base_lookup


def test_changed_lookup_in_thread_doesnt_affect_main():
    # a different ILookup
    # (we don't actually fulfill the interface as that's not needed for
    # this test)
    different_lookup = object()

    log = []

    def f():
        implicit.lookup = different_lookup
        log.append(implicit.lookup)

    thread = threading.Thread(target=f)
    thread.start()
    thread.join()
    assert len(log) == 1
    assert log[0] is different_lookup
    assert implicit.lookup is implicit.base_lookup


def test_implicit_clear():
    implicit.clear()

    assert implicit.lookup is None
    assert implicit.base_lookup is None

    log = []

    def f():
        log.append(implicit.lookup)
        log.append(implicit.base_lookup)

    thread = threading.Thread(target=f)
    thread.start()
    thread.join()
    assert log[0] is None
    assert log[1] is None


def test_implicit_reset_main():
    other_lookup = object()
    implicit.lookup = other_lookup
    assert implicit.lookup is other_lookup
    assert implicit.lookup is not implicit.base_lookup
    implicit.reset()
    assert implicit.lookup is implicit.base_lookup


def test_implicit_reset_thread():
    log = []
    other_lookup = object()

    def f():
        implicit.lookup = other_lookup
        log.append(implicit.lookup)
        implicit.reset()
        log.append(implicit.lookup)

    thread = threading.Thread(target=f)
    thread.start()
    thread.join()
    assert log[0] is other_lookup
    assert log[1] is implicit.base_lookup


def test_lookup_in_thread_does_not_use_changed_default():
    log = []

    def f():
        log.append(implicit.lookup)
    thread = threading.Thread(target=f)

    other_lookup = object()
    implicit.lookup = other_lookup

    thread.start()
    thread.join()
    assert len(log) == 1
    # possibly contrary to expectations, changing the default lookup
    # in the main thread does not affect sub-threads; they will still
    # use the original initialization
    assert log[0] is implicit.base_lookup


def test_implicit_component_lookup():
    @generic
    def func():
        pass

    reg = Registry()

    reg.register(func, (), 'test component')

    implicit.initialize(reg)
    assert func.component() == 'test component'
