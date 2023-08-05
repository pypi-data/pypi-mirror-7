#!/usr/bin/env python
"""
Module with classes for PEPA model.

"""

class BaseNode(object):
    left, right = None, None
    data = None
    asttype = None
    length = None

    def __init__(self, data, asttype):
        self.data = data
        self.asttype = asttype

    def __str__(self):
        return self.data

class ChoiceNode(BaseNode):
    lhs, rhs = None, None
    reolved = None

    def __init__(self, data, asttype):
        super(ChoiceNode, self).__init__(data, asttype)

class PrefixNode(BaseNode):
    action, resolved, rate, var_rate  = None, None, None, None

    def __init__(self, data, asttype):
        super(PrefixNode, self).__init__(data, asttype)

class DefNode(BaseNode):
    process, resolved = None, None

    def __init__(self, data, asttype):
        super(DefNode, self).__init__(data, asttype)

class ActivityNode(BaseNode):

    action, rate = "", ""

    def __init__(self, data, asttype):
        super(ActivityNode, self).__init__(data, asttype)

class ProcdefNode(BaseNode):
    name  = None
    aggregation = False
    aggr_num = 0

    def __init__(self, data, asttype):
        super(ProcdefNode, self).__init__(data, asttype)

class CoopNode(BaseNode):
    cooptype, actionset = None, None

    def __init__(self, data, asttype):
        super(CoopNode, self).__init__(data, asttype)

class SyncsetNode(BaseNode):
    actionset = None

    def __init__(self, data, asttype):
        super(SyncsetNode, self).__init__(data, asttype)

