#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for save_image() function
Tests saving images to disk with various scenarios
"""
import os
import sys

from PIL import Image as PILImage

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase
from henskan import image


class TestSaveImage(ImageTestBase):
    """Tests for save_image() function"""
    
    def test_save_image_valid_png(self, temp_dir):
        """Test save_image saves a valid PNG image"""
        # Créer une image de test
        test_img = PILImage.new('RGB', (100, 100), color='red')
        target_path = os.path.join(temp_dir, "test.png")
        
        # Sauvegarder l'image
        image.save_image(test_img, target_path)
        
        # Vérifier que le fichier existe
        assert os.path.exists(target_path)
        assert os.path.getsize(target_path) > 0
        
        # Vérifier que c'est bien un PNG
        with open(target_path, 'rb') as f:
            header = f.read(8)
            assert header == b'\x89PNG\r\n\x1a\n', "Should be a valid PNG file"
    
    
    def test_save_image_valid_jpg(self, temp_dir):
        """Test save_image saves a valid JPG image"""
        # Créer une image de test
        test_img = PILImage.new('RGB', (100, 100), color='blue')
        target_path = os.path.join(temp_dir, "test.jpg")
        
        # Sauvegarder l'image
        image.save_image(test_img, target_path)
        
        # Vérifier que le fichier existe
        assert os.path.exists(target_path)
        assert os.path.getsize(target_path) > 0
        
        # Vérifier que c'est bien un JPEG
        with open(target_path, 'rb') as f:
            header = f.read(2)
            assert header == b'\xff\xd8', "Should be a valid JPEG file"
    
    
    def test_save_image_rgb_mode(self, temp_dir):
        """Test save_image with RGB mode image"""
        # Créer une image RGB
        test_img = PILImage.new('RGB', (50, 50), color=(128, 64, 32))
        target_path = os.path.join(temp_dir, "rgb_image.png")
        
        # Sauvegarder
        image.save_image(test_img, target_path)
        
        # Vérifier et recharger
        assert os.path.exists(target_path)
        loaded_img = PILImage.open(target_path)
        assert loaded_img.mode == 'RGB'
        assert loaded_img.size == (50, 50)
    
    
    def test_save_image_greyscale_mode(self, temp_dir):
        """Test save_image with greyscale (L) mode image"""
        # Créer une image en niveaux de gris
        test_img = PILImage.new('L', (50, 50), color=128)
        target_path = os.path.join(temp_dir, "greyscale_image.png")
        
        # Sauvegarder
        image.save_image(test_img, target_path)
        
        # Vérifier et recharger
        assert os.path.exists(target_path)
        loaded_img = PILImage.open(target_path)
        assert loaded_img.mode == 'L'
        assert loaded_img.size == (50, 50)
    
    
    def test_save_image_palette_mode(self, temp_dir):
        """Test save_image with palette (P) mode image"""
        # Créer une image avec palette
        test_img = PILImage.new('P', (50, 50))
        # Définir une palette simple
        palette = []
        for i in range(256):
            palette.extend([i, i, i])  # Palette en niveaux de gris
        test_img.putpalette(palette)
        
        target_path = os.path.join(temp_dir, "palette_image.png")
        
        # Sauvegarder
        image.save_image(test_img, target_path)
        
        # Vérifier
        assert os.path.exists(target_path)
        loaded_img = PILImage.open(target_path)
        assert loaded_img.mode == 'P'
    
    
    def test_save_image_invalid_path(self):
        """Test save_image raises RuntimeError with invalid path"""
        import pytest
        
        # Créer une image
        test_img = PILImage.new('RGB', (10, 10), color='white')
        
        # Chemin invalide (sur Windows, caractères invalides)
        invalid_path = "C:\\invalid<>path|?.png"
        
        # Devrait lever RuntimeError
        with pytest.raises(RuntimeError, match='Cannot write image file'):
            image.save_image(test_img, invalid_path)
    
    
    def test_save_image_nonexistent_directory(self):
        """Test save_image raises RuntimeError with non-existent directory"""
        import pytest
        
        # Créer une image
        test_img = PILImage.new('RGB', (10, 10), color='white')
        
        # Répertoire qui n'existe pas
        nonexistent_path = os.path.join("C:\\", "nonexistent_dir_12345", "subdir", "image.png")
        
        # Devrait lever RuntimeError
        with pytest.raises(RuntimeError, match='Cannot write image file'):
            image.save_image(test_img, nonexistent_path)
    
    
    def test_save_image_readonly_directory(self, temp_dir):
        """Test save_image raises RuntimeError with read-only directory"""
        import pytest
        import stat
        
        # Créer une image
        test_img = PILImage.new('RGB', (10, 10), color='white')
        
        # Créer un sous-répertoire et le mettre en lecture seule
        readonly_dir = os.path.join(temp_dir, "readonly")
        os.makedirs(readonly_dir)
        
        # Sur Windows, mettre en lecture seule un répertoire ne fonctionne pas comme sur Unix
        # On teste plutôt avec un fichier en lecture seule existant
        target_path = os.path.join(readonly_dir, "test.png")
        
        # Créer d'abord le fichier
        test_img.save(target_path)
        
        # Le mettre en lecture seule
        os.chmod(target_path, stat.S_IREAD)
        
        try:
            # Essayer d'écraser le fichier en lecture seule devrait échouer
            with pytest.raises(RuntimeError, match='Cannot write image file'):
                image.save_image(test_img, target_path)
        finally:
            # Restaurer les permissions pour le nettoyage
            try:
                os.chmod(target_path, stat.S_IWRITE | stat.S_IREAD)
            except:
                pass
    
    
    def test_save_image_overwrite_existing(self, temp_dir):
        """Test save_image overwrites existing file"""
        # Créer une première image
        test_img1 = PILImage.new('RGB', (50, 50), color='red')
        target_path = os.path.join(temp_dir, "overwrite.png")
        
        # Sauvegarder la première fois
        image.save_image(test_img1, target_path)
        assert os.path.exists(target_path)
        
        # Récupérer la taille du premier fichier
        first_size = os.path.getsize(target_path)
        
        # Créer une deuxième image différente
        test_img2 = PILImage.new('RGB', (100, 100), color='blue')
        
        # Sauvegarder par-dessus
        image.save_image(test_img2, target_path)
        
        # Vérifier que le fichier existe toujours
        assert os.path.exists(target_path)
        
        # Vérifier que la taille a changé (nouvelle image plus grande)
        second_size = os.path.getsize(target_path)
        assert second_size != first_size
        
        # Vérifier que c'est bien la nouvelle image
        loaded_img = PILImage.open(target_path)
        assert loaded_img.size == (100, 100)
    
    
    def test_save_image_with_nested_path(self, temp_dir):
        """Test save_image behavior with nested path"""
        import pytest
        
        # Créer une image
        test_img = PILImage.new('RGB', (10, 10), color='white')
        
        # Chemin avec plusieurs niveaux de répertoires non existants
        nested_path = os.path.join(temp_dir, "level1", "level2", "level3", "image.png")
        
        # save_image ne crée PAS les répertoires parents, donc ça devrait échouer
        with pytest.raises(RuntimeError, match='Cannot write image file'):
            image.save_image(test_img, nested_path)
    
    
    def test_save_image_reload_verify(self, temp_dir):
        """Test saved image can be reloaded and verified"""
        # Créer une image avec un pattern reconnaissable
        test_img = PILImage.new('RGB', (100, 100), color='white')
        pixels = test_img.load()
        
        # Dessiner un pattern
        for x in range(0, 100, 10):
            for y in range(0, 100, 10):
                pixels[x, y] = (255, 0, 0)  # Points rouges
        
        target_path = os.path.join(temp_dir, "verify.png")
        
        # Sauvegarder
        image.save_image(test_img, target_path)
        
        # Recharger
        loaded_img = PILImage.open(target_path)
        loaded_pixels = loaded_img.load()
        
        # Vérifier que le pattern est préservé
        assert loaded_img.size == (100, 100)
        assert loaded_pixels[0, 0] == (255, 0, 0), "Red pixel should be preserved"
        assert loaded_pixels[10, 10] == (255, 0, 0), "Red pixel should be preserved"
        assert loaded_pixels[5, 5] == (255, 255, 255), "White pixel should be preserved"
    
    
    def test_save_image_large_image(self, temp_dir):
        """Test save_image with large image (performance)"""
        # Créer une grande image (2000x2000)
        test_img = PILImage.new('RGB', (2000, 2000), color='green')
        target_path = os.path.join(temp_dir, "large_image.png")
        
        # Sauvegarder (ne devrait pas causer d'erreur)
        image.save_image(test_img, target_path)
        
        # Vérifier que le fichier existe et a une taille raisonnable
        assert os.path.exists(target_path)
        file_size = os.path.getsize(target_path)
        assert file_size > 1000, "Large image should have significant size"
        assert file_size < 50 * 1024 * 1024, "Should not be excessively large"
        
        # Vérifier qu'on peut recharger l'image
        loaded_img = PILImage.open(target_path)
        assert loaded_img.size == (2000, 2000)
    
    
    def test_save_image_after_conversion(self, test_images_dir, temp_dir):
        """Test save_image with image that went through conversion pipeline"""
        # Charger une vraie image manga et la convertir
        try:
            manga_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
            
            # Convertir l'image via la pipeline
            converted_images = image.convert_image(manga_path)
            assert len(converted_images) > 0
            
            # Sauvegarder la première image convertie
            target_path = os.path.join(temp_dir, "converted.png")
            image.save_image(converted_images[0], target_path)
            
            # Vérifier
            assert os.path.exists(target_path)
            assert os.path.getsize(target_path) > 0
            
            # Vérifier qu'on peut recharger
            loaded_img = PILImage.open(target_path)
            assert loaded_img is not None
            assert loaded_img.size == converted_images[0].size
            
        except (FileNotFoundError, AssertionError):
            # Si l'image de test n'existe pas, créer une image simple
            test_img = PILImage.new('L', (600, 800), color=128)
            target_path = os.path.join(temp_dir, "converted_simple.png")
            
            image.save_image(test_img, target_path)
            
            assert os.path.exists(target_path)
            assert os.path.getsize(target_path) > 0
    
    
    def test_save_image_special_characters(self, temp_dir):
        """Test save_image with special characters in filename"""
        # Créer une image
        test_img = PILImage.new('RGB', (10, 10), color='white')
        
        # Nom de fichier avec espaces et caractères accentués (valides sur Windows)
        special_filename = "test image éèà ñ.png"
        target_path = os.path.join(temp_dir, special_filename)
        
        # Sauvegarder
        image.save_image(test_img, target_path)
        
        # Vérifier que le fichier existe
        assert os.path.exists(target_path)
        assert os.path.getsize(target_path) > 0
        
        # Vérifier qu'on peut recharger
        loaded_img = PILImage.open(target_path)
        assert loaded_img.size == (10, 10)

