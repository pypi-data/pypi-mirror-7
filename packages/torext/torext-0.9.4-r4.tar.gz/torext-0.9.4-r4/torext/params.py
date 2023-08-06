#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import copy
import uuid
import datetime
import functools
from tornado.escape import _unicode, json_decode
from torext.errors import ValidationError, ParamsInvalidError


# don't know where to find the <type '_sre.SRE_Pattern'>
_pattern_class = type(re.compile(''))


class Field(object):
    name = None
    with_choices = True

    def __init__(self, description=None, key=None, required=False,
                 length=None, choices=None, default=None, null=True):
        self.description = description  # default message
        self.required = required  # used with ParamSet
        self.choices = choices
        self.key = key
        self.default = default
        self.null = null

        self.min_length = None
        assert length is None or isinstance(length, (int, tuple))
        if isinstance(length, int):
            assert length > 0
        if isinstance(length, tuple):
            assert len(length) == 2 and length[0] > 0
            if length[1] == 0:
                self.min_length = length[0]
            else:
                assert length[1] > length[0]
        self.length = length

    #@property
    #def name(self):
        #raise NotImplementedError

    def raise_exc(self, error_message=None):
        raise ValidationError(self.description, error_message)

    def _validate_length(self, value):
        length = self.length
        value_len = len(value)

        if isinstance(length, int):
            if value_len != length:
                self.raise_exc(
                    'Length of value should be %s, but %s' %
                    (length, value_len))
        else:
            if self.min_length:
                if value_len < self.min_length:
                    self.raise_exc(
                        'Length of value should be larger than %s' %
                        self.min_length)
            else:
                min, max = length
                if value_len < min or value_len > max:
                    self.raise_exc(
                        'Length should be >= %s and <= %s, but %s' %
                        (min, max, value_len))
        return value

    def _validate_choices(self, value):
        if not value in self.choices:
            self.raise_exc(
                'value "%s" is not one of %s' % (value, self.choices))
        return value

    def _validate_type(self, value):
        """Override this method to implement type specified validation"""
        return value

    def validate(self, value):
        # If null is allowed, skip other validates
        if not value:
            if self.null:
                return value
            else:
                self.raise_exc('empty value is not allowed')

        if self.length:
            self._validate_length(value)

        value = self._validate_type(value)

        # Validate choices after type, so that the value has been converted
        if self.with_choices and self.choices:
            self._validate_choices(value)

        return value

    def __get__(self, owner, cls):
        return owner.data.get(self.key, self.default)

    def __set__(self, owner, value):
        raise AttributeError('You can not set value to a param field')

    def spawn(self, **kwargs):
        new = copy.copy(self)
        new.__dict__.update(kwargs)
        #for k, v in kwargs.iteritems():
            #setattr(new, k, v)
        return new


class RegexField(Field):
    def __init__(self, *args, **kwgs):
        # assume pattern is a raw string like r'\n'
        if 'pattern' in kwgs:
            pattern = kwgs.pop('pattern')
            self.regex = re.compile(pattern)
        assert hasattr(self, 'regex'),\
            'regex should be set if no keyword argument pattern passed'
        assert isinstance(self.regex, _pattern_class),\
            'regex should be a compiled pattern'

        super(RegexField, self).__init__(*args, **kwgs)

    def _validate_type(self, value):
        # Equate the type of regex pattern and the checking value
        pattern_type = type(self.regex.pattern)
        c_value = value
        if not isinstance(value, pattern_type):
            try:
                c_value = pattern_type(value)
            except Exception, e:
                self.raise_exc(
                    'value could not be converted into type "%s"'
                    'of regex pattern, error: %s' % (pattern_type, e))
        if not self.regex.search(c_value):
            self.raise_exc(
                'regex pattern (%s, %s) is not match with value "%s"' %
                (self.regex.pattern, self.regex.flags, c_value))
        return value


class WordField(RegexField):
    """
    >>> v = WordField('should not contain punctuations')
    >>> s = 'oh123,'
    >>> v.validate(s)
    ValidationError: should not contain punctuations
    """

    regex = re.compile(r'^[\w]+$')


# take from Django
EMAIL_REGEX = re.compile(
    # dot-atom
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
    # quoted-string
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|'
    r'\\[\001-011\013\014\016-\177])*"'
    # domain
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$',
    re.IGNORECASE)


class EmailField(RegexField):
    regex = EMAIL_REGEX


URL_REGEX = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
    r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class URLField(RegexField):
    regex = URL_REGEX


class IntegerField(Field):
    def __init__(self, *args, **kwargs):
        min = kwargs.pop('min', None)
        max = kwargs.pop('max', None)
        if min is not None:
            assert isinstance(min, int)
        if max is not None:
            assert isinstance(max, int)
        if min is not None and max is not None:
            assert min <= max

        self.min = min
        self.max = max

        super(IntegerField, self).__init__(*args, **kwargs)

    def _validate_type(self, value):
        try:
            value = int(value)
        except (ValueError, TypeError):
            self.raise_exc(
                'could not convert value "%s" into int type' % value)

        if self.min:
            if value < self.min:
                self.raise_exc('value is too small, min %s' % self.min)
        if self.max:
            if value > self.max:
                self.raise_exc('vaule is too big, max %s' % self.max)

        return value


# TODO
class FloatField(Field):
    pass


