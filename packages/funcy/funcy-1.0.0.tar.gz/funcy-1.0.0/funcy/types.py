from collections import Mapping, Sequence, Iterator, Iterable

from .cross import xrange


__all__ = ('isa', 'is_mapping', 'is_seq', 'is_list', 'is_tuple',
           'is_seqcoll', 'is_seqcont',
           'iterable', 'is_iter')


def isa(*types):
    return lambda x: isinstance(x, types)

is_mapping = isa(Mapping)
is_seq = isa(Sequence)
is_list = isa(list)
is_tuple = isa(tuple)

is_seqcoll = isa(list, tuple)
is_seqcont = isa(list, tuple, Iterator, xrange)

iterable = isa(Iterable)
is_iter = isa(Iterator)
