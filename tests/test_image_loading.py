#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for image loading and basic operations
"""
import os
import sys

import pytest
from PIL import Image as PILImage

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase


class TestImageLoading(ImageTestBase):
    """Tests for image loading and basic operations"""
    
    
    def test_load_image_manga_full_page(self, test_images_dir):
        """Test loading a simple manga page"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        img = PILImage.open(img_path)
        assert img is not None
        assert img.size == (800, 1200)
    
    
    def test_load_image_webtoon(self, test_images_dir):
        """Test loading a webtoon image"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_lot_of_white.jpg")
        img = PILImage.open(img_path)
        assert img is not None
        assert img.size == (720, 5342)
    
    
    def test_load_all_test_images(self, test_images_dir):
        """Test that all test images can be loaded"""
        jpg_files = [f for f in os.listdir(test_images_dir) if f.endswith('.jpg')]
        
        for filename in jpg_files:
            img_path = self.get_test_image_path(test_images_dir, filename)
            try:
                img = PILImage.open(img_path)
                assert img is not None, f"Failed to load {filename}"
                assert img.size[0] > 0 and img.size[1] > 0, f"Invalid size for {filename}"
            except Exception as e:
                pytest.fail(f"Failed to load {filename}: {e}")
