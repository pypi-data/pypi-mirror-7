"""This module provides config-file -> object mapping functionality."""


import ConfigParser
import os


class Bunch(object):
    """Simple bag-of-properties class."""

    def __repr__(self):
        clsname = self.__class__.__name__
        attribs = ', '.join('%s:%s' % kv for kv in self.__dict__.iteritems())
        return '({attribs})'.format(clsname=clsname, attribs=attribs)

    @classmethod
    def from_dict(cls, dictionary):
        """Factory method to create a Bunch from a dictionary.

        Args:
            dictionary (dict): The dictionary of attribute-(name,value) pairs
                to set on the Bunch.

        Returns:
            Bunch: A Bunch where Bunch.k = v for all (k,v) in dictionary.

        Examples:
            >>> bunch = Bunch.from_dict({'foo': 1})
            >>> bunch.foo
            1

        """
        bunch = Bunch()
        for key, value in dictionary.iteritems():
            setattr(bunch, key, value)
        return bunch

    @classmethod
    def from_instance(cls, instance, attribute):
        """Factory method to create a Bunch copying an object's attribute.

        Args:
            instance (object): The object to copy from.
            attribute (str): The attribute to copy.

        Returns:
            Bunch: A Bunch copying instance.attribute (or an empty Bunch if
                instance has no such attribute).

        """
        return (Bunch() if not hasattr(instance, attribute)
                else Bunch.from_dict(getattr(instance, attribute).__dict__))


class ConfigMapping(object):
    """Object to config-file mapping class."""

    class Section(Bunch):
        """Object representing a section in the config file/mapping."""
        pass

    @classmethod
    def from_config(cls, path):
        """Factory method to create a ConfigMapping from a config-file.

        Args:
            path (str): The path of the config-file to read.

        Returns:
            ConfigMapping: An object reflecting the values in the config-file.

        Raises:
            IOError: If `path` does not exist

        """
        if not os.path.isfile(path):
            raise IOError('File %s does not exist' % path)

        config = ConfigParser.SafeConfigParser()
        config.read(path)
        instance = cls()
        new_section = ConfigMapping.Section.from_instance
        for section_name in config.sections():
            section_obj = new_section(instance, section_name)
            for option_name in config.options(section_name):
                option_value = config.get(section_name, option_name)
                setattr(section_obj, option_name, option_value)
            setattr(instance, section_name, section_obj)
        return instance

    def write_config(self, path):
        """Dumps the ConfigMapping object to a config-file on disk.

        Args:
            path (str): The location to which to write the config-file.

        """
        config = ConfigParser.SafeConfigParser()
        for section_name, section_obj in self.__dict__.iteritems():
            opts = [kv for kv in section_obj.__dict__.iteritems()
                    if kv[1] is not None]
            if len(opts) > 0:
                config.add_section(section_name)
                for option_name, value in opts:
                    config.set(section_name, option_name, str(value))
        with open(path, 'wb') as configfile:
            config.write(configfile)

    def merge(self, other):
        """Updates the ConfigMapping object with the sections from another
        ConfigMapping. If any sections and options therein are shared between
        the two objects, the option-values from the other ConfigMapping object
        are kept.

        Args:
            other (ConfigMapping): The ConfigMapping to merge with.

        """
        if not isinstance(other, ConfigMapping):
            raise ValueError('can not merge {cls} with non-{cls} object'
                             .format(cls=self.__class__.__name__))

        own_sections, other_sections = self.__dict__, other.__dict__
        for section_name, other_section in other_sections.iteritems():
            if section_name not in own_sections:
                setattr(self, section_name, other_section)
            else:
                own_section = own_sections[section_name]
                own_section.__dict__.update(other_section.__dict__)

    def __repr__(self):
        clsname = self.__class__.__name__
        attr = ', '.join('%s=%s' % kv for kv in self.__dict__.iteritems())
        return '{clsname}({attr})'.format(clsname=clsname, attr=attr)
