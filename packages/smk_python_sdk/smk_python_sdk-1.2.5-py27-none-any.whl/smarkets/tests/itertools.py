from nose.tools import eq_, raises

from smarkets.itertools import (
    group, inverse_mapping, listitems, listkeys, listvalues, mapkeys, mapvalues,
)


def test_mapkeys():
    eq_(mapkeys(str, {1: 'this', 2: 'that'}),
        {'1': 'this', '2': 'that'})


def test_mapvalues():
    eq_(mapvalues(tuple, {1: 'this', 2: 'that'}),
        {1: ('t', 'h', 'i', 's',), 2: ('t', 'h', 'a', 't',)})


def test_group():
    for i, n, o in (
        ('', 2, ()),
        ('A', 2, (('A',),)),
        ('AB', 2, (('A', 'B'),)),
        ('ABCDE', 2, (('A', 'B'), ('C', 'D'), ('E',))),
    ):
        yield check_group, i, n, o


def check_group(i, n, o):
    eq_(tuple(group(i, n)), tuple(o))


def test_listxxx():
    data = dict(a='a', b='x', c=123)
    keys = listkeys(data)
    values = listvalues(data)
    items = listitems(data)
    types = map(type, (keys, values, items))
    eq_(set(types), set([list]))

    eq_(sorted(keys), ['a', 'b', 'c'])
    eq_(sorted(values), [123, 'a', 'x'])
    eq_(sorted(items), [('a', 'a'), ('b', 'x'), ('c', 123)])


def test_inverse_mapping_works():
    eq_(inverse_mapping({'a': 123, 'x': 'x'}), {123: 'a', 'x': 'x'})


@raises(ValueError)
def test_inverse_mapping_raises_exception_when_values_arent_unique():
    inverse_mapping({'a': 1, 'b': 1})
