#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for e-reader device profiles
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase
from henskan import image


class TestEReaderProfiles(ImageTestBase):
    """Tests for e-reader device profiles"""
    
    
    def test_get_size_kindle(self):
        """Test getting Kindle device size"""
        size = image.EReaderData.get_size('Kindle Paperwhite 3/Voyage/Oasis')
        assert size == (1072, 1448)
    
    
    def test_get_size_kobo(self):
        """Test getting Kobo device size"""
        size = image.EReaderData.get_size('Kobo Aura H2O')
        assert size == (1080, 1430)
    
    
    def test_get_palette_kindle(self):
        """Test getting Kindle palette"""
        palette = image.EReaderData.get_palette('Kindle 1')
        assert palette == image.Palette4
    
    
    def test_get_palette_kobo(self):
        """Test getting Kobo palette"""
        palette = image.EReaderData.get_palette('Kobo Aura HD')
        assert palette == image.Palette16
    
    
    def test_get_archive_format_kindle(self):
        """Test that Kindle uses PDF format"""
        from henskan.archive import ARCHIVE_FORMATS
        fmt = image.EReaderData.get_archive_format('Kindle Paperwhite 1 & 2')
        assert fmt == ARCHIVE_FORMATS.PDF
    
    
    def test_get_archive_format_kobo(self):
        """Test that Kobo uses CBZ format"""
        from henskan.archive import ARCHIVE_FORMATS
        fmt = image.EReaderData.get_archive_format('Kobo Glo HD')
        assert fmt == ARCHIVE_FORMATS.CBZ
    
    
    def test_is_device_exists_valid(self):
        """Test device exists check with valid device"""
        assert image.EReaderData.is_device_exists('Kindle Paperwhite 3/Voyage/Oasis')
        assert image.EReaderData.is_device_exists('Kobo Aura H2O')
    
    
    def test_is_device_exists_invalid(self):
        """Test device exists check with invalid device"""
        assert not image.EReaderData.is_device_exists('Invalid Device')
        assert not image.EReaderData.is_device_exists('')
    
    
    def test_all_devices_have_required_data(self):
        """Test that all devices have size, palette and format"""
        for device_name, device_data in image.EReaderData.Profiles.items():
            # Each device should have (size, palette, format)
            assert len(device_data) == 3, f"{device_name} should have 3 elements"
            
            size = device_data[0]
            assert isinstance(size, tuple) and len(size) == 2
            assert size[0] > 0 and size[1] > 0
            
            palette = device_data[1]
            assert isinstance(palette, list) or isinstance(palette, type(image.Palette4))
            
            archive_format = device_data[2]
            from henskan.archive import ARCHIVE_FORMATS
            assert isinstance(archive_format, ARCHIVE_FORMATS)
