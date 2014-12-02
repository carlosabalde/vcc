# -*- coding: utf-8 -*-

'''
:copyright: (c) 2014 by Carlos Abalde, see AUTHORS.txt for more details.
'''

from __future__ import absolute_import
import HLL


class Counter(object):
    def __init__(self, op):
        self.__op = op
        self._value = None

    @property
    def op(self):
        return self.__op

    @property
    def value(self):
        return self._value

    def append(self, raw):
        raise NotImplementedError('Please implement this method.')


class CountOp(Counter):
    def __init__(self, *args, **kwargs):
        super(CountOp, self).__init__(*args, **kwargs)
        self._value = 0

    def append(self, raw):
        self._value += 1


class HLLOp(Counter):
    def __init__(self, k, seed, *args, **kwargs):
        super(HLLOp, self).__init__(*args, **kwargs)
        self._value = HLL.HyperLogLog(int(k), int(seed))

    def append(self, raw):
        self._value.add(raw)

    @Counter.value.getter
    def value(self):
        return int(self._value.cardinality())


class FirstOp(Counter):
    def __init__(self, *args, **kwargs):
        super(FirstOp, self).__init__(*args, **kwargs)

    def append(self, raw):
        if self._value is None:
            self._value = raw


class LastOp(Counter):
    def __init__(self, *args, **kwargs):
        super(LastOp, self).__init__(*args, **kwargs)

    def append(self, raw):
        self._value = raw


class NumericCounter(Counter):
    def __init__(self, *args, **kwargs):
        super(NumericCounter, self).__init__(*args, **kwargs)

    def append(self, raw):
        value = self._raw2number(raw)
        if value is not None:
            self._append_number(value)

    def _raw2number(self, raw):
        try:
            return int(raw)
        except ValueError:
            try:
                return float(raw)
            except ValueError:
                return None

    def _append_number(self, value):
        raise NotImplementedError('Please implement this method.')


class AvgOp(NumericCounter):
    def __init__(self, *args, **kwargs):
        super(AvgOp, self).__init__(*args, **kwargs)

    def _append_number(self, value):
        if self._value is not None:
            self._value = (self._value + value) / 2.0
        else:
            self._value = value


class MinOp(NumericCounter):
    def __init__(self, *args, **kwargs):
        super(MinOp, self).__init__(*args, **kwargs)

    def _append_number(self, value):
        if self._value is None or value < self._value:
            self._value = value


class MaxOp(NumericCounter):
    def __init__(self, *args, **kwargs):
        super(MaxOp, self).__init__(*args, **kwargs)

    def _append_number(self, value):
        if self._value is None or value > self._value:
            self._value = value


_OPERATORS = {
    'count': CountOp,
    'hll': HLLOp,
    'avg': AvgOp,
    'min': MinOp,
    'max': MaxOp,
    'first': FirstOp,
    'last': LastOp,
}


def instance(op):
    items = op.split(',')
    klass = _OPERATORS.get(items[0], None)
    if klass is not None:
        try:
            return klass(*items[1:], op=op)
        except:
            pass
    return None
