# -*- coding: utf-8 -*-

from nose.tools.trivial import assert_true, assert_false

from valhalla import Schema


def test_range():
    s = Schema()
    s.some_number.range()
    s.validate({'some_number': 4})
    assert_true(s.valid)

    s = Schema()
    s.some_number.range(low=1)
    s.validate({'some_number': 0})
    assert_false(s.valid)
    s.reset()
    s.validate({'some_number': 1})
    assert_true(s.valid)
    s.reset()
    s.validate({'some_number': 2})
    assert_true(s.valid)

    s = Schema()
    s.some_number.range(high=5)
    s.validate({'some_number': 6})
    assert_false(s.valid)
    s.reset()
    s.validate({'some_number': 4})
    assert_true(s.valid)

    s = Schema()
    s.some_number.range(low=2, high=3)
    s.validate({'some_number': 2})
    assert_true(s.valid)


def test_minimum():
    s = Schema()
    s.some_number.minimum(1)
    s.validate({'some_number': 0})
    assert_false(s.valid)
    s.reset()
    s.validate({'some_number': 1})
    assert_true(s.valid)


def test_maximum():
    s = Schema()
    s.some_number.maximum(5)
    s.validate({'some_number': 6})
    assert_false(s.valid)
    s.reset()
    s.validate({'some_number': 5})
    assert_true(s.valid)


def test_between():
    s = Schema()
    s.some_number.between(5, 10)
    s.validate({'some_number': 5})
    assert_false(s.valid)
    s.reset()
    s.validate({'some_number': 6})
    assert_true(s.valid)
    s.reset()
    s.validate({'some_number': 10})
    assert_false(s.valid)


def test_equal():
    s = Schema()
    s.some_number.equal(10)
    s.validate({'some_number': 11})
    assert_false(s.valid)
    s.reset()
    s.validate({'some_number': 10})
    assert_true(s.valid)


def test_zero():
    s = Schema()
    s.some_number.zero()
    s.validate({'some_number': 1})
    assert_false(s.valid)
    s.reset()
    s.validate({'some_number': 0})
    assert_true(s.valid)
