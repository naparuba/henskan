#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for image splitting (manga double pages)
"""
import os
import sys

from PIL import Image as PILImage

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase
from henskan import image


class TestImageSplitting(ImageTestBase):
    """Tests for image splitting (manga double pages)"""
    
    
    def test_split_left_basic(self, test_images_dir):
        """Test splitting left half of a double page"""
        img_path = self.get_test_image_path(test_images_dir, "manga_scan_double_page.jpg")
        img = PILImage.open(img_path)
        original_width, original_height = img.size
        
        left_img = image._split_left(img)
        assert left_img is not None
        assert left_img.size == (original_width // 2, original_height)
    
    
    def test_split_right_basic(self, test_images_dir):
        """Test splitting right half of a double page"""
        img_path = self.get_test_image_path(test_images_dir, "manga_scan_double_page.jpg")
        img = PILImage.open(img_path)
        original_width, original_height = img.size
        
        right_img = image._split_right(img)
        assert right_img is not None
        assert right_img.size == (original_width // 2, original_height)
    
    
    def test_split_double_page_creates_two_images(self, test_images_dir):
        """Test that splitting creates two separate images"""
        img_path = self.get_test_image_path(test_images_dir, "manga_scan_double_page.jpg")
        img = PILImage.open(img_path)
        
        left_img = image._split_left(img)
        right_img = image._split_right(img)
        
        # Les deux moitiés devraient avoir la même hauteur
        assert left_img.size[1] == right_img.size[1]
        # Et la somme des largeurs devrait être égale à l'original
        assert left_img.size[0] + right_img.size[0] == img.size[0]
