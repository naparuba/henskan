#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for image transformations
"""
import os
import sys

from PIL import Image as PILImage

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase
from henskan import image


class TestImageTransformations(ImageTestBase):
    """Tests for image transformations (resize, orient, etc.)"""
    
    
    # ============================================
    # Tests pour _resize_image
    # ============================================
    
    def test_resize_image_width_limited(self):
        """Test _resize_image when width is the limiting factor"""
        test_img = PILImage.new('RGB', (1000, 500), color='blue')  # Ratio 2:1
        target_size = (500, 600)  # Width limite
        
        result = image._resize_image(test_img, target_size)
        assert result is not None
        # Width devrait être 500, height proportionnel (250)
        assert result.size[0] == 500
        assert result.size[1] == 250
    
    
    def test_resize_image_height_limited(self):
        """Test _resize_image when height is the limiting factor"""
        test_img = PILImage.new('RGB', (500, 1000), color='green')  # Ratio 1:2
        target_size = (600, 500)  # Height limite
        
        result = image._resize_image(test_img, target_size)
        assert result is not None
        # Height devrait être 500, width proportionnel (250)
        assert result.size[0] == 250
        assert result.size[1] == 500
    
    
    def test_resize_image_same_ratio(self):
        """Test _resize_image when ratios match exactly"""
        test_img = PILImage.new('RGB', (400, 600), color='red')  # Ratio 2:3
        target_size = (200, 300)  # Même ratio 2:3
        
        result = image._resize_image(test_img, target_size)
        assert result is not None
        assert result.size == target_size
    
    
    def test_resize_image_upscale(self):
        """Test _resize_image can upscale images"""
        test_img = PILImage.new('RGB', (100, 100), color='yellow')
        target_size = (300, 300)
        
        result = image._resize_image(test_img, target_size)
        assert result is not None
        assert result.size == target_size
    
    
    def test_resize_image_downscale(self):
        """Test _resize_image can downscale images"""
        test_img = PILImage.new('RGB', (800, 600), color='purple')
        target_size = (200, 150)
        
        result = image._resize_image(test_img, target_size)
        assert result is not None
        # Devrait être redimensionné en respectant le ratio
        assert result.size[0] <= 200
        assert result.size[1] <= 150
    
    
    def test_resize_image_preserves_aspect_ratio(self):
        """Test _resize_image preserves aspect ratio"""
        test_img = PILImage.new('RGB', (1600, 1200), color='orange')  # Ratio 4:3
        target_size = (800, 800)
        
        result = image._resize_image(test_img, target_size)
        assert result is not None
        # Le ratio devrait être préservé (4:3)
        original_ratio = 1600 / 1200
        result_ratio = result.size[0] / result.size[1]
        assert abs(original_ratio - result_ratio) < 0.01  # Tolérance de 1%
    
    
    def test_resize_image_with_real_manga(self, test_images_dir):
        """Test _resize_image with real manga image"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        img = image._load_image(img_path)
        target_size = (600, 800)
        
        result = image._resize_image(img, target_size)
        assert result is not None
        assert result.size[0] <= 600
        assert result.size[1] <= 800
    
    
    def test_resize_image_with_real_webtoon(self, test_images_dir):
        """Test _resize_image with real webtoon image (very tall)"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_lot_of_white.jpg")
        img = image._load_image(img_path)
        target_size = (400, 600)
        
        result = image._resize_image(img, target_size)
        assert result is not None
        # Pour un webtoon très haut, la hauteur sera limitante
        assert result.size[1] <= 600
    
    
    # ============================================
    # Tests pour _orient_image
    # ============================================
    
    def test_orient_image_landscape_to_portrait_device(self):
        """Test _orient_image rotates landscape image for portrait device"""
        test_img = PILImage.new('RGB', (200, 100), color='cyan')  # Paysage
        device_size = (100, 200)  # Portrait
        
        result = image._orient_image(test_img, device_size)
        assert result is not None
        # Devrait être tourné (dimensions inversées)
        assert result.size[0] < result.size[1]  # Maintenant portrait
    
    
    def test_orient_image_portrait_to_landscape_device(self):
        """Test _orient_image rotates portrait image for landscape device"""
        test_img = PILImage.new('RGB', (100, 200), color='magenta')  # Portrait
        device_size = (200, 100)  # Paysage
        
        result = image._orient_image(test_img, device_size)
        assert result is not None
        # Devrait être tourné (dimensions inversées)
        assert result.size[0] > result.size[1]  # Maintenant paysage
    
    
    def test_orient_image_portrait_to_portrait_device(self):
        """Test _orient_image keeps portrait image for portrait device"""
        test_img = PILImage.new('RGB', (100, 200), color='pink')  # Portrait
        device_size = (150, 300)  # Portrait aussi
        
        result = image._orient_image(test_img, device_size)
        assert result is not None
        # Ne devrait PAS être tourné
        assert result is test_img  # Même objet
        assert result.size == test_img.size
    
    
    def test_orient_image_landscape_to_landscape_device(self):
        """Test _orient_image keeps landscape image for landscape device"""
        test_img = PILImage.new('RGB', (200, 100), color='lime')  # Paysage
        device_size = (300, 150)  # Paysage aussi
        
        result = image._orient_image(test_img, device_size)
        assert result is not None
        # Ne devrait PAS être tourné
        assert result is test_img
        assert result.size == test_img.size
    
    
    def test_orient_image_square_to_portrait(self):
        """Test _orient_image with square image and portrait device"""
        test_img = PILImage.new('RGB', (100, 100), color='gold')  # Carré
        device_size = (100, 200)  # Portrait
        
        result = image._orient_image(test_img, device_size)
        assert result is not None
        # Carré devrait rester inchangé
        assert result is test_img
    
    
    def test_orient_image_square_to_landscape(self):
        """Test _orient_image with square image and landscape device"""
        test_img = PILImage.new('RGB', (100, 100), color='silver')  # Carré
        device_size = (200, 100)  # Paysage
        
        result = image._orient_image(test_img, device_size)
        assert result is not None
        # Pour un carré, width == height, donc (100 > 100) = False
        # Device: (200 > 100) = True
        # False != True, donc rotation
        # Mais rotation de 90° d'un carré donne le même carré (visuellement)
        assert result.size == (100, 100)  # Taille reste carrée
    
    
    def test_orient_image_with_real_landscape(self, test_images_dir):
        """Test _orient_image with real landscape manga page"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page_landscape.jpg")
        img = image._load_image(img_path)
        device_size = (600, 800)  # Portrait
        
        result = image._orient_image(img, device_size)
        assert result is not None
        # Devrait être tourné pour portrait
    
    
    # ============================================
    # Tests pour _fill_image_to_whole_size
    # ============================================
    
    def test_fill_image_to_whole_size_smaller_image(self):
        """Test _fill_image_to_whole_size with smaller image"""
        test_img = PILImage.new('RGB', (100, 100), color='red')
        target_size = (300, 300)
        
        result = image._fill_image_to_whole_size(test_img, target_size)
        assert result is not None
        assert result.size == target_size
        assert result.mode == 'RGB'
    
    
    def test_fill_image_to_whole_size_with_margin(self):
        """Test _fill_image_to_whole_size adds left margin when possible"""
        test_img = PILImage.new('RGB', (100, 100), color='blue')
        target_size = (200, 200)  # Assez de place pour la marge
        
        result = image._fill_image_to_whole_size(test_img, target_size)
        assert result is not None
        assert result.size == target_size
        # L'image devrait être collée avec une marge à gauche (10px)
        # On peut vérifier qu'il y a du blanc à gauche
        left_pixel = result.getpixel((0, 50))
        assert left_pixel == (255, 255, 255)  # Blanc
    
    
    def test_fill_image_to_whole_size_no_margin(self):
        """Test _fill_image_to_whole_size without margin when no space"""
        test_img = PILImage.new('RGB', (195, 100), color='green')
        target_size = (200, 200)  # Pas assez de place pour la marge (200 - 10 = 190 < 195)
        
        result = image._fill_image_to_whole_size(test_img, target_size)
        assert result is not None
        assert result.size == target_size
        # L'image devrait être collée à (0, 0)
        # Le pixel en haut à gauche devrait être vert
        top_left_pixel = result.getpixel((0, 0))
        assert top_left_pixel == (0, 128, 0)  # Vert
    
    
    def test_fill_image_to_whole_size_white_background(self):
        """Test _fill_image_to_whole_size fills with white background"""
        test_img = PILImage.new('RGB', (50, 50), color='black')
        target_size = (150, 150)
        
        result = image._fill_image_to_whole_size(test_img, target_size)
        assert result is not None
        assert result.size == target_size
        # Les bords devraient être blancs
        bottom_right_pixel = result.getpixel((149, 149))
        assert bottom_right_pixel == (255, 255, 255)  # Blanc
    
    
    def test_fill_image_to_whole_size_preserves_image_content(self):
        """Test _fill_image_to_whole_size preserves original image content"""
        # Créer une image avec un pattern unique
        test_img = PILImage.new('RGB', (80, 80), color='yellow')
        pixels = test_img.load()
        pixels[40, 40] = (255, 0, 0)  # Point rouge au centre
        
        target_size = (200, 200)
        
        result = image._fill_image_to_whole_size(test_img, target_size)
        assert result is not None
        # Le point rouge devrait toujours être présent (décalé par la marge)
        # Avec marge de 10, le point (40,40) devient (50,40)
        center_pixel = result.getpixel((50, 40))
        assert center_pixel == (255, 0, 0)  # Point rouge préservé
    
    
    def test_fill_image_to_whole_size_exact_size(self):
        """Test _fill_image_to_whole_size when image fits exactly"""
        test_img = PILImage.new('RGB', (190, 100), color='purple')
        target_size = (200, 200)  # Image width = 190, target - margin = 190
        
        result = image._fill_image_to_whole_size(test_img, target_size)
        assert result is not None
        assert result.size == target_size
    
    
    def test_fill_image_to_whole_size_with_real_image(self, test_images_dir):
        """Test _fill_image_to_whole_size with real manga image"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        img = image._load_image(img_path)
        target_size = (1000, 1400)
        
        result = image._fill_image_to_whole_size(img, target_size)
        assert result is not None
        assert result.size == target_size
    
    
    # ============================================
    # Tests pour _format_image_to_rgb
    # ============================================
    
    def test_format_image_to_rgb_already_rgb(self):
        """Test _format_image_to_rgb with already RGB image"""
        test_img = PILImage.new('RGB', (100, 100), color='red')
        
        result = image._format_image_to_rgb(test_img)
        assert result is not None
        assert result is test_img  # Devrait retourner la même instance
        assert result.mode == 'RGB'
    
    
    def test_format_image_to_rgb_from_greyscale(self):
        """Test _format_image_to_rgb converts greyscale to RGB"""
        test_img = PILImage.new('L', (100, 100), color=128)
        
        result = image._format_image_to_rgb(test_img)
        assert result is not None
        assert result.mode == 'RGB'
        assert result.size == test_img.size
    
    
    def test_format_image_to_rgb_from_palette(self):
        """Test _format_image_to_rgb converts palette mode to RGB"""
        test_img = PILImage.new('P', (100, 100))
        test_img.putpalette([i for i in range(256)] * 3)
        
        result = image._format_image_to_rgb(test_img)
        assert result is not None
        assert result.mode == 'RGB'
        assert result.size == test_img.size
    
    
    def test_format_image_to_rgb_from_rgba(self):
        """Test _format_image_to_rgb converts RGBA to RGB"""
        test_img = PILImage.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        
        result = image._format_image_to_rgb(test_img)
        assert result is not None
        assert result.mode == 'RGB'
        assert result.size == test_img.size
    
    
    def test_format_image_to_rgb_from_cmyk(self):
        """Test _format_image_to_rgb converts CMYK to RGB"""
        test_img = PILImage.new('CMYK', (100, 100), color=(0, 100, 100, 0))
        
        result = image._format_image_to_rgb(test_img)
        assert result is not None
        assert result.mode == 'RGB'
        assert result.size == test_img.size
    
    
    def test_format_image_to_rgb_preserves_content(self):
        """Test _format_image_to_rgb preserves image content"""
        # Créer une image greyscale avec un pattern
        test_img = PILImage.new('L', (100, 100), color=200)
        pixels = test_img.load()
        pixels[50, 50] = 50  # Point plus sombre
        
        result = image._format_image_to_rgb(test_img)
        assert result is not None
        assert result.mode == 'RGB'
        # Le point sombre devrait être préservé
        dark_pixel = result.getpixel((50, 50))
        assert dark_pixel == (50, 50, 50)  # Greyscale converti en RGB
    
    
    def test_format_image_to_rgb_with_real_image(self, test_images_dir):
        """Test _format_image_to_rgb with real image"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        img = image._load_image(img_path)
        
        result = image._format_image_to_rgb(img)
        assert result is not None
        assert result.mode == 'RGB'
        assert result.size == img.size
