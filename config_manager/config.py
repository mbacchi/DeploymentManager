#!/usr/bin/env python

# Copyright 2009-2014 Eucalyptus Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
from pprint import pformat
from shutil import copyfile
import difflib

class JsonMapping(object):
    def __init__(self, json_name, configmanager, value=None, validate=None):
        assert isinstance(configmanager, Config)
        self.configmanager = configmanager
        self.name = json_name
        if validate:
            self.validate = validate
        self.set(value)
        self.__doc__ = "Mapping to allow json property: {0} manipulation"\
            .format(json_name)

    def set(self, value):
        if value is None:
            return self.configmanager._del_json_property(self.name)
        return self.configmanager._set_json_property(self.name, value)

    def get(self):
        return self.configmanager._get_json_property(self.name)

    def delete(self):
        self.configmanager._del_json_property(self.name)

    def validate(self, value):
        pass

    def reset(self):
        pass


class Config(object):
    """
    Intention of this class is to provide utilities around reading and writing
    CLI environment related configuration.
    """
    def __init__(self,
                 name,
                 description=None,
                 config_file_path=None,
                 objtype=None,
                 version=None):
        """
        Creates a base Config() object. This object is a basic python
        representation of a textual configuration(file). This configuration
        is currently described using JSON. This class provides utilities to
        read, write, map, save, compare, and validate python attributes to a
        json configuration.
        :param name: string. The name of this config section
        :param config_file_path: Optional.string. Local path this config obj
                                 should read/write
        :param type: Optional. string. Identifier for this config object.
        :param version: Optional. string. can be used to version a config
        :param kwargs: Optional set of key word args which will be passed to
                       to the local user defined _setup() method.
        """
        # Set name and config file path first to allow updating base values
        # from an existing file
        self._json_properties = {}
        # Set name and config file path first to allow updating base values
        # from an existing file
        name = name
        if not name:
            name = self.__class__.__name__.lower()

        self.default_attributes = {}
        #Now overwrite with any params provided
        self.name = JsonMapping(json_name=)
        self.objtype = self.create_prop('objtype', self.__class__.__name__)
        self.version = self.create_prop('version', version)
        self.description = self.create_prop('description', description)

        self.config_file_path = config_file_path
        self.update_from_file()
        self.default_attributes = {}

    def _get_json_property(self, property_name):
        """
        helper method for mapping json to python properties
        """
        return self._json_properties[property_name]

    def _set_json_property(self, property_name, value):
        """
        helper method for mapping json to python properties
        """
        self._json_properties[property_name] = value

    def _del_json_property(self, property_name):
        """
        helper method for mapping json to python properties
        """
        if property_name in self._json_properties:
            self._json_properties.pop(property_name)

    def __repr__(self):
        """
        Default string representation of this object will be the formatted
        json configuration
        """
        buf = ""
        for key in self.__dict__:
            buf += "{0}  ---> {1}\n".format(key, self.__dict__[key])
        buf += "json:\n{0}".format(self.to_json())
        return buf

    def del_prop(self, property_name):
        prop = getattr(self, property_name, None)
        if not hasattr(prop, 'fdel'):
            raise ValueError('{0} is not a property of this object'
                             .format(property_name))
        if prop:
            prop.fdel(self)
            self.__delattr__(property_name)

    def get_attr_by_json_name(self, json_name):
        for key in self._get_keys():
            attr = getattr(self, key)
            if hasattr(attr, 'fget') and attr.fget() == json_name:
                return attr
        return None

    #todo define how validation methods for each config subclass should be used
    def validate(self):
        """
        Method to validate configuration. This would likely be checks
        against the aggregate config as individual validation checks
        should be done in each property's setter via the validation_callback
        """
        pass

    def to_json(self):
        """
        converts the local dict '_json_properties{} to json
        """
        return json.dumps(self,
                          default=lambda o: o._json_properties,
                          sort_keys=True,
                          indent=4)

    def _get_formatted_conf(self):
        return pformat(vars(self))

    def _get_keys(self):
        return vars(self).keys()

    def _get_dict_from_file(self, file_path=None):
        """
        Attempts to read in json from an existing file, load and return as
        a dict
        """
        file_path = file_path or self.config_file_path
        newdict = None
        if os.path.exists(str(file_path)) and os.path.getsize(str(file_path)):
            if not os.path.isfile(file_path):
                raise ValueError('config file exists at path and is not '
                                 'a file:' + str(file_path))
            conf_file = open(file_path, 'rb')
            with conf_file:
                data = conf_file.read()
            if data:
                try:
                    newdict = json.loads(data)
                except ValueError as ve:
                    ve.args = (['Failed to load json config from: "{0}". '
                                'ERR: "{1}"'.format(file_path, ve.message)])
                    raise
        return newdict

    def update_from_file(self, file_path=None):
        file_path = file_path or self.config_file_path
        if not file_path:
            return
        newdict = self._get_dict_from_file(file_path=file_path)
        if newdict:
            for key in newdict:
                value = newdict[key]
                if not key in self._json_properties:
                    print ('warning "{0}" not found in json properties for '
                           'class: "{1}"'.format(key, self.__class__))
                else:
                    attr = self.get_attr_by_json_name(key)
                    if not attr:
                        print 'warning local attribute with json_name "{0}" ' \
                              'not found'.format(key)
                    else:
                        attr.fset(value)

    #todo define how/if this method should be used, examples, etc..
    def send(self, filehandle=None):
        """
        Method which defines how, where, when etc a config should be written.
        For writing to a local path use self.save(), this method is a
        placeholder for possibly writing to a remote server, or submitting
        the json configuration to another process, etc..
        """
        pass

    def diff(self, file_path=None):
        """
        Method to show current values vs those (saved) in a file.
        Will return a formatted string to show the difference
        """
        #Create formatted string representation of dict values
        text1 = self.to_json().splitlines()
        #Create formatted string representation of values in file
        file_path = file_path or self.config_file_path
        file_dict = self._get_dict_from_file(file_path=file_path) or {}
        text2 = json.dumps(file_dict, sort_keys=True, indent=4).splitlines()
        diff = difflib.unified_diff(text2, text1, lineterm='')
        return str('\n'.join(diff))

    def save(self, path=None):
        """
        Will write the json configuration to a file at path or by default at
        self.config_file_path.
        """
        path = path or self.config_file_path
        if not path:
            raise ValueError('Path/config_file_path has not been set '
                             'or provided.')
        backup_path = path + '.bak'
        config_json = self.to_json()
        if os.path.isfile(path):
            copyfile(path, backup_path)
        save_file = file(path, "w")
        with save_file:
            save_file.write(config_json)
            save_file.flush()



    def add_config(self, service_config):
        self.default_attributes.update(
            {service_config.__class__.__name__.lower(): service_config}
        )

    def to_dict(self):
        return dict(name=self.name,
                    description=self.description,
                    default_attributes=self.default_attributes)


class DMJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        else:
            return json.JSONEncoder.default(self, obj)

