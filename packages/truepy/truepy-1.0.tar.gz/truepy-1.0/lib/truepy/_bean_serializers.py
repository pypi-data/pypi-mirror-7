# coding=utf-8
'''
truepy
Copyright (C) 2014 Moses Palmér

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import types

from datetime import datetime, timedelta

from ._bean import bean_serializer, bean_deserializer, camel_to_snake, \
    deserialize, value_to_xml, UnknownFragmentException


@bean_serializer(bool)
def str_serializer(value):
    return value_to_xml('true' if value else 'false', 'boolean')


@bean_serializer(int)
def str_serializer(value):
    return value_to_xml(str(value), 'int')


@bean_serializer(str)
def str_serializer(value):
    return value_to_xml(value, 'string')


if sys.version_info.major < 3:
    @bean_serializer(unicode)
    def str_serializer(value):
        return value_to_xml(value, 'string')


@bean_serializer(datetime)
def datetime_serializer(v):
    ms_since_epoch = int(
        (v - datetime.strptime('1970-01-01 UTC', '%Y-%m-%d %Z')).total_seconds()
            * 1000)
    return value_to_xml(
        str(ms_since_epoch), 'long', 'java.util.Date')


@bean_deserializer
def bool_deserializer(element):
    if element.tag == 'boolean':
        value = element.text.strip()
        if value == 'true':
            return True
        elif value == 'false':
            return False
        else:
            raise ValueError('invalid boolean value: %s', value)
    else:
        raise UnknownFragmentException()


@bean_deserializer
def int_deserializer(element):
    if element.tag == 'int':
        return int(element.text.strip())
    else:
        raise UnknownFragmentException()


@bean_deserializer
def str_deserializer(element):
    if element.tag == 'string':
        return (element.text or '').strip()
    else:
        raise UnknownFragmentException()


@bean_deserializer
def datetime_deserializer(element):
    if element.tag == 'object' \
            and element.attrib.get('class', None) == 'java.util.Date':
        ms_since_epoch = int(element.find('.//long').text)
        return datetime.strptime('1970-01-01 UTC', '%Y-%m-%d %Z') + timedelta(
            milliseconds = ms_since_epoch)
    else:
        raise UnknownFragmentException()


_DESERIALIZER_CLASSES = {}

def default_bean_deserialize(self, element):
    """
    The default bean deserialiser for classes decorated with @bean_class.

    This function will call the constructor with all properties read from
    element as named arguments. If this fails with TypeError, it will call the
    empty constructor and then set all properties.

    @param element
        The XML fragment to deserialise.
    @return an instance of self
    """
    properties = {camel_to_snake(e.attrib['property']): deserialize(e[0])
        for e in element.findall('.//void')}

    try:
        return self(**properties)
    except TypeError:
        pass

    result = self()
    for name, value in properties.iteritems():
        setattr(result, name, value)
    return result

def bean_class(class_name):
    """
    Marks a class as deserialisable and sets its class name.

    A class decorated with this decorator does not need to define 'bean_class'.

    The class method 'bean_deserialize' will be called when the XML fragment
    <object class="(class_name)">...</object> is encountered. If the class does
    not have this callable, it will be set to default_bean_deserialize.

    @param class_name
        The class name to use for this class.
    """
    def inner(c):
        if not callable(getattr(c, 'bean_deserialize', None)):
            c.bean_deserialize = types.MethodType(default_bean_deserialize, c)
        c.bean_class = class_name
        _DESERIALIZER_CLASSES[class_name] = c
        return c

    return inner

@bean_deserializer
def object_deserializer(element):
    """
    Deserialises <object class="(class_name)">...</object> for registered values
    of class_name.

    A class is registered by decorating it with @bean_class.
    """
    try:
        return _DESERIALIZER_CLASSES[element.attrib['class']].bean_deserialize(
            element)
    except KeyError:
        raise UnknownFragmentException()
