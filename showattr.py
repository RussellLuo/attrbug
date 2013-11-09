#!/usr/bin/env python
# -*- coding: utf-8 -*-

import types
import inspect

def showattr(obj, name, method='get'):
    """Show (type, location) of attribute named `name`, after trying to
       access (method specified by `method`) the attribute via object `obj`.

        type                | meaning
        ------------------- | -----------------------------------------------------------
        attribute           | `treated as` normal attribute (returned directly)
        get descriptor      | descriptor has __get__ (which will be called)
        set descriptor      | descriptor has __set__ or __delete__ (which will be called)
        non-data descriptor | get descriptor, but not set descriptor
        data descriptor     | get descriptor, and also set descriptor

        Note:
            `treated as` means: an object is processed as a normal attribute
                                *semantically* even if it looks like a valid descriptor.

             A typical example is: "descriptor" within instance dictionary is `treated as` a normal attribute.

             For more details, see http://www.cnblogs.com/russellluo/p/3414943.html
    """
    assert isnewstyle(obj), \
           '`obj` must be a new-style instance or class'
    assert isinstance(name, basestring), \
           '`name` must be a string'
    assert (method in ('get', 'set', 'del')), \
           "`method` must be in ('get', 'set', 'del')"

    if inspect.isclass(obj):
        route = {
            'get': getattr_via_class,
            'set': setattr_via_class,
            'del': delattr_via_class
        }
    else:
        route = {
            'get': getattr_via_instance,
            'set': setattr_via_instance,
            'del': delattr_via_instance
        }
    target = route.get(method, None)
    if target is not None:
        info = target(obj, name)
        print(info)

def getattr_via_class(cls, name):
    """Get attribute named `name` via class `cls`.

    For algorithm details, see http://www.cnblogs.com/russellluo/p/3414943.html#1_2
    """
    mcls = type(cls)
    try:
        # step 1
        _getattribute = getattr(mcls, '__getattribute__', None)
        if isoverridemethod(_getattribute):
            _getattribute(cls, name) # executed to trigger possible EXCEPTION
            return ('attribute',
                    '%s.%s' % (mcls.__name__, _getattribute.__name__))
        # step 2
        attr = None
        location = None
        for c in mcls.__mro__:
            attr = c.__dict__.get(name, None)
            if attr is not None:
                location = c.__name__ + '.__dict__'
                break
        # step 3
        if isdatadescriptor(attr):
            attr.__get__(cls, mcls) # executed to trigger possible EXCEPTION
            return ('data descriptor', location)
        else:
            # step 4
            for c in cls.__mro__:
                attr_c = c.__dict__.get(name, None)
                if attr_c is not None:
                    location = c.__name__ + '.__dict__'
                    if isgetdescriptor(attr_c):
                        attr_c.__get__(None, cls) # executed to trigger possible EXCEPTION
                        return ('get descriptor', location)
                    else:
                        return ('attribute', location)
            # step 5
            if isnondatadescriptor(attr):
                attr.__get__(cls, mcls) # executed to trigger possible EXCEPTION
                return ('non-data descriptor', location)
            # step 6
            elif attr is not None:
                return ('attribute', location)
            else:
                raise AttributeError
    except AttributeError:
        # step 7
        _getattr = getattr(mcls, '__getattr__', None)
        if _getattr is not None:
            return ('attribute',
                    '%s.%s' % (mcls.__name__, _getattr.__name__))
        # step 8
        return ('attribute', 'Not found')

def setattr_via_class(cls, name):
    """Set attribute named `name` via class `cls`.

    For algorithm details, see http://www.cnblogs.com/russellluo/p/3414943.html#2_2
    """
    return setattr_via_instance(cls, name)

def delattr_via_class(cls, name):
    """Delete attribute named `name` via class `cls`.

    For algorithm details, see http://www.cnblogs.com/russellluo/p/3414943.html#3_1
    """
    return delattr_via_instance(cls, name)

