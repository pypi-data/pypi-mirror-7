#!/usr/bin/env python

"""Tests the j5basic.Singleton implementation"""

from . import Singleton
import gc
import types

def test_basic():
    """Tests most basic singleton definition, that it works and constructing always produces the same result"""
    class Highlander(object):
        __metaclass__ = Singleton.Singleton
    assert issubclass(Highlander, object)
    highlander = Highlander()
    assert isinstance(highlander, Highlander)
    highlander2 = Highlander()
    assert highlander2 is highlander

def test_non_oldstyle():
    """Tests that Singleton classes are implictly newstyle"""
    class Highlander:
        __metaclass__ = Singleton.Singleton
    assert isinstance(Highlander, object)
    assert not isinstance(Highlander, types.ClassType)
    highlander = Highlander()
    assert isinstance(highlander, Highlander)
    highlander2 = Highlander()
    assert highlander2 is highlander

def test_subclass():
    """Tests that subclasses are distinct singletons"""
    class Highlander(object):
        __metaclass__ = Singleton.Singleton
    class VeryHighlander(Highlander):
        pass
    assert issubclass(VeryHighlander, Highlander)
    assert issubclass(VeryHighlander, object)
    highlander = Highlander()
    assert isinstance(highlander, Highlander)
    veryhighlander = VeryHighlander()
    assert veryhighlander is not highlander
    veryhighlander2 = VeryHighlander()
    assert veryhighlander2 is veryhighlander

def test_deletion():
    """Tests that deletion and garbage collection don't destroy the singleton"""
    class Highlander(object):
        __metaclass__ = Singleton.Singleton
    assert issubclass(Highlander, object)
    highlander = Highlander()
    highlander.value = 3
    assert isinstance(highlander, Highlander)
    highid = id(highlander)
    del highlander
    gc.collect()
    highlander2 = Highlander()
    assert id(highlander2) == highid
    assert highlander2.value == 3

def test_args_irrelevant():
    """Tests that arguments passed to the constructor don't have any effect after the initial construction"""
    class Highlander(object):
        __metaclass__ = Singleton.Singleton
        def __init__(self, clan):
            self.clan = clan
    assert issubclass(Highlander, object)
    highlander = Highlander("McDonald")
    assert isinstance(highlander, Highlander)
    highlander2 = Highlander("BurgerKing")
    assert highlander2.clan == "McDonald"
    assert highlander2 is highlander

