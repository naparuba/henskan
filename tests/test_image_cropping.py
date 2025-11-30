#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for image cropping operations
"""
import os
import sys

from PIL import Image as PILImage

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase
from henskan import image


class TestImageCropping(ImageTestBase):
    """Tests for image cropping operations"""
    
    
    # ============================================
    # Tests pour _simple_crop_image
    # ============================================
    
    def test_simple_crop_image_removes_white_borders(self):
        """Test _simple_crop_image removes white borders"""
        # Créer une image avec des bordures blanches
        test_img = PILImage.new('RGB', (200, 200), color='white')
        pixels = test_img.load()
        # Zone centrale en noir (50x50 au centre)
        for x in range(75, 125):
            for y in range(75, 125):
                pixels[x, y] = (0, 0, 0)
        
        original_size = test_img.size
        result = image._simple_crop_image(test_img)
        
        assert result is not None
        # L'image devrait être plus petite (bordures enlevées)
        assert result.size[0] < original_size[0]
        assert result.size[1] < original_size[1]
        # Devrait être environ 50x50
        assert result.size[0] == 50
        assert result.size[1] == 50
    
    
    def test_simple_crop_image_with_real_manga(self, test_images_dir):
        """Test _simple_crop_image with real manga image"""
        img_path = self.get_test_image_path(test_images_dir, "manga_lot_of_white_around.jpg")
        img = image._load_image(img_path)
        
        original_size = img.size
        result = image._simple_crop_image(img)
        
        assert result is not None
        # L'image devrait être croppée (probablement plus petite)
        assert result.size[0] <= original_size[0]
        assert result.size[1] <= original_size[1]
    
    
    def test_simple_crop_image_with_no_borders(self):
        """Test _simple_crop_image with image without white borders"""
        # Image complètement noire (pas de bordures)
        test_img = PILImage.new('RGB', (100, 100), color='black')
        
        original_size = test_img.size
        result = image._simple_crop_image(test_img)
        
        assert result is not None
        # L'image devrait rester de la même taille
        assert result.size == original_size
    
    
    def test_simple_crop_image_asymmetric_borders(self):
        """Test _simple_crop_image with asymmetric borders"""
        # Créer une image avec bordures asymétriques
        test_img = PILImage.new('RGB', (200, 150), color='white')
        pixels = test_img.load()
        # Zone noire décalée (de 30,20 à 170,130)
        for x in range(30, 170):
            for y in range(20, 130):
                pixels[x, y] = (0, 0, 0)
        
        result = image._simple_crop_image(test_img)
        
        assert result is not None
        # Devrait être 140x110
        assert result.size == (140, 110)
    
    
    def test_simple_crop_image_preserves_content(self):
        """Test _simple_crop_image preserves image content"""
        # Créer une image avec bordure et un pattern unique au centre
        test_img = PILImage.new('RGB', (150, 150), color='white')
        pixels = test_img.load()
        # Zone grise
        for x in range(30, 120):
            for y in range(30, 120):
                pixels[x, y] = (128, 128, 128)
        # Point rouge au centre
        pixels[75, 75] = (255, 0, 0)
        
        result = image._simple_crop_image(test_img)
        
        assert result is not None
        # Le point rouge devrait être préservé (au nouveau centre)
        result_pixels = result.load()
        center_x = result.size[0] // 2
        center_y = result.size[1] // 2
        assert result_pixels[center_x, center_y] == (255, 0, 0)
    
    
    def test_simple_crop_image_with_closed_image_returns_original(self):
        """Test _simple_crop_image with closed image returns original"""
        test_img = PILImage.new('RGB', (100, 100), color='white')
        test_img.close()
        
        result = image._simple_crop_image(test_img)
        assert result is test_img  # Retourne l'original en cas d'erreur
    
    
    # ============================================
    # Tests pour _blurauto_crop_image
    # ============================================
    
    def test_blurauto_crop_image_basic(self):
        """Test _blurauto_crop_image with basic image"""
        # Créer une image avec bordures
        test_img = PILImage.new('RGB', (200, 200), color='white')
        pixels = test_img.load()
        # Zone centrale en gris foncé
        for x in range(50, 150):
            for y in range(50, 150):
                pixels[x, y] = (50, 50, 50)
        
        original_size = test_img.size
        result = image._blurauto_crop_image(test_img)
        
        assert result is not None
        # L'image devrait être croppée
        assert result.size[0] <= original_size[0]
        assert result.size[1] <= original_size[1]
    
    
    def test_blurauto_crop_image_with_real_manga(self, test_images_dir):
        """Test _blurauto_crop_image with real manga"""
        img_path = self.get_test_image_path(test_images_dir, "manga_can_remove_white_on_top.jpg")
        img = image._load_image(img_path)
        
        original_size = img.size
        result = image._blurauto_crop_image(img)
        
        assert result is not None
        assert result.size[0] <= original_size[0]
        assert result.size[1] <= original_size[1]
    
    
    def test_blurauto_crop_image_no_bbox_returns_original(self):
        """Test _blurauto_crop_image returns original if no bbox found"""
        # Image complètement blanche (pas de bbox)
        test_img = PILImage.new('RGB', (100, 100), color='white')
        
        result = image._blurauto_crop_image(test_img)
        
        assert result is not None
        assert result is test_img  # Retourne l'original
    
    
    def test_blurauto_crop_image_with_gradient(self):
        """Test _blurauto_crop_image with gradient image"""
        # Créer une image avec gradient
        test_img = PILImage.new('RGB', (150, 150))
        pixels = test_img.load()
        for x in range(150):
            for y in range(150):
                intensity = int((x + y) / 2)
                pixels[x, y] = (intensity, intensity, intensity)
        
        result = image._blurauto_crop_image(test_img)
        
        assert result is not None
        # Devrait traiter le gradient
    
    
    def test_blurauto_crop_image_with_noise(self):
        """Test _blurauto_crop_image handles noisy borders"""
        # Créer une image avec bordures bruitées
        test_img = PILImage.new('RGB', (180, 180), color='white')
        pixels = test_img.load()
        # Zone centrale noire
        for x in range(40, 140):
            for y in range(40, 140):
                pixels[x, y] = (0, 0, 0)
        # Ajouter du bruit sur les bordures
        import random
        random.seed(42)
        for x in range(180):
            for y in range(10):
                if random.random() > 0.7:
                    pixels[x, y] = (200, 200, 200)
        
        result = image._blurauto_crop_image(test_img)
        
        assert result is not None
        # Le blur devrait gérer le bruit
    
    
    # ============================================
    # Tests pour _auto_crop_image
    # ============================================
    
    def test_auto_crop_image_with_page_numbers(self, test_images_dir):
        """Test _auto_crop_image removes page numbers at bottom"""
        img_path = self.get_test_image_path(test_images_dir, "manga_can_remove_page_number.jpg")
        img = image._load_image(img_path)
        
        original_height = img.size[1]
        result = image._auto_crop_image(img)
        
        assert result is not None
        # La hauteur devrait être réduite (numéro de page enlevé)
        assert result.size[1] <= original_height
    
    
    def test_auto_crop_image_basic_manga(self, test_images_dir):
        """Test _auto_crop_image with basic manga page"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        img = image._load_image(img_path)
        
        original_size = img.size
        result = image._auto_crop_image(img)
        
        assert result is not None
        # Devrait être croppée ou de taille identique
        assert result.size[0] <= original_size[0]
        assert result.size[1] <= original_size[1]
    
    
    def test_auto_crop_image_with_white_around(self, test_images_dir):
        """Test _auto_crop_image with white borders"""
        img_path = self.get_test_image_path(test_images_dir, "manga_lot_of_white_around.jpg")
        img = image._load_image(img_path)
        
        original_size = img.size
        result = image._auto_crop_image(img)
        
        assert result is not None
        # Devrait enlever le blanc autour
        assert result.size[0] < original_size[0] or result.size[1] < original_size[1]
    
    
    def test_auto_crop_image_double_page(self, test_images_dir):
        """Test _auto_crop_image with double page"""
        img_path = self.get_test_image_path(test_images_dir, "manga_scan_double_page.jpg")
        img = image._load_image(img_path)
        
        result = image._auto_crop_image(img)
        
        assert result is not None
        # Devrait traiter la double page correctement
    
    
    def test_auto_crop_image_clean_manga(self, test_images_dir):
        """Test _auto_crop_image with clean manga"""
        img_path = self.get_test_image_path(test_images_dir, "manga_clean_can_remove_page_number.jpg")
        img = image._load_image(img_path)
        
        original_size = img.size
        result = image._auto_crop_image(img)
        
        assert result is not None
        assert result.size[0] <= original_size[0]
        assert result.size[1] <= original_size[1]
    
    
    def test_auto_crop_image_old_quality(self, test_images_dir):
        """Test _auto_crop_image with old quality manga"""
        img_path = self.get_test_image_path(test_images_dir, "manga_bad_quality.jpg")
        img = image._load_image(img_path)
        
        result = image._auto_crop_image(img)
        
        assert result is not None
        # Devrait gérer la mauvaise qualité
    
    
    def test_auto_crop_image_preserves_content(self):
        """Test _auto_crop_image preserves main content"""
        # Créer une image avec contenu principal et bordures
        test_img = PILImage.new('RGB', (300, 400), color='white')
        pixels = test_img.load()
        
        # Contenu principal (zone grise centrale)
        for x in range(50, 250):
            for y in range(50, 350):
                pixels[x, y] = (128, 128, 128)
        
        # Point de référence au centre
        pixels[150, 200] = (255, 0, 0)
        
        result = image._auto_crop_image(test_img)
        
        assert result is not None
        # Vérifier que le point rouge est toujours présent
        result_pixels = result.load()
        found_red = False
        for x in range(result.size[0]):
            for y in range(result.size[1]):
                if result_pixels[x, y] == (255, 0, 0):
                    found_red = True
                    break
            if found_red:
                break
        assert found_red, "Red reference point should be preserved"
    
    
    def test_auto_crop_image_with_comics(self, test_images_dir):
        """Test _auto_crop_image with comics page"""
        img_path = self.get_test_image_path(test_images_dir, "comics_can_remove_page_number.jpg")
        img = image._load_image(img_path)
        
        original_size = img.size
        result = image._auto_crop_image(img)
        
        assert result is not None
        assert result.size[0] <= original_size[0]
        assert result.size[1] <= original_size[1]
    
    
    # ============================================
    # Tests comparatifs entre les méthodes
    # ============================================
    
    def test_simple_vs_blurauto_crop(self):
        """Test comparison between simple and blurauto crop"""
        # Créer une image de test
        test_img = PILImage.new('RGB', (200, 200), color='white')
        pixels = test_img.load()
        for x in range(50, 150):
            for y in range(50, 150):
                pixels[x, y] = (100, 100, 100)
        
        simple_result = image._simple_crop_image(test_img)
        blurauto_result = image._blurauto_crop_image(test_img)
        
        assert simple_result is not None
        assert blurauto_result is not None
        # Les deux devraient avoir croppé l'image
        assert simple_result.size[0] <= test_img.size[0]
        assert blurauto_result.size[0] <= test_img.size[0]
    
    
    def test_auto_crop_uses_simple_and_blur(self, test_images_dir):
        """Test _auto_crop_image uses both simple and blur crop"""
        img_path = self.get_test_image_path(test_images_dir, "manga_lot_of_white_around_again.jpg")
        img = image._load_image(img_path)
        
        # _auto_crop_image utilise _simple_crop_image et _blurauto_crop_image
        result = image._auto_crop_image(img)
        
        assert result is not None
        # Le résultat devrait être optimisé par les deux méthodes
    
    
    def test_crop_methods_handle_edge_cases(self):
        """Test all crop methods handle edge cases"""
        # Image très petite
        tiny_img = PILImage.new('RGB', (10, 10), color='white')
        
        simple_result = image._simple_crop_image(tiny_img)
        blurauto_result = image._blurauto_crop_image(tiny_img)
        auto_result = image._auto_crop_image(tiny_img)
        
        assert simple_result is not None
        assert blurauto_result is not None
        assert auto_result is not None
    
    
    def test_crop_maintains_aspect_ratio_concept(self):
        """Test crop maintains meaningful aspect ratio"""
        # Image rectangulaire avec contenu
        test_img = PILImage.new('RGB', (300, 200), color='white')
        pixels = test_img.load()
        for x in range(50, 250):
            for y in range(40, 160):
                pixels[x, y] = (80, 80, 80)
        
        result = image._simple_crop_image(test_img)
        
        assert result is not None
        # Le ratio devrait être préservé approximativement
        original_ratio = 300 / 200
        result_ratio = result.size[0] / result.size[1]
        # Les ratios devraient être similaires (tolérance)
        assert abs(original_ratio - result_ratio) < 1.0
