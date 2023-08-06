"""Tests for the property cache."""

from django.test import TestCase

import optimizations


class CachedPropertyTestObj(object):

    def __init__(self, name):
        self._name = name
        self._get_count = 0
    
    @optimizations.cached_property
    def name(self):
        self._get_count += 1
        return self._name
        
    @name.setter
    def name(self, value):
        self._name = value
        
    @name.deleter
    def name(self):
        del self._name
        
    @optimizations.cached_property
    def read_only(self):
        self._get_count += 1
        return "baz"


class OptimizationsTest(TestCase):

    def testCachedProperty(self):
        self.assertTrue(isinstance(CachedPropertyTestObj.name, property))
        self.assertTrue(isinstance(CachedPropertyTestObj.name, optimizations.cached_property))
        # Create the test obj.
        obj = CachedPropertyTestObj("foo")
        self.assertEqual(obj._get_count, 0)
        # Call the getter.
        self.assertEqual(obj.name, "foo")
        self.assertEqual(obj._get_count, 1)
        self.assertEqual(obj.name, "foo")
        self.assertEqual(obj._get_count, 1)
        self.assertEqual(obj._name_cache, "foo")
        # Call the setter.
        obj.name = "bar"
        self.assertEqual(obj.name, "bar")
        self.assertEqual(obj._get_count, 1)
        self.assertEqual(obj._name_cache, "bar")
        # Call the deleter.
        del obj.name
        self.assertRaises(AttributeError, lambda: obj.name)
        # Call the setter again.
        obj.name = "foobar"
        self.assertEqual(obj.name, "foobar")
        self.assertEqual(obj._get_count, 2)
        # Check the read-only property.
        self.assertEqual(obj.read_only, "baz")
        self.assertEqual(obj._get_count, 3)
        self.assertEqual(obj.read_only, "baz")
        self.assertEqual(obj._get_count, 3)
        # Try modifying a read-only property.
        def set_read_only():
            obj.read_only = "foo"
        self.assertRaises(AttributeError, set_read_only)
        def del_read_only():
            del obj.read_only
        self.assertRaises(AttributeError, del_read_only)