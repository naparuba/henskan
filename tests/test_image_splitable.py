#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for is_splitable() function
Tests if an image can be split (landscape) or not (portrait)
"""
import os
import sys
from PIL import Image as PILImage

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase
from henskan import image


class TestIsSplitable(ImageTestBase):
    """Tests for is_splitable() function"""
    
    def test_is_splitable_landscape_image(self, temp_dir):
        """Test is_splitable returns True for landscape image"""
        # Créer une image paysage (width > height)
        landscape_img = PILImage.new('RGB', (800, 600), color='white')
        temp_path = os.path.join(temp_dir, "landscape.png")
        landscape_img.save(temp_path)
        
        # is_splitable devrait retourner True car width > height
        result = image.is_splitable(temp_path)
        assert result == True
    
    
    def test_is_splitable_portrait_image(self, temp_dir):
        """Test is_splitable returns False for portrait image"""
        # Créer une image portrait (width < height)
        portrait_img = PILImage.new('RGB', (600, 800), color='white')
        temp_path = os.path.join(temp_dir, "portrait.png")
        portrait_img.save(temp_path)
        
        # is_splitable devrait retourner False car width < height
        result = image.is_splitable(temp_path)
        assert result == False
    
    
    def test_is_splitable_square_image(self, temp_dir):
        """Test is_splitable with square image (edge case)"""
        # Créer une image carrée (width == height)
        square_img = PILImage.new('RGB', (600, 600), color='white')
        temp_path = os.path.join(temp_dir, "square.png")
        square_img.save(temp_path)
        
        # is_splitable devrait retourner False car width n'est PAS > height
        result = image.is_splitable(temp_path)
        assert result == False
    
    
    def test_is_splitable_real_double_page(self, temp_dir):
        """Test is_splitable with real manga double page"""
        # Créer une double page manga pour le test
        double_page_img = PILImage.new('RGB', (1600, 800), color='white')
        temp_path = os.path.join(temp_dir, "double_page.png")
        double_page_img.save(temp_path)
        
        result = image.is_splitable(temp_path)
        
        # Une double page devrait être splitable (landscape)
        assert result == True
    
    
    def test_is_splitable_real_single_page(self, temp_dir):
        """Test is_splitable with real manga single page"""
        # Créer une page simple manga pour le test
        single_page_img = PILImage.new('RGB', (800, 1200), color='white')
        temp_path = os.path.join(temp_dir, "single_page.png")
        single_page_img.save(temp_path)
        
        result = image.is_splitable(temp_path)
        
        # Une page simple devrait être portrait (non splitable)
        assert result == False
    
    
    def test_is_splitable_invalid_path(self):
        """Test is_splitable raises RuntimeError with non-existent file"""
        import pytest
        
        invalid_path = "/nonexistent/path/to/image.jpg"
        
        # Devrait lever RuntimeError
        with pytest.raises(RuntimeError, match='Cannot read image file'):
            image.is_splitable(invalid_path)
    
    
    def test_is_splitable_corrupted_image(self, temp_dir):
        """Test is_splitable raises RuntimeError with corrupted image"""
        import pytest
        
        # Créer un fichier corrompu (pas une vraie image)
        corrupted_path = os.path.join(temp_dir, "corrupted.jpg")
        with open(corrupted_path, 'wb') as f:
            f.write(b"This is not a valid image file")
        
        # Devrait lever RuntimeError
        with pytest.raises(RuntimeError, match='Cannot read image file'):
            image.is_splitable(corrupted_path)
    
    
    def test_is_splitable_very_wide_image(self, temp_dir):
        """Test is_splitable with very wide image (extreme landscape)"""
        # Créer une image très large (ratio extrême)
        very_wide_img = PILImage.new('RGB', (3000, 500), color='white')
        temp_path = os.path.join(temp_dir, "very_wide.png")
        very_wide_img.save(temp_path)
        
        # Devrait être splitable car très large
        result = image.is_splitable(temp_path)
        assert result == True
    
    
    def test_is_splitable_webtoon_image(self, test_images_dir, temp_dir):
        """Test is_splitable returns False for webtoon (very tall)"""
        # Créer une image webtoon pour le test
        webtoon_img = PILImage.new('RGB', (720, 5000), color='white')
        temp_path = os.path.join(temp_dir, "webtoon.png")
        webtoon_img.save(temp_path)
        
        result = image.is_splitable(temp_path)
        
        # Un webtoon est très haut, donc non splitable
        assert result == False
    
    
    def test_is_splitable_various_aspect_ratios(self, temp_dir):
        """Test is_splitable with various aspect ratios"""
        test_cases = [
            # (width, height, expected_splitable)
            (1000, 500, True),   # 2:1 - splitable
            (500, 1000, False),  # 1:2 - not splitable
            (1920, 1080, True),  # 16:9 - splitable
            (1080, 1920, False), # 9:16 - not splitable
            (800, 800, False),   # 1:1 - not splitable (square)
            (1600, 1200, True),  # 4:3 landscape - splitable
            (1200, 1600, False), # 3:4 portrait - not splitable
        ]
        
        for width, height, expected in test_cases:
            test_img = PILImage.new('RGB', (width, height), color='white')
            temp_path = os.path.join(temp_dir, f"test_{width}x{height}.png")
            test_img.save(temp_path)
            
            result = image.is_splitable(temp_path)
            assert result == expected, f"Failed for {width}x{height}: expected {expected}, got {result}"

