from copy import deepcopy
from urllib2 import urlparse
import inspect
import re
import textwrap

from confmodel.errors import ConfigError
from confmodel.interfaces import IConfigData


class ConfigField(object):
    _creation_order = 0

    field_type = None

    def __init__(self, doc, required=False, default=None, static=False):
        # This hack is to allow us to track the order in which fields were
        # added to a config class. We want to do this so we can document fields
        # in the same order they're defined.
        self.creation_order = ConfigField._creation_order
        ConfigField._creation_order += 1
        self.name = None
        self.doc = doc
        self.required = required
        self.default = default
        self.static = static

    def get_doc(self):
        if self.field_type is None:
            header = ":param %s:" % (self.name,)
        else:
            header = ":param %s %s:" % (self.field_type, self.name)
        return header, self.doc

    def setup(self, name):
        self.name = name

    def present(self, obj):
        return self.name in obj._config_data

    def validate(self, obj):
        if self.required:
            if not self.present(obj):
                raise ConfigError(
                    "Missing required config field '%s'" % (self.name))
        # This will raise an exception if the value exists, but is invalid.
        self.get_value(obj)

    def raise_config_error(self, message_suffix):
        raise ConfigError("Field '%s' %s" % (self.name, message_suffix))

    def clean(self, value):
        return value

    def get_value(self, obj):
        value = obj._config_data.get(self.name, self.default)
        return self.clean(value) if value is not None else None

    def __get__(self, obj, cls):
        if obj is None:
            return self
        if obj.static and not self.static:
            self.raise_config_error("is not marked as static.")
        return self.get_value(obj)

    def __set__(self, obj, value):
        raise AttributeError("Config fields are read-only.")


class ConfigText(ConfigField):
    field_type = 'str'

    def clean(self, value):
        # XXX: We should really differentiate between "unicode" and "bytes".
        #      However, yaml.load() gives us bytestrings or unicode depending
        #      on the content.
        if not isinstance(value, basestring):
            self.raise_config_error("is not unicode.")
        return value


class ConfigInt(ConfigField):
    field_type = 'int'

    def clean(self, value):
        try:
            # We go via "str" to avoid silently truncating floats.
            # XXX: Is there a better way to do this?
            return int(str(value))
        except (ValueError, TypeError):
            self.raise_config_error("could not be converted to int.")


class ConfigFloat(ConfigField):
    field_type = 'float'

    def clean(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            self.raise_config_error("could not be converted to float.")


class ConfigBool(ConfigField):
    field_type = 'bool'

    def clean(self, value):
        if isinstance(value, basestring):
            return value.strip().lower() not in ('false', '0', '')
        return bool(value)


class ConfigList(ConfigField):
    field_type = 'list'

    def clean(self, value):
        if isinstance(value, tuple):
            value = list(value)
        if not isinstance(value, list):
            self.raise_config_error("is not a list.")
        return deepcopy(value)


class ConfigDict(ConfigField):
    field_type = 'dict'

    def clean(self, value):
        if not isinstance(value, dict):
            self.raise_config_error("is not a dict.")
        return deepcopy(value)


class ConfigUrl(ConfigField):
    field_type = 'URL'

    def clean(self, value):
        if value is None:
            return None
        if not isinstance(value, basestring):
            self.raise_config_error("is not a URL string.")
        # URLs must be bytes, not unicode.
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return urlparse.urlparse(value)


class ConfigRegex(ConfigText):
    field_type = 'regex'

    def clean(self, value):
        value = super(ConfigRegex, self).clean(value)
        return re.compile(value)


def generate_doc(cls, fields, header_indent='', indent=' ' * 4):
    """
    Generate a docstring for a cls and its fields.
    """
    cls_doc = cls.__doc__ or ''
    doc = cls_doc.split("\n")
    if doc and doc[-1].strip():
        doc.append("")
    doc.append("Configuration options:")
    for field in fields:
        header, field_doc = field.get_doc()
        doc.append("")
        doc.append(header_indent + header)
        doc.append("")
        doc.extend(textwrap.wrap(field_doc, initial_indent=indent,
                                 subsequent_indent=indent))
    return "\n".join(doc)


class ConfigMetaClass(type):
    def __new__(mcs, name, bases, dict):
        # locate Field instances
        fields = []
        unified_class_dict = {}
        for base in bases:
            unified_class_dict.update(inspect.getmembers(base))
        unified_class_dict.update(dict)

        for key, possible_field in unified_class_dict.items():
            if isinstance(possible_field, ConfigField):
                fields.append(possible_field)
                possible_field.setup(key)

        fields.sort(key=lambda f: f.creation_order)
        dict['fields'] = fields
        cls = type.__new__(mcs, name, bases, dict)
        cls.__doc__ = generate_doc(cls, fields)
        return cls


class Config(object):
    """
    Config object.
    """

    __metaclass__ = ConfigMetaClass

    def __init__(self, config_data, static=False):
        self._config_data = IConfigData(config_data)
        self.static = static
        for field in self.fields:
            if self.static and not field.static:
                # Skip non-static fields on static configs.
                continue
            field.validate(self)
        self.post_validate()

    def raise_config_error(self, message):
        """
        Raise a :class:`ConfigError` with the given message.
        """
        raise ConfigError(message)

    def post_validate(self):
        """
        Subclasses may override this to provide cross-field validation.

        Implementations should raise :class:`ConfigError` if the configuration
        is invalid (by calling :meth:`raise_config_error`, for example).
        """
        pass
