#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for error handling and edge cases
"""
import os
import sys

from PIL import Image as PILImage

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase
from henskan import image


class TestErrorHandling(ImageTestBase):
    """Tests for error handling and edge cases"""
    
    
    def test_split_left_with_closed_image(self):
        """Test _split_left returns original image when operation fails"""
        test_img = PILImage.new('RGB', (100, 100), color='white')
        test_img.close()
        
        # Le décorateur devrait attraper l'erreur et retourner l'image originale
        result = image._split_left(test_img)
        assert result is test_img  # Devrait retourner l'image originale
    
    
    def test_split_right_with_closed_image(self):
        """Test _split_right returns original image when operation fails"""
        test_img = PILImage.new('RGB', (100, 100), color='blue')
        test_img.close()
        
        result = image._split_right(test_img)
        assert result is test_img  # Devrait retourner l'image originale
    
    
    def test_split_left_with_valid_image(self, test_images_dir):
        """Test _split_left works correctly with valid images"""
        img_path = self.get_test_image_path(test_images_dir, "manga_scan_double_page.jpg")
        img = PILImage.open(img_path)
        original_width, original_height = img.size
        
        result = image._split_left(img)
        assert result is not None
        assert result.size == (original_width // 2, original_height)
        assert result != img  # Devrait être une nouvelle image
    
    
    def test_split_right_with_valid_image(self, test_images_dir):
        """Test _split_right works correctly with valid images"""
        img_path = self.get_test_image_path(test_images_dir, "manga_scan_double_page.jpg")
        img = PILImage.open(img_path)
        original_width, original_height = img.size
        
        result = image._split_right(img)
        assert result is not None
        assert result.size == (original_width // 2, original_height)
    
    
    def test_is_globally_grey_with_corrupted_pixel_data(self):
        """Test _is_globally_grey__slow handles corrupt pixel data"""
        test_img = PILImage.new('RGB', (10, 10), color='grey')
        test_img.close()
        
        # Le décorateur devrait attraper l'erreur et retourner l'image originale
        result = image._is_globally_grey__slow(test_img)
        assert result is test_img  # Retourne l'image originale en cas d'erreur
    
    
    def test_is_totally_greyscale_with_valid_greyscale(self, test_images_dir):
        """Test _is_totally_greyscale__fast with actual greyscale image"""
        # Créer une vraie image en niveaux de gris
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        img = image._load_image(img_path).convert('L')  # Forcer en greyscale
        
        result = image._is_totally_greyscale__fast(img)
        assert isinstance(result, bool)
        assert result is True  # Image L est toujours greyscale
    
    
    def test_is_totally_greyscale_with_rgb_color(self):
        """Test _is_totally_greyscale__fast with colored RGB image"""
        # Image RGB colorée
        color_img = PILImage.new('RGB', (50, 50))
        pixels = color_img.load()
        for i in range(50):
            for j in range(50):
                pixels[i, j] = (255, 0, 0)  # Rouge pur
        
        result = image._is_totally_greyscale__fast(color_img)
        assert isinstance(result, bool)
        assert result is False  # Image colorée
    
    
    def test_resize_image_with_invalid_size(self):
        """Test _resize_image with closed image"""
        test_img = PILImage.new('RGB', (100, 100), color='green')
        test_img.close()
        
        result = image._resize_image(test_img, (50, 50))
        assert result is test_img  # Retourne l'original en cas d'erreur
    
    
    def test_resize_image_with_valid_image(self):
        """Test _resize_image works correctly"""
        test_img = PILImage.new('RGB', (200, 300), color='blue')
        
        result = image._resize_image(test_img, (100, 150))
        assert result is not None
        # Vérifie que l'image a été redimensionnée (ratio préservé)
        assert result.size[0] <= 100
        assert result.size[1] <= 150
    
    
    def test_format_image_to_rgb_already_rgb(self):
        """Test _format_image_to_rgb with already RGB image"""
        test_img = PILImage.new('RGB', (50, 50), color='red')
        
        result = image._format_image_to_rgb(test_img)
        assert result is test_img  # Même image car déjà RGB
    
    
    def test_format_image_to_rgb_from_greyscale(self):
        """Test _format_image_to_rgb converts L to RGB"""
        test_img = PILImage.new('L', (50, 50), color=128)
        
        result = image._format_image_to_rgb(test_img)
        assert result is not None
        assert result.mode == 'RGB'
    
    
    def test_format_image_to_rgb_with_closed_image(self):
        """Test _format_image_to_rgb with closed image"""
        test_img = PILImage.new('L', (50, 50))
        test_img.close()
        
        result = image._format_image_to_rgb(test_img)
        assert result is test_img  # Retourne l'original en cas d'erreur
    
    
    def test_orient_image_landscape_to_portrait(self):
        """Test _orient_image rotates when orientations differ"""
        test_img = PILImage.new('RGB', (200, 100), color='yellow')  # Paysage
        device_size = (100, 200)  # Portrait
        
        result = image._orient_image(test_img, device_size)
        assert result is not None
        # Devrait être tourné
        assert result.size != test_img.size
    
    
    def test_orient_image_same_orientation(self):
        """Test _orient_image keeps image when orientations match"""
        test_img = PILImage.new('RGB', (100, 200), color='purple')  # Portrait
        device_size = (100, 200)  # Portrait aussi
        
        result = image._orient_image(test_img, device_size)
        assert result is test_img  # Pas de rotation nécessaire
    
    
    def test_simple_crop_image_with_white_borders(self):
        """Test _simple_crop_image removes white borders"""
        # Créer une image avec des bordures blanches
        test_img = PILImage.new('RGB', (100, 100), color='white')
        pixels = test_img.load()
        # Zone centrale en noir
        for i in range(20, 80):
            for j in range(20, 80):
                pixels[i, j] = (0, 0, 0)
        
        result = image._simple_crop_image(test_img)
        assert result is not None
        # Devrait être plus petit (bordures enlevées)
        assert result.size[0] < test_img.size[0]
        assert result.size[1] < test_img.size[1]
    
    
    def test_simple_crop_image_with_closed_image(self):
        """Test _simple_crop_image with closed image"""
        test_img = PILImage.new('RGB', (100, 100))
        test_img.close()
        
        result = image._simple_crop_image(test_img)
        assert result is test_img  # Retourne l'original
    
    
    def test_apply_basic_grey_converts_to_greyscale(self):
        """Test _apply_basic_grey converts color to greyscale"""
        test_img = PILImage.new('RGB', (50, 50), color=(100, 150, 200))
        
        result = image._apply_basic_grey(test_img)
        assert result is not None
        assert result.mode == 'L'  # Mode greyscale
    
    
    def test_apply_basic_grey_with_closed_image(self):
        """Test _apply_basic_grey with closed image"""
        test_img = PILImage.new('RGB', (50, 50))
        test_img.close()
        
        result = image._apply_basic_grey(test_img)
        assert result is test_img  # Retourne l'original
    
    
    def test_apply_grey_palette_with_valid_image(self):
        """Test _apply_grey_palette applies palette correctly"""
        test_img = PILImage.new('RGB', (50, 50), color='grey')
        palette = image.Palette4  # Palette 4 couleurs
        
        result = image._apply_grey_palette(test_img, palette)
        assert result is not None
        assert result.mode == 'P'  # Mode palette
    
    
    def test_quantize_image_with_valid_image(self):
        """Test _quantize_image quantizes correctly"""
        test_img = PILImage.new('RGB', (100, 100), color=(128, 128, 128))
        palette = image.Palette4
        
        result = image._quantize_image(test_img, palette)
        assert result is not None
        # Devrait retourner soit palette soit basic grey
        assert result.mode in ('P', 'L')
