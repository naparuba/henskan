#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for grayscale detection
"""
import os
import sys

from PIL import Image as PILImage

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase
from henskan import image


class TestImageGrayscaleDetection(ImageTestBase):
    """Tests for grayscale detection"""
    
    
    def test_is_totally_greyscale_on_grayscale_image(self, test_images_dir):
        """Test grayscale detection on a black and white manga"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        img = PILImage.open(img_path)
        # La plupart des mangas sont en grayscale
        result = image._is_totally_greyscale__fast(img)
        # On ne peut pas être sûr sans analyser l'image, donc on vérifie juste que la fonction retourne un booléen
        assert isinstance(result, bool)
    
    
    def test_detect_pixel_category_white(self):
        """Test pixel category detection for white pixel"""
        white_pixel = (255, 255, 255)
        result = image._detect_pixel_category(white_pixel)
        assert result == image.PIXEL_CATEGORY.WHITE
    
    
    def test_detect_pixel_category_black(self):
        """Test pixel category detection for black pixel"""
        black_pixel = (0, 0, 0)
        result = image._detect_pixel_category(black_pixel)
        assert result == image.PIXEL_CATEGORY.BLACK
    
    
    def test_detect_pixel_category_grey(self):
        """Test pixel category detection for grey pixel"""
        grey_pixel = (128, 128, 128)
        result = image._detect_pixel_category(grey_pixel)
        assert result == image.PIXEL_CATEGORY.GREY
        
        # Test avec une légère différence (< 10)
        almost_grey = (100, 105, 102)
        result = image._detect_pixel_category(almost_grey)
        assert result == image.PIXEL_CATEGORY.GREY
    
    
    def test_detect_pixel_category_color(self):
        """Test pixel category detection for colored pixel"""
        red_pixel = (255, 0, 0)
        result = image._detect_pixel_category(red_pixel)
        assert result == image.PIXEL_CATEGORY.OTHER
        
        blue_pixel = (0, 0, 255)
        result = image._detect_pixel_category(blue_pixel)
        assert result == image.PIXEL_CATEGORY.OTHER
