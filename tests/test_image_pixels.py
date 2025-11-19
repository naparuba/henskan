#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for pixel-level operations
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase
from henskan import image


class TestPixelOperations(ImageTestBase):
    """Tests for pixel-level operations"""
    
    
    def test_is_quite_black_pure_black(self):
        """Test detection of pure black pixel"""
        black = (0, 0, 0)
        assert image._is_quite_black(black) == True
    
    
    def test_is_quite_black_dark_gray(self):
        """Test detection of dark gray pixel (within threshold)"""
        dark_gray = (20, 20, 20)  # < QUITE_BLACK_LIMIT (25)
        assert image._is_quite_black(dark_gray) == True
    
    
    def test_is_quite_black_not_black(self):
        """Test that medium gray is not considered black"""
        medium_gray = (50, 50, 50)  # > QUITE_BLACK_LIMIT (25)
        assert image._is_quite_black(medium_gray) == False
    
    
    def test_is_quite_white_pure_white(self):
        """Test detection of pure white pixel"""
        white = (255, 255, 255)
        assert image._is_quite_white(white) == True
    
    
    def test_is_quite_white_light_gray(self):
        """Test detection of light gray pixel (within threshold)"""
        light_gray = (240, 240, 240)  # >= 255 - 25
        assert image._is_quite_white(light_gray) == True
    
    
    def test_is_quite_white_not_white(self):
        """Test that medium gray is not considered white"""
        medium_gray = (200, 200, 200)  # < 255 - 25
        assert image._is_quite_white(medium_gray) == False
    
    
    def test_is_background_pixel_white_background(self):
        """Test background detection with white background"""
        white = (255, 255, 255)
        assert image._is_background_pixel(white, is_black_background=False) == True
        
        light_gray = (250, 250, 250)
        assert image._is_background_pixel(light_gray, is_black_background=False) == True
    
    
    def test_is_background_pixel_black_background(self):
        """Test background detection with black background"""
        black = (0, 0, 0)
        assert image._is_background_pixel(black, is_black_background=True) == True
        
        dark_gray = (5, 5, 5)
        assert image._is_background_pixel(dark_gray, is_black_background=True) == True
    
    
    def test_detect_pixel_category_comprehensive(self):
        """Test comprehensive pixel category detection"""
        # White
        assert image._detect_pixel_category((255, 255, 255)) == image.PIXEL_CATEGORY.WHITE
        
        # Black
        assert image._detect_pixel_category((0, 0, 0)) == image.PIXEL_CATEGORY.BLACK
        
        # Grey (all values equal)
        assert image._detect_pixel_category((128, 128, 128)) == image.PIXEL_CATEGORY.GREY
        
        # Almost grey (diff < 10)
        assert image._detect_pixel_category((100, 105, 102)) == image.PIXEL_CATEGORY.GREY
        assert image._detect_pixel_category((50, 55, 58)) == image.PIXEL_CATEGORY.GREY
        
        # Colors (diff >= 10)
        assert image._detect_pixel_category((255, 0, 0)) == image.PIXEL_CATEGORY.OTHER
        assert image._detect_pixel_category((0, 255, 0)) == image.PIXEL_CATEGORY.OTHER
        assert image._detect_pixel_category((0, 0, 255)) == image.PIXEL_CATEGORY.OTHER
        assert image._detect_pixel_category((150, 200, 100)) == image.PIXEL_CATEGORY.OTHER
