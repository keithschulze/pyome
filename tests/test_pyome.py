#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pyome
----------------------------------

Tests for `pyome` module.
"""

from __future__ import absolute_import

import unittest
import bioformats

import pyome as ome


class TestPyome(unittest.TestCase):

    def setUp(self):
        self.dv = "tests/data/decon.ome.xml"

    def test_000_omexml(self):
        m = bioformats.get_omexml_metadata(self.dv).encode('UTF-8')
        self.assertEqual(ome.read(self.dv).xml, m)

    def test_001_series_count(self):
        self.assertEqual(len(ome.read(self.dv)), 1)

    def test_002_id(self):
        self.assertEqual(next(ome.read(self.dv)).id, "Image:0")

    def test_003_name(self):
        self.assertEqual(next(ome.read(self.dv)).name, "decon.dv")

    def test_004_pixel_type(self):
        self.assertEqual(next(ome.read(self.dv)).pixel_type, "uint16")

    def test_005_size_x(self):
        self.assertEqual(next(ome.read(self.dv)).sizex, 960)

    def test_006_as_dict(self):
        s1_meta = next(ome.read(self.dv))
        s1_meta_dict = s1_meta._asdict()
        self.assertIsInstance(s1_meta_dict, dict)
        self.assertEqual(s1_meta_dict['id'], s1_meta.id)
        self.assertEqual(s1_meta_dict['name'], s1_meta.name)

        s1_meta_dict_ch = s1_meta_dict['channels']
        self.assertIsInstance(s1_meta_dict_ch, list)
        self.assertEqual(s1_meta_dict_ch[0]['id'], s1_meta.channels[0].id)
