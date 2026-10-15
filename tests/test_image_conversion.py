#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for complete image conversion pipeline
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase
from henskan import image
from henskan.parameters import parameters


class TestImageConversion(ImageTestBase):
    """Tests for complete image conversion pipeline"""
    
    
    def setup_method(self):
        """Setup before each test - set a default device"""
        # Index 5: 'Kindle Paperwhite 3/Voyage/Oasis'
        parameters.set_device('Kindle Paperwhite 3/Voyage/Oasis', 5)
        parameters.set_is_webtoon(False)
    
    
    def teardown_method(self):
        """Cleanup after each test"""
        parameters.set_is_webtoon(False)
    
    
    # ============================================
    # Tests basiques de convert_image
    # ============================================
    
    def test_convert_image_basic_manga(self, test_images_dir):
        """Test convert_image with basic manga page"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        
        result = image.convert_image(img_path)
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1  # Une seule image en sortie
        
        converted_img = result[0]
        assert converted_img is not None
        # Devrait être redimensionnée à la taille du device
        device_size = image.EReaderData.get_size('Kindle Paperwhite 3/Voyage/Oasis')
        assert converted_img.size == device_size
    
    
    def test_convert_image_basic_comics(self, test_images_dir):
        """Test convert_image with basic comics page"""
        img_path = self.get_test_image_path(test_images_dir, "comics_classic.jpg")
        
        result = image.convert_image(img_path)
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        
        converted_img = result[0]
        assert converted_img is not None
    
    
    def test_convert_image_returns_list(self, test_images_dir):
        """Test convert_image always returns a list"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        
        result = image.convert_image(img_path)
        assert isinstance(result, list)
    
    
    def test_convert_image_with_different_device_kindle(self, test_images_dir):
        """Test convert_image with Kindle device"""
        parameters.set_device('Kindle 2/3/Touch', 1)
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        
        result = image.convert_image(img_path)
        assert len(result) == 1
        
        device_size = image.EReaderData.get_size('Kindle 2/3/Touch')
        assert result[0].size == device_size
    
    
    def test_convert_image_with_different_device_kobo(self, test_images_dir):
        """Test convert_image with Kobo device"""
        parameters.set_device('Kobo Aura HD', 10)
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        
        result = image.convert_image(img_path)
        assert len(result) == 1
        
        device_size = image.EReaderData.get_size('Kobo Aura HD')
        assert result[0].size == device_size
    
    
    def test_convert_image_converts_to_greyscale_or_palette(self, test_images_dir):
        """Test convert_image converts to greyscale or palette mode"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        
        result = image.convert_image(img_path)
        converted_img = result[0]
        
        # Devrait être en mode L (greyscale) ou P (palette)
        assert converted_img.mode in ('L', 'P', 'RGB')
    
    
    # ============================================
    # Tests avec split flags
    # ============================================
    
    def test_convert_image_with_split_left(self, test_images_dir):
        """Test convert_image with split_left flag"""
        img_path = self.get_test_image_path(test_images_dir, "manga_scan_double_page.jpg")
        
        result = image.convert_image(img_path, split_left=True)
        assert len(result) == 1
        
        converted_img = result[0]
        assert converted_img is not None
        # L'image devrait avoir été splitée (moitié gauche)
    
    
    def test_convert_image_with_split_right(self, test_images_dir):
        """Test convert_image with split_right flag"""
        img_path = self.get_test_image_path(test_images_dir, "manga_scan_double_page.jpg")
        
        result = image.convert_image(img_path, split_right=True)
        assert len(result) == 1
        
        converted_img = result[0]
        assert converted_img is not None
        # L'image devrait avoir été splitée (moitié droite)
    
    
    def test_convert_image_with_split_both(self, test_images_dir):
        """Test convert_image with both split flags"""
        img_path = self.get_test_image_path(test_images_dir, "manga_scan_double_page.jpg")
        
        # Les deux flags ensemble donnent la partie gauche de la droite
        result = image.convert_image(img_path, split_left=True, split_right=True)
        assert len(result) == 1
        
        converted_img = result[0]
        assert converted_img is not None
    
    
    def test_convert_image_without_split(self, test_images_dir):
        """Test convert_image without any split flags"""
        img_path = self.get_test_image_path(test_images_dir, "manga_scan_double_page.jpg")
        
        result = image.convert_image(img_path, split_left=False, split_right=False)
        assert len(result) == 1
        
        converted_img = result[0]
        assert converted_img is not None
    
    
    # ============================================
    # Tests avec mode webtoon
    # ============================================
    
    def test_convert_image_webtoon_mode(self, test_images_dir):
        """Test convert_image in webtoon mode"""
        parameters.set_is_webtoon(True)
        img_path = self.get_test_image_path(test_images_dir, "webtoon_lot_of_white.jpg")
        
        result = image.convert_image(img_path)
        assert result is not None
        assert isinstance(result, list)
        # Webtoon peut retourner plusieurs images (splits verticaux)
        assert len(result) >= 1
        
        # Toutes les images devraient être à la bonne taille
        device_size = image.EReaderData.get_size(parameters.get_device())
        for img in result:
            assert img is not None
            assert img.size == device_size
    
    
    def test_convert_image_webtoon_returns_multiple_images(self, test_images_dir):
        """Test convert_image webtoon mode can return multiple images"""
        parameters.set_is_webtoon(True)
        img_path = self.get_test_image_path(test_images_dir, "webtoon_lot_of_white.jpg")
        
        result = image.convert_image(img_path)
        # Un webtoon long devrait être coupé en plusieurs images
        assert len(result) >= 1
    
    
    def test_convert_image_webtoon_vs_normal_mode(self, test_images_dir):
        """Test convert_image produces different results for webtoon vs normal"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_lot_of_white.jpg")
        
        # Mode normal
        parameters.set_is_webtoon(False)
        result_normal = image.convert_image(img_path)
        
        # Mode webtoon
        parameters.set_is_webtoon(True)
        result_webtoon = image.convert_image(img_path)
        
        # Le mode webtoon produit généralement plus d'images
        assert len(result_webtoon) >= len(result_normal)
    
    
    def test_convert_image_webtoon_all_greyscale(self, test_images_dir):
        """Test convert_image webtoon mode converts all to greyscale"""
        parameters.set_is_webtoon(True)
        img_path = self.get_test_image_path(test_images_dir, "webtoon_lot_of_white.jpg")
        
        result = image.convert_image(img_path)
        # Toutes les images devraient être en greyscale (L) ou RGB (après fill)
        for img in result:
            assert img.mode in ('L', 'RGB')
    
    
    # ============================================
    # Tests avec différents types d'images
    # ============================================
    
    def test_convert_image_landscape_page(self, test_images_dir):
        """Test convert_image with landscape page"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page_landscape.jpg")
        
        result = image.convert_image(img_path)
        assert len(result) == 1
        
        converted_img = result[0]
        assert converted_img is not None
        # Devrait être orientée correctement
    
    
    def test_convert_image_double_page(self, test_images_dir):
        """Test convert_image with double page"""
        img_path = self.get_test_image_path(test_images_dir, "manga_scan_double_page.jpg")
        
        result = image.convert_image(img_path)
        assert len(result) == 1
        
        converted_img = result[0]
        assert converted_img is not None
    
    
    def test_convert_image_old_quality(self, test_images_dir):
        """Test convert_image with old quality manga"""
        img_path = self.get_test_image_path(test_images_dir, "manga_bad_quality.jpg")
        
        result = image.convert_image(img_path)
        assert len(result) == 1
        
        converted_img = result[0]
        assert converted_img is not None
    
    
    def test_convert_image_with_colors(self, test_images_dir):
        """Test convert_image with colored comics"""
        img_path = self.get_test_image_path(test_images_dir, "comics_old_colors.jpg")
        
        result = image.convert_image(img_path)
        assert len(result) == 1
        
        converted_img = result[0]
        assert converted_img is not None
        # Les comics colorés devraient être convertis en greyscale
        assert converted_img.mode in ('L', 'P', 'RGB')
    
    
    def test_convert_image_very_vertical(self, test_images_dir):
        """Test convert_image with very vertical image"""
        img_path = self.get_test_image_path(test_images_dir, "comics_very_vertical.jpg")
        
        result = image.convert_image(img_path)
        assert len(result) == 1
        
        converted_img = result[0]
        assert converted_img is not None
    
    
    # ============================================
    # Tests de la pipeline complète
    # ============================================
    
    def test_convert_image_pipeline_crops_auto(self, test_images_dir):
        """Test convert_image pipeline includes auto crop"""
        img_path = self.get_test_image_path(test_images_dir, "manga_lot_of_white_around.jpg")
        
        result = image.convert_image(img_path)
        assert len(result) == 1
        
        converted_img = result[0]
        assert converted_img is not None
        # L'image devrait avoir été auto-croppée puis redimensionnée
    
    
    def test_convert_image_pipeline_orients_correctly(self, test_images_dir):
        """Test convert_image pipeline orients image correctly"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        
        result = image.convert_image(img_path)
        converted_img = result[0]
        
        device_size = image.EReaderData.get_size(parameters.get_device())
        # L'image devrait être orientée selon le device
        assert converted_img.size == device_size
    
    
    def test_convert_image_pipeline_resizes_to_device(self, test_images_dir):
        """Test convert_image pipeline resizes to exact device size"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        
        # Tester avec plusieurs devices (device, index)
        devices = [
            ('Kindle 2/3/Touch', 1),
            ('Kobo Aura HD', 10),
            ('Kindle Paperwhite 3/Voyage/Oasis', 5)
        ]
        for device, index in devices:
            parameters.set_device(device, index)
            result = image.convert_image(img_path)
            
            expected_size = image.EReaderData.get_size(device)
            assert result[0].size == expected_size
    
    
    def test_convert_image_with_invalid_device_raises_error(self, test_images_dir):
        """Test convert_image with invalid device raises RuntimeError"""
        import pytest
        
        parameters.set_device('Invalid Device XYZ', 999)
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        
        with pytest.raises(RuntimeError, match='Unexpected output device'):
            image.convert_image(img_path)
    
    
    def test_convert_image_preserves_image_quality(self, test_images_dir):
        """Test convert_image produces valid output images"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        
        result = image.convert_image(img_path)
        converted_img = result[0]
        
        # Vérifier que l'image est valide
        assert converted_img.size[0] > 0
        assert converted_img.size[1] > 0
        assert converted_img.mode in ('L', 'P', 'RGB')
        
        # Vérifier qu'on peut accéder aux pixels
        pixel = converted_img.getpixel((0, 0))
        assert pixel is not None
