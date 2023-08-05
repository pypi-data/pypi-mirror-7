# -*- coding: utf-8 -*-
#
# library for Robot Framework to inspect python modules
#
import imp
import os.path


BASE_PATH = os.path.dirname(__file__)


class Inspector(object):
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def variable_presented(self, modulePath, name):
        module = imp.load_source("module", modulePath)
        value = getattr(module, name)
        if not value:
            raise AssertionError(
                "Module: %s has no variable '%s'!" % (self.modulePath, name)
            )

    def is_type_of(self, element, reference):
        if type(element) != reference:
            raise AssertionError(
                "type(%s) != %s" % (str(type(element)), str(reference))
            )

    def call(self, fn, *args, **kwargs):
        return fn(*args, **kwargs)

    def greater_or_equal_than(self, lvalue, rvalue):
        if int(lvalue) < int(rvalue):
            raise AssertionError(str(lvalue) + " is not >= " + str(rvalue))

    def length(self, val):
        return len(val)
