#!/usr/bin/python
# -*- coding: utf-8 -*-

# pylint: disable=C0111

# Copyright (c) 2012 Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

import logging

from django.utils.translation import ugettext as _

from dbfpy import dbf

from lizard_esf.export_dbf import DBFExporterToDict
from lizard_esf.export_dbf import DbfFile

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

    def __init__(self):
        self.get_candidate_config_as_dict = AreaConfigDbf().as_dict
        self.get_current_config_as_dict = ESFConfig().as_dict

    def compare(self, config):
        """Return the differences for the given configuration."""
        candidate = self.get_candidate_config_as_dict(config)
        current = self.get_current_config_as_dict(config)
        diff = Diff()
        for area_ident, area_attrs in candidate.items():
            try:
                current_attrs = current[area_ident]
            except KeyError:
                diff.new_areas.append(area_ident)
                continue
            for attr_name, attr_value in area_attrs.items():
                current_attr_value = current_attrs.get(attr_name, _('not present'))
                if attr_value != current_attr_value:
                    diff_for_key = diff.changed_areas.setdefault(area_ident, {})
                    diff_for_key[attr_name] = (attr_value, current_attr_value)
        return diff

    def get_candidate_config_as_dict(self, config):
        pass

    def get_current_config_as_dict(self, config):
        pass


class AreaConfigDbf(object):
    """Implements the retrieval of the area records of a configuration."""

    def as_dict(self, config):
        """Return the dict of area records from the given configuration.

        The dict maps the value of the GAFIDENT field of each area record to
        each record.

        """
        result = {}
        for record in self.retrieve_records(config):
            try:
                result[record['GAFIDENT']] = record
            except KeyError:
                logger.warning("area configuration file '%s' does not have a "
                               "GAFIDENT field", config.area_dbf)
                break
        return result

    def retrieve_records(self, config):
        """Return the list of records from the given configuration.

        Each record is specified as a dict from attribute name to attribute
        value.

        """
        records = []
        try:
            records = [rec.asDict() for rec in dbf.Dbf(config.area_dbf)]
        except IOError:
            logger.warning("area configuration file '%s' does not exist",
                           config.area_dbf)
        return records



class ESFConfig(AreaConfigDbf):

    def retrieve_records(self, config):
        """Return the list of records from the given configuration.

        Each record is specified as a dict from attribute name to attribute
        value.

        """
        exporter = DBFExporterToDict()
        dbf_file = DbfFile.objects.get(name=config.config_type)
        exporter.export_esf_configurations(config.data_set, "don't care",
            dbf_file, "don't care")
        return exporter.out