# TODO
class DateField(Field):
    def __init__(self, *args, **kwargs):
        datefmt = kwargs.pop('datefmt', None)
        assert datefmt, '`datefmt` argument should be passed for DateField'
        self.datefmt = datefmt
        super(DateField, self).__init__(*args, **kwargs)

    def _validate_type(self, value):
        try:
            value = datetime.datetime.strptime(value, self.datefmt)
        except ValueError:
            self.raise_exc(
                'Could not convert %s to datetime object by format %s' %
                (value, self.datefmt))
        return value


class ListField(Field):
    with_choices = False

    def __init__(self, *args, **kwargs):
        self.item_field = kwargs.pop('item_field', None)
        super(ListField, self).__init__(*args, **kwargs)

    def _validate_type(self, value):
        if not isinstance(value, list):
            self.raise_exc('Not a list')

        if self.item_field:
            formatted_value = []
            for i in value:
                formatted_value.append(self.item_field.validate(i))
            value = formatted_value

        bad_values = []
        if self.choices:
            for i in value:
                if not i in self.choices:
                    bad_values.append(i)
        if bad_values:
            self.raise_exc('%s is/are not allowed' % bad_values)

        return value


class UUIDField(Field):
    def _validate_type(self, value):
        try:
            return uuid.UUID(value)
        except ValueError, e:
            self.raise_exc('Invalid uuid string: %s' % e)


class ParamSetMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = {}
        for k, v in attrs.iteritems():
            # TODO Assert not reserved attribute name
            if isinstance(v, Field):
                v.name = k
                if not v.key:
                    v.key = k
                fields[k] = v
        attrs['_fields'] = fields
        return type.__new__(cls, name, bases, attrs)


# TODO user-define check function
class ParamSet(object):
    """
    item in `errors` could be:
        tuple: (key, ValidationError)
        exception: ValidationError
    """
    __metaclass__ = ParamSetMeta
    __datatype__ = 'form'  # or 'json'

    @classmethod
    def keys(cls):
        return [i.key for i in cls._fields.itervalues()]

    def __init__(self, **kwargs):
        if 'form' == self.__datatype__:
            self._raw_data = {}
            # Processing on handler.request.arguments, utf-8 values
            for k in kwargs:
                if isinstance(kwargs[k], list):
                    if len(kwargs[k]) > 1:
                        self._raw_data[k] = map(_unicode, kwargs[k])
                    else:
                        self._raw_data[k] = _unicode(kwargs[k][0])
                else:
                    self._raw_data[k] = _unicode(kwargs[k])
        else:
            self._raw_data = kwargs

        self.data = {}
        self.errors = []

        self.validate()

    def validate(self):
        for name, field in self.__class__._fields.iteritems():
            key = field.key
            if key in self._raw_data:

                value = self._raw_data[key]

                try:
                    value = field.validate(value)
                    func_name = 'validate_' + name
                    if hasattr(self, func_name):
                        value = getattr(self, func_name)(value)
                        assert value is not None, (
                            'Forget to return value after validation?'
                            'Or this is caused by your explicitly returns'
                            'None, which is not allowed in the mechanism.')
                except ValidationError, e:
                    self.errors.append((key, e))
                else:
                    self.data[key] = value
            else:
                if field.required:
                    try:
                        field.raise_exc('%s is required' % key)
                    except ValidationError, e:
                        self.errors.append((key, e))
                #elif field.default is not None:
                    #self.data[key] = field.default

        for attr_name in dir(self):
            if attr_name.startswith('validate_') and\
                    attr_name[len('validate_'):] not in self._fields:
                try:
                    getattr(self, attr_name)()
                except ValidationError, e:
                    self.errors.append(e)

    def kwargs(self, *args):
        d = {}
        for k in args:
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        return d

    def has(self, name):
        return name in self.data

    def to_dict(self, include_none=False):
        """Convert the ParamSet instance to a dict, if `include_none` is True,
        the result will represent both data and schema.
        """
        d = {}
        for f in self.__class__._fields.itervalues():
            value = getattr(self, f.name)
            if value is not None or (value is None and include_none):
                d[f.key] = value
        return d

    def __str__(self):
        return self.__unicode__().encode('utf8')

    def __unicode__(self):
        return u'<%s: %s; errors=%s>' % (
            self.__class__.__name__,
            u','.join([u'%s=%s' % (k, v) for k, v in self.data.iteritems()]),
            self.errors)

    @classmethod
    def validation_required(cls, method):
        @functools.wraps(method)
        def wrapper(hdr, *args, **kwgs):
            if 'json' == cls.__datatype__:
                try:
                    arguments = json_decode(hdr.request.body)
                except Exception, e:
                    raise ParamsInvalidError('JSON decode failed: %s' % e)
            else:
                arguments = hdr.request.arguments
            # Instantiate ParamSet
            print 'cls', cls.__datatype__
            params = cls(**arguments)
            if params.errors:
                raise ParamsInvalidError(params.errors)
            hdr.params = params
            return method(hdr, *args, **kwgs)
        return wrapper


def define_params(kwargs, datatype='form'):
    param_class = type('AutoCreatedParams', (ParamSet, ), kwargs)
    param_class.__datatype__ = datatype
    return param_class.validation_required


def simple_params(datatype='form'):
    assert datatype in ('form', 'json')

    def decorator(method):
        @functools.wraps(method)
        def wrapper(hdr, *args, **kwgs):
            if 'json' == datatype:
                try:
                    params = json_decode(hdr.request.body)
                except Exception, e:
                    raise ParamsInvalidError('JSON decode failed: %s' % e)
            else:
                params = dict((k, v[0])
                              for k, v in hdr.request.arguments.iteritems())

            hdr.params = params
            return method(hdr, *args, **kwgs)
        return wrapper
    return decorator
