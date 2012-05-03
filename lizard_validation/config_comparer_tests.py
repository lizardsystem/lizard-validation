#!/usr/bin/python
# -*- coding: utf-8 -*-

# pylint: disable=C0111

# Copyright (c) 2012 Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

import logging

from unittest import TestCase

from django.utils.translation import ugettext as _

from mock import Mock

from lizard_area.models import Area
from lizard_portal.configurations_retriever import ConfigurationToValidate
from lizard_validation.config_comparer import AreaConfigDbf
from lizard_validation.config_comparer import ConfigComparer

logger = logging.getLogger(__name__)


class ConfigComparerTestSuite(TestCase):

    def test_a(self):
        """Test the difference of a single attribute.

        The attribute is present in both configurations but with different
        values.

        """
        comparer = self.create_comparer({'DIEPTE': '1.17'}, {'DIEPTE': '1.18'})

        diff = comparer.compare(ConfigurationToValidate())
        self.assertEqual({'DIEPTE': ('1.17', '1.18')}, diff)

    def create_comparer(self, new_attrs, current_attrs):
        comparer = ConfigComparer()
        comparer.get_new_attrs = lambda c: new_attrs
        comparer.get_current_attrs = lambda c: current_attrs
        return comparer

    def test_b(self):
        """Test the difference of a single attribute.

        The attribute is only present in the new configuration.

        """
        comparer = self.create_comparer({'DIEPTE': '1.17'}, {})

        diff = comparer.compare(ConfigurationToValidate())
        self.assertEqual({'DIEPTE': ('1.17', _('not present'))}, diff)

    def test_c(self):
        """Test the difference of a single attribute.

        The attribute is only present in the current configuration.

        """
        comparer = self.create_comparer({}, {'DIEPTE': '1.18'})

        diff = comparer.compare(ConfigurationToValidate())
        self.assertEqual({'DIEPTE': (_('not present'), '1.18')}, diff)

    def test_d(self):
        """Test the equality of a single field."""
        comparer = self.create_comparer({'DIEPTE': '1.17'}, {'DIEPTE': '1.17'})

        diff = comparer.compare(ConfigurationToValidate())
        self.assertEqual({}, diff)


class AreaConfigDbfTestSuite(TestCase):

    def setUp(self):
        self.config = ConfigurationToValidate()
        self.config.area = Area()
        self.config.area.ident = '3201'
        self.attrs_retriever = AreaConfigDbf()
        record = {'GAFIDENT': '3201', 'DIEPTE': ' 1.17'}
        self.attrs_retriever.retrieve_records = Mock(return_value=[record])

    def test_a(self):
        """Test the retrieval of a single record."""
        attrs = self.attrs_retriever.as_dict(self.config)
        self.assertEqual({'GAFIDENT': '3201', 'DIEPTE': ' 1.17'}, attrs)

    def test_b(self):
        """Test the retrieval of a single record of an unknown area."""
        self.config.area.ident = '3203'
        attrs = self.attrs_retriever.as_dict(self.config)
        self.assertEqual({}, attrs)

    def test_c(self):
        """Test the records are retrieved from the right file."""
        self.attrs_retriever.as_dict(self.config)
        args, kwargs = self.attrs_retriever.retrieve_records.call_args
        self.assertEqual(self.config, args[0])

    def test_d(self):
        """Test the retrieval of records without a GAFIDENT field."""
        record = {'DIEPTE': ' 1.17'}
        self.attrs_retriever.retrieve_records = Mock(return_value=[record])
        attrs = self.attrs_retriever.as_dict(self.config)
        self.assertEqual({}, attrs)