def getattr_via_instance(inst, name):
    """Get attribute named `name` via instance `inst`.

    For algorithm details, see http://www.cnblogs.com/russellluo/p/3414943.html#1_1
    """
    cls = type(inst)
    try:
        # step 1
        _getattribute = getattr(cls, '__getattribute__', None)
        if isoverridemethod(_getattribute):
            _getattribute(inst, name) # executed to trigger possible EXCEPTION
            return ('attribute',
                    '%s.%s' % (cls.__name__, _getattribute.__name__))
        # step 2
        attr = None
        location = None
        for c in cls.__mro__:
            attr = c.__dict__.get(name, None)
            if attr is not None:
                location = c.__name__ + '.__dict__'
                break
        # step 3
        if isdatadescriptor(attr):
            attr.__get__(inst, cls) # executed to trigger possible EXCEPTION
            return ('data descriptor', location)
        # step 4
        elif getattr(inst, '__dict__', None) and name in inst.__dict__:
            return ('attribute', '%s.__dict__' % instancename(inst))
        # step 5
        elif isnondatadescriptor(attr):
            attr.__get__(inst, cls) # executed to trigger possible EXCEPTION
            return ('non-data descriptor', location)
        # step 6
        elif attr is not None:
            return ('attribute', location)
        else:
            raise AttributeError
    except AttributeError:
        # step 7
        _getattr = getattr(cls, '__getattr__', None)
        if _getattr is not None:
            return ('attribute',
                    '%s.%s' % (cls.__name__, _getattr.__name__))
        # step 8
        return ('attribute', 'Not found')

def setattr_via_instance(inst, name):
    """Set attribute named `name` via instance `inst`.

    For algorithm details, see http://www.cnblogs.com/russellluo/p/3414943.html#2_1
    """
    cls = type(inst)

    # step 1
    _setattr = getattr(cls, '__setattr__', None)
    if isoverridemethod(_setattr):
        return ('attribute',
                '%s.%s' % (cls.__name__, _setattr.__name__))
    # step 2
    for c in cls.__mro__:
        attr = c.__dict__.get(name, None)
        if attr is not None:
            if issetdescriptor(attr):
                location = c.__name__ + '.__dict__'
                return ('set descriptor', location)
            break
    # step 3
    return ('attribute', '%s.__dict__' % instancename(inst))

def delattr_via_instance(inst, name):
    """Delete attribute named `name` via instance `inst`.

    For algorithm details, see http://www.cnblogs.com/russellluo/p/3414943.html#3
    """
    cls = type(inst)

    # step 1
    _delattr = getattr(cls, '__delattr__', None)
    if isoverridemethod(_delattr):
        return ('attribute',
                '%s.%s' % (cls.__name__, _delattr.__name__))
    # step 2
    for c in cls.__mro__:
        attr = c.__dict__.get(name, None)
        if attr is not None:
            if issetdescriptor(attr):
                location = c.__name__ + '.__dict__'
                return ('set descriptor', location)
            break
    # step 3
    if getattr(inst, '__dict__', None) and name in inst.__dict__:
        return ('attribute', '%s.__dict__' % instancename(inst))
    # step 4
    return ('attribute', 'Not found')

def instancename(inst):
    """Get name of instance `inst`.
    """
    return getattr(inst, '__name__', None) or 'instance'

def isnewstyle(obj):
    """Check if `obj` is a new-style instance or class.
    """
    return type(obj) not in (types.InstanceType, types.ClassType)

def isoverridemethod(func):
    """Check if `func` is an user-defined method.
    """
    if func is None:
        return False
    return isinstance(func, types.MethodType)
    #return inspect.ismethod(func)

def isgetdescriptor(attr):
    """Check if `attr` is a get descriptor.
    """
    return hasattr(attr, '__get__')

def issetdescriptor(attr):
    """Check if `attr` is a set descriptor.
    """
    return (hasattr(attr, '__set__') or
            hasattr(attr, '__delete__'))

def isnondatadescriptor(attr):
    """Check if `attr` is a non-data descriptor.
    """
    return (isgetdescriptor(attr) and
            not issetdescriptor(attr))

def isdatadescriptor(attr):
    """Check if `attr` is a data descriptor.
    """
    return (isgetdescriptor(attr) and
            issetdescriptor(attr))
