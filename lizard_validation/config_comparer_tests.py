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
from lizard_validation.config_comparer import AreaConfig
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


class AreaConfigTestSuite(TestCase):

    def setUp(self):
        self.config = ConfigurationToValidate()
        self.config.area = Area()
        self.config.area.ident = '3201'
        self.attrs_retriever = AreaConfig()
        record = {'GAFIDENT': '3201', 'DIEPTE': ' 1.17'}
        dbf = Mock()
        dbf.get_records = lambda: [record]
        self.attrs_retriever.open_database = Mock(return_value=dbf)

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
        """Test the retrieval of records without a GAFIDENT field."""
        record = {'DIEPTE': ' 1.17'}
        dbf = Mock()
        dbf.get_records = lambda: [record]
        self.attrs_retriever.open_database = Mock(return_value=dbf)
        attrs = self.attrs_retriever.as_dict(self.config)
        self.assertEqual({}, attrs)

    def test_d(self):
        """Test the records are retrieved from the right file."""
        self.attrs_retriever.as_dict(self.config)
        args, kwargs = self.attrs_retriever.open_database.call_args
        self.assertEqual(self.config, args[0])

    def test_e(self):
        """Test the open DBF file is closed."""
        self.attrs_retriever.as_dict(self.config)
        mock_calls = self.attrs_retriever.open_database().mock_calls
        name, args, kwargs = mock_calls[-1]
        self.assertTrue('close' == name and () == args and {} == kwargs)
