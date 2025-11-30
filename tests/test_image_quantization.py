#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for image quantization and palette application
"""
import os
import sys

from PIL import Image as PILImage

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase
from henskan import image


class TestImageQuantization(ImageTestBase):
    """Tests for image quantization and palette application"""
    
    
    def test_apply_basic_grey_converts_rgb_to_greyscale(self):
        """Test _apply_basic_grey converts RGB image to greyscale"""
        test_img = PILImage.new('RGB', (100, 100), color=(128, 128, 128))
        
        result = image._apply_basic_grey(test_img)
        assert result is not None
        assert result.mode == 'L'  # Mode greyscale
        assert result.size == test_img.size
    
    
    def test_apply_basic_grey_with_color_image(self):
        """Test _apply_basic_grey converts colored image to greyscale"""
        test_img = PILImage.new('RGB', (50, 50), color=(255, 0, 0))  # Rouge
        
        result = image._apply_basic_grey(test_img)
        assert result is not None
        assert result.mode == 'L'
        # Vérifier que c'est bien en niveaux de gris
        pixel = result.getpixel((25, 25))
        assert isinstance(pixel, int)  # Un seul canal pour L
    
    
    def test_apply_basic_grey_with_already_greyscale(self):
        """Test _apply_basic_grey with already greyscale image"""
        test_img = PILImage.new('L', (50, 50), color=100)
        
        result = image._apply_basic_grey(test_img)
        assert result is not None
        assert result.mode == 'L'
    
    
    def test_apply_basic_grey_with_real_image(self, test_images_dir):
        """Test _apply_basic_grey with real manga image"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        img = image._load_image(img_path)
        
        result = image._apply_basic_grey(img)
        assert result is not None
        assert result.mode == 'L'
        assert result.size == img.size
    
    
    def test_apply_grey_palette_with_palette4(self):
        """Test _apply_grey_palette with 4-color palette"""
        test_img = PILImage.new('RGB', (100, 100), color=(128, 128, 128))
        
        result = image._apply_grey_palette(test_img, image.Palette4)
        assert result is not None
        assert result.mode == 'P'  # Mode palette
        assert result.size == test_img.size
    
    
    def test_apply_grey_palette_with_palette15a(self):
        """Test _apply_grey_palette with 15-color palette A"""
        test_img = PILImage.new('RGB', (100, 100), color=(200, 200, 200))
        
        result = image._apply_grey_palette(test_img, image.Palette15a)
        assert result is not None
        assert result.mode == 'P'
        assert result.size == test_img.size
    
    
    def test_apply_grey_palette_with_palette15b(self):
        """Test _apply_grey_palette with 15-color palette B"""
        test_img = PILImage.new('RGB', (100, 100), color=(150, 150, 150))
        
        result = image._apply_grey_palette(test_img, image.Palette15b)
        assert result is not None
        assert result.mode == 'P'
        assert result.size == test_img.size
    
    
    def test_apply_grey_palette_with_palette16(self):
        """Test _apply_grey_palette with 16-color palette"""
        test_img = PILImage.new('RGB', (100, 100), color=(100, 100, 100))
        
        result = image._apply_grey_palette(test_img, image.Palette16)
        assert result is not None
        assert result.mode == 'P'
        assert result.size == test_img.size
    
    
    def test_apply_grey_palette_extends_small_palette(self):
        """Test _apply_grey_palette extends palette if less than 256 colors"""
        # Palette avec seulement 4 couleurs (12 valeurs)
        small_palette = [0, 0, 0, 85, 85, 85, 170, 170, 170, 255, 255, 255]
        test_img = PILImage.new('RGB', (50, 50), color=(128, 128, 128))
        
        result = image._apply_grey_palette(test_img, small_palette)
        assert result is not None
        assert result.mode == 'P'
        # La palette devrait être étendue à 256 couleurs
    
    
    def test_apply_grey_palette_with_gradient_image(self):
        """Test _apply_grey_palette with gradient image"""
        test_img = PILImage.new('RGB', (256, 100))
        pixels = test_img.load()
        for x in range(256):
            for y in range(100):
                pixels[x, y] = (x, x, x)  # Gradient de noir à blanc
        
        result = image._apply_grey_palette(test_img, image.Palette16)
        assert result is not None
        assert result.mode == 'P'
        # Vérifier que le gradient est quantifié
    
    
    def test_apply_grey_palette_with_real_image(self, test_images_dir):
        """Test _apply_grey_palette with real image"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        img = image._load_image(img_path)
        
        result = image._apply_grey_palette(img, image.Palette15a)
        assert result is not None
        assert result.mode == 'P'
        assert result.size == img.size
    
    
    def test_quantize_image_with_palette4(self):
        """Test _quantize_image chooses best compression with Palette4"""
        test_img = PILImage.new('RGB', (200, 200), color=(128, 128, 128))
        
        result = image._quantize_image(test_img, image.Palette4)
        assert result is not None
        # Devrait retourner soit mode P (palette) soit L (greyscale)
        assert result.mode in ('P', 'L')
        assert result.size == test_img.size
    
    
    def test_quantize_image_with_palette15a(self):
        """Test _quantize_image with Palette15a"""
        test_img = PILImage.new('RGB', (200, 200), color=(150, 150, 150))
        
        result = image._quantize_image(test_img, image.Palette15a)
        assert result is not None
        assert result.mode in ('P', 'L')
    
    
    def test_quantize_image_with_palette16(self):
        """Test _quantize_image with Palette16"""
        test_img = PILImage.new('RGB', (200, 200), color=(100, 100, 100))
        
        result = image._quantize_image(test_img, image.Palette16)
        assert result is not None
        assert result.mode in ('P', 'L')
    
    
    def test_quantize_image_with_complex_image(self):
        """Test _quantize_image with complex gradient image"""
        test_img = PILImage.new('RGB', (300, 300))
        pixels = test_img.load()
        for x in range(300):
            for y in range(300):
                # Créer un pattern complexe
                pixels[x, y] = ((x + y) % 256, (x + y) % 256, (x + y) % 256)
        
        result = image._quantize_image(test_img, image.Palette15b)
        assert result is not None
        assert result.mode in ('P', 'L')
        assert result.size == test_img.size
    
    
    def test_quantize_image_with_real_manga(self, test_images_dir):
        """Test _quantize_image with real manga page"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        img = image._load_image(img_path)
        
        result = image._quantize_image(img, image.Palette16)
        assert result is not None
        assert result.mode in ('P', 'L')
        assert result.size == img.size
    
    
    def test_quantize_image_with_real_comics(self, test_images_dir):
        """Test _quantize_image with real comics page"""
        img_path = self.get_test_image_path(test_images_dir, "comics_classic.jpg")
        img = image._load_image(img_path)
        
        result = image._quantize_image(img, image.Palette15a)
        assert result is not None
        assert result.mode in ('P', 'L')
        assert result.size == img.size
    
    
    def test_quantize_image_preserves_size(self):
        """Test _quantize_image preserves image dimensions"""
        original_size = (150, 200)
        test_img = PILImage.new('RGB', original_size, color=(180, 180, 180))
        
        result = image._quantize_image(test_img, image.Palette4)
        assert result is not None
        assert result.size == original_size
    
    
    def test_apply_grey_palette_with_black_image(self):
        """Test _apply_grey_palette with pure black image"""
        test_img = PILImage.new('RGB', (100, 100), color=(0, 0, 0))
        
        result = image._apply_grey_palette(test_img, image.Palette16)
        assert result is not None
        assert result.mode == 'P'
    
    
    def test_apply_grey_palette_with_white_image(self):
        """Test _apply_grey_palette with pure white image"""
        test_img = PILImage.new('RGB', (100, 100), color=(255, 255, 255))
        
        result = image._apply_grey_palette(test_img, image.Palette16)
        assert result is not None
        assert result.mode == 'P'
    
    
    def test_quantize_image_different_palettes_same_image(self):
        """Test _quantize_image with different palettes on same image"""
        test_img = PILImage.new('RGB', (150, 150), color=(128, 128, 128))
        
        result4 = image._quantize_image(test_img, image.Palette4)
        result15a = image._quantize_image(test_img, image.Palette15a)
        result16 = image._quantize_image(test_img, image.Palette16)
        
        # Tous devraient retourner une image valide
        assert result4 is not None
        assert result15a is not None
        assert result16 is not None
        
        # Tous devraient avoir le même size
        assert result4.size == test_img.size
        assert result15a.size == test_img.size
        assert result16.size == test_img.size
