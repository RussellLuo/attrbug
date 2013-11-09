#!/usr/bin/env python
# -*- coding: utf-8 -*-

from showattr import showattr

def test_doc():
    """
        >>> class A(object):
        ...     attr = 'hello'
        ...
        >>> a = A()
        >>> showattr(a, 'attr')
        ('attribute', 'A.__dict__')
        >>> showattr(a, 'attr', 'set')
        ('attribute', 'instance.__dict__')

        >>> class Descr(object):
        ...     def __get__(self, instance, owner):
        ...         return 'why'
        ...
        >>> class A(object):
        ...     attr = Descr()
        ...     def __init__(self):
        ...         self.attr = Descr()
        ...
        >>> a = A()
        >>> showattr(a, 'attr')
        ('attribute', 'instance.__dict__')
        >>> showattr(A, 'attr')
        ('get descriptor', 'A.__dict__')
    """
    pass

if __name__ == '__main__':
    import doctest
    doctest.testmod()
