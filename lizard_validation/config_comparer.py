#!/usr/bin/python
# -*- coding: utf-8 -*-

# pylint: disable=C0111

# Copyright (c) 2012 Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

import logging

from django.utils.translation import ugettext as _

from dbfpy import dbf

from lizard_esf.export_dbf import DBFExporterToDict
from lizard_esf.export_dbf import DbfFile
from lizard_wbconfiguration.export_dbf import WbExporterToDict

logger = logging.getLogger(__name__)


class Diff(object):
    """Describes the differences between new and current configurations.

    Instance parameters:
      *new_areas*
         list of area identifications only specified in the new configurations
      *changed_areas*
         dict of area identification to attribute name to tuple of new and
         current attribute values

    """
    def __init__(self):
        self.new_areas = []
        self.changed_areas = {}

    def __eq__(self, other):
        return self.new_areas == other.new_areas and \
            self.changed_areas == other.changed_areas


class ConfigComparer(object):
    """Implements the functionality to compare two ESF configurations.

    One of the ESF configurations, the 'new' one, is retrieved from a DBF
    file. The other ESF configuration, the 'current' one, is retrieved from the
    Django database.

    """
    def __init__(self):
        tmp = AreaConfig()
        tmp.open_database = lambda config: DbfWrapper(config.area_dbf)
        self.get_new_attrs = tmp.as_dict

        tmp = AreaConfig()
        tmp.open_database = lambda config: DatabaseWrapper(config)
        self.get_current_attrs = tmp.as_dict

    def compare(self, config):
        """Return the dict of differences for the given configuration.

        The dict maps attribute names to a tuple of two values: the first value
        specifies the new attribute value, the second value specifies the
        current attribute value.

        """
        new_attrs = self.get_new_attrs(config)
        print new_attrs
        current_attrs = self.get_current_attrs(config)
        diff = {}
        for new_attr_name, new_attr_value in new_attrs.items():
            current_attr_value = current_attrs.get(new_attr_name, _('not present'))
            if new_attr_value != current_attr_value:
                diff[new_attr_name] = \
                    (new_attr_value, current_attr_value)
        for current_attr_name, current_attr_value in current_attrs.items():
            if current_attr_name not in new_attrs.keys():
                diff[current_attr_name] = (_('not present'), current_attr_value)
        return diff

    def get_new_attrs(self, config):
        """Return the dict of attributes of the new configuration.

        The new configuration is stored in a DBF file which is specified by the
        config parameter, which is a ConfigurationToValidate.

        This method is not implemented here and should be set through
        dependency injection.

        """
        pass

    def get_current_attrs(self, config):
        """Return the dict of attributes of the current configuration.

        The current configuration is stored in the Django database.

        This method is not implemented here and should be set through
        dependency injection.

        """
        pass


class AreaConfig(object):
    """Implements the retrieval of the area record of a configuration."""

    def as_dict(self, config):
        """Return the area attributes of the specified configuration."""
        attrs = {}
        try:
            open_dbf = self.open_database(config)
            for record in open_dbf.get_records():
                try:
                    if record['GAFIDENT'] == config.area.ident:
                        attrs = record
                        break
                except KeyError:
                    logger.warning("area configuration file '%s' does not have "
                                   "a GAFIDENT field", config.area_dbf)
                    break
            open_dbf.close()
        except IOError:
            logger.warning("area configuration file '%s' does not exist",
                           config.area_dbf)
        if attrs == {}:
            logger.warning("area configuration file '%s' does not have a "
                           "%s configuration for area '%s' (%s)",
                           config.area_dbf,
                           config.config_type,
                           config.area.name,
                           config.area.ident)
        return attrs

    def open_database(self, config):
        """Return an interface to the open database for the given configuration.

        This method is not implemented here and should be set through
        dependency injection.

        """
        pass


class DbfWrapper(object):
    """Implements the retrieval of the records of a single DBF."""

    def __init__(self, file_name):
        """Open the DBF whose records should be retrieved."""
        self.dbf = dbf.Dbf(file_name)

    def close(self):
        """Close the DBF."""
        self.dbf.close()

    def get_records(self):
        """Return the records of the open DBF.

        This method returns each record as a dict that maps attribute name to
        attribute value.

        """
        for record in self.dbf:
            yield record.asDict()


class DatabaseWrapper(object):
    """Implements the retrieval of the ESF records from the Django database."""

    def __init__(self, config):
        """Set the configuration whose ESF records should be retrieved."""
        self.config = config

    def close(self):
        pass

    def get_records(self):
        """Return the records from the given configuration.

        This method returns each record as a dict that maps attribute name to
        attribute value.

        """
        exporter = DBFExporterToDict()
        dbf_file = DbfFile.objects.get(name=self.config.config_type)
        exporter.export_esf_configurations(self.config.data_set, "don't care",
            dbf_file, "don't care")
        return exporter.out

class WaterbalanceFromDatabaseRetriever(object):
    """Implements the retrieval of the aan-/afvoer records from the Django database."""

    def __init__(self, config):
        """Set the configuration whose waterbalance aan-/afvoer records should
        be retrieved."""
        self.config = config

    def close(self):
        pass

    def get_records(self):
        """Return the records from the given configuration.

        This method returns each record as a dict that maps attribute name to
        attribute value.

        """
        exporter = WbExporterToDict()
        exporter.export_areaconfiguration(self.config.data_set, "don't care",
            "don't care")
        print exporter
        return exporter.out


def create_wb_comparer():
    comparer = ConfigComparer()
    tmp = AreaConfig()
    tmp.open_database = lambda config: WaterbalanceFromDatabaseRetriever(config)
    comparer.get_current_attrs = tmp.as_dict
    return comparer
