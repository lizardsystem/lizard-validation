#!/usr/bin/python
# -*- coding: utf-8 -*-

# pylint: disable=C0111

# Copyright (c) 2012 Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

import logging

from unittest import TestCase

from django.utils.translation import ugettext as tr

from mock import Mock

from lizard_portal.configurations_retriever import ConfigurationToValidate
from lizard_portal.config_comparer import AreaConfigDbf
from lizard_portal.config_comparer import ConfigComparer
from lizard_portal.config_comparer import Diff


logger = logging.getLogger(__name__)


class ConfigComparerTestSuite(TestCase):

    def test_a(self):
        """Test the difference of a single field.

        The field is present in both configurations but with different values.

        """
        config = ConfigurationToValidate()
        comparer = ConfigComparer()

        candidate_config = { '3201': { 'DIEPTE': '1.17' } }
        current_config = { '3201' : { 'DIEPTE': '1.18' } }
        comparer.get_candidate_config_as_dict = lambda s, c: candidate_config
        comparer.get_current_config_as_dict = lambda s, c: current_config

        diff = comparer.compare(config)
        expected_diff = Diff()
        expected_diff.changed_areas = {
            '3201': {
                'DIEPTE': ('1.17', '1.18'),
                }
            }
        self.assertEqual(expected_diff, diff)

    def test_b(self):
        """Test the difference of a single field.

        The field is present in only one configuration.

        """
        config = ConfigurationToValidate()
        comparer = ConfigComparer()

        candidate_config = { '3201': { 'DIEPTE': '1.17' } }
        current_config = { '3201' : {} }
        comparer.get_candidate_config_as_dict = lambda s, c: candidate_config
        comparer.get_current_config_as_dict = lambda s, c: current_config

        diff = comparer.compare(config)
        expected_diff = Diff()
        expected_diff.changed_areas = {
            '3201': {
                'DIEPTE': ('1.17', tr('not present')),
                }
            }
        self.assertEqual(expected_diff, diff)

    def test_c(self):
        """Test the difference of a single field.

        The field is present in only one configuration. The configuration is
        not yet present.

        """
        config = ConfigurationToValidate()
        comparer = ConfigComparer()

        candidate_config = { '3201': { 'DIEPTE': '1.17' } }
        current_config = { }
        comparer.get_candidate_config_as_dict = lambda s, c: candidate_config
        comparer.get_current_config_as_dict = lambda s, c: current_config

        diff = comparer.compare(config)
        expected_diff = Diff()
        expected_diff.new_areas = ['3201']
        self.assertEqual(expected_diff, diff)

    def test_d(self):
        """Test the equality of a single field."""
        config = ConfigurationToValidate()
        comparer = ConfigComparer()

        candidate_config = { '3201': { 'DIEPTE': '1.17' } }
        current_config = { '3201': { 'DIEPTE': '1.17' } }
        comparer.get_candidate_config_as_dict = lambda s, c: candidate_config
        comparer.get_current_config_as_dict = lambda s, c: current_config

        diff = comparer.compare(config)
        expected_diff = Diff()
        self.assertEqual(expected_diff, diff)


class AreaConfigDbfTestSuite(TestCase):

    def setUp(self):
        self.config = ConfigurationToValidate()
        self.config.config_type = 'esf1'
        self.config.file_path = '/path'
        self.area_dbf = AreaConfigDbf()
        record = {'GAFIDENT': '3201', 'DIEPTE': ' 1.17'}
        self.area_dbf.retrieve_records = Mock(return_value=[record])

    def test_a(self):
        """Test the retrieval of a single record."""
        area2attrs = self.area_dbf.as_dict(self.config)
        self.assertEqual({'3201': {'GAFIDENT': '3201', 'DIEPTE': ' 1.17'}}, area2attrs)

    def test_b(self):
        """Test the records are retrieved from the right file."""
        self.area_dbf.as_dict(self.config)
        args, kwargs = self.area_dbf.retrieve_records.call_args
        self.assertEqual(self.config, args[0])

    def test_c(self):
        """Test the retrieval of records without a GAFIDENT field."""
        self.area_dbf.retrieve_records = Mock(return_value=[{'DIEPTE': ' 1.17'}])
        area2attrs = self.area_dbf.as_dict(self.config)
        self.assertEqual(0, len(area2attrs))
