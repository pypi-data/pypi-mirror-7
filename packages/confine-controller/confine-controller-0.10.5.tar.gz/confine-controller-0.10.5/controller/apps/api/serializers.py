import json
import six

from django.forms import widgets
from rest_framework import exceptions
from rest_framework.serializers import *

# CONFINE compatibility layer for DRF


class RelHyperlinkedRelatedField(HyperlinkedRelatedField):
    """ 
    HyperlinkedRelatedField field providing a relation object rather than flat URL 
    """
    def to_native(self, obj):
        """ 
        CONFINE specs to DRF compat
        converts from "http//example.org" to { "uri": "http://example.org" }
        """
        url = super(RelHyperlinkedRelatedField, self).to_native(obj)
        if url is None:
             return None
        return { 'uri': url }
    
    def from_native(self, value):
        """ 
        CONFINE specs to DRF compat
        converts from { "uri": "http://example.org" } to "http//example.org"
        """
        if isinstance(value, six.text_type):
            value = value.replace("u'", '"').replace("'", '"')
            try:
                value = json.loads(value)
            except ValueError:
                raise exceptions.ParseError("%s is not an object" % value)
        if isinstance(value, dict):
            value = value.pop('uri', None)
        else:
            raise exceptions.ParseError("%s is not an object" % value)
        return super(RelHyperlinkedRelatedField, self).from_native(value)


class UriHyperlinkedModelSerializer(HyperlinkedModelSerializer):
    """ 
    Like HyperlinkedModelSerializer but renaming url field to uri 
    """
    uri = Field()
    _hyperlink_field_class = RelHyperlinkedRelatedField
    

    def __init__(self, *args, **kwargs):
        """ url to uri renaming """
        super(UriHyperlinkedModelSerializer, self).__init__(*args, **kwargs)
        self.fields['uri'] = self.fields.pop('url', None)


class HyperlinkedFileField(FileField):
    """ display file url instead of file path """
    def to_native(self, value):
        if value:
            request = self.context.get('request')
            return request.build_absolute_uri(value.url)

class FieldWithDefault(WritableField):
    def __init__(self, default, *args, **kwargs):
        if default is None:
            raise TypeError("'default' is a mandatory argument")
        kwargs['required'] = False
        self.default = default
        super(FieldWithDefault, self).__init__(*args, **kwargs)
    
    def field_to_native(self, obj, field_name):
        value = super(FieldWithDefault, self).field_to_native(obj, field_name)
        if value is None:
            return self.default
        return value


class PropertyField(FieldWithDefault):
    """
    Dict-like representation of a Property Model
    A bit hacky, objects get deleted on from_native method and Serializer will
    need a custom override of restore_object method.
    """
    def to_native(self, value):
        """ dict-like representation of a Property Model"""
        return dict((prop.name, prop.value) for prop in value.all())
    
    def from_native(self, value):
        """ Convert a dict-like representation back to a Property Model """
        parent = self.parent
        related_manager = getattr(parent.object, self.source or 'properties', False)
        properties = []
        if value:
            model = getattr(parent.opts.model, self.source or 'properties').related.model
            if isinstance(value, basestring):
                try:
                    value = json.loads(value)
                except:
                    raise exceptions.ParseError("Malformed property: %s" % str(value))
            if not related_manager:
                # POST (new parent object)
                return [ model(name=n, value=v) for n,v in value.iteritems() ]
            # PUT
            to_save = []
            for (name, value) in value.iteritems():
                try:
                    # Update existing property
                    prop = related_manager.get(name=name)
                except model.DoesNotExist:
                    # Create a new one
                    prop = model(name=name, value=value)
                else:
                    prop.value = value
                    to_save.append(prop.pk)
                properties.append(prop)
        
        # Discart old values
        if related_manager:
            for obj in related_manager.all():
                if obj.pk not in to_save:
                    # TODO do it in serializer.save() self.object._deleted ?
                    obj.delete()
        return properties


class MultiSelectField(ChoiceField):
    widget = widgets.CheckboxSelectMultiple
    
    def field_from_native(self, data, files, field_name, into):
        """ convert multiselect data into comma separated string """
        if field_name in data:
            data = data.copy()
            try:
                # data is a querydict when using forms
                data[field_name] = ','.join(data.getlist(field_name))
            except AttributeError:
                data[field_name] = ','.join(data[field_name])
        return super(MultiSelectField, self).field_from_native(data, files, field_name, into)
    
    def valid_value(self, value):
        """ checks for each item if is a valid value """
        for val in value.split(','):
            valid = super(MultiSelectField, self).valid_value(val)
            if not valid:
                return False
        return True


class DynamicReadonlyFieldsModelSerializer(UriHyperlinkedModelSerializer):
    """
    Provides simple field level permissions, marking as readonly some
    fields defined on read_only_fields parameter.
    `read_only_fields` list or tuple of fields to be marked as readonly
    
    """
    def __init__(self, *args, **kwargs):
        ro_fields = kwargs.pop('read_only_fields', [])
        super(DynamicReadonlyFieldsModelSerializer, self).__init__(*args, **kwargs)
        for field_name in ro_fields:
            self.fields[field_name].read_only = True
 
