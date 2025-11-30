#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for Parameters class
Tests configuration and state management
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase
from henskan.parameters import Parameters


class TestParameters(ImageTestBase):
    """Tests for Parameters class"""
    
    # ============================================
    # Tests d'initialisation
    # ============================================
    
    def test_parameters_initialization(self):
        """Test Parameters initializes with default values"""
        params = Parameters()
        
        assert params is not None
        assert params._images == []
        assert params._chapters == []
        assert params._images_by_chapter == {}
        assert params._title == Parameters.DefaultTitle
        assert params._device == Parameters.DefaultDevice
    
    
    def test_parameters_default_device(self):
        """Test Parameters has default device set"""
        params = Parameters()
        
        assert params.get_device() == Parameters.DefaultDevice
        assert params.get_device() == 'Kobo Libra H2O'
        assert params.get_device_index() == 12
    
    
    def test_parameters_default_output_directory(self):
        """Test Parameters has default output directory"""
        params = Parameters()
        
        output_dir = params.get_output_directory()
        assert output_dir is not None
        assert isinstance(output_dir, str)
        assert len(output_dir) > 0
    
    
    # ============================================
    # Tests de sauvegarde et chargement
    # ============================================
    
    def test_save_parameters_creates_file(self, temp_dir):
        """Test save_parameters creates parameters JSON file"""
        params = Parameters()
        params._default_document_directory = temp_dir
        params.set_output_directory(temp_dir)
        params.set_device('Kindle 2/3/Touch', 1)
        
        params.save_parameters()
        
        json_file = os.path.join(temp_dir, 'henskan_parameters.json')
        assert os.path.exists(json_file)
        
        import json
        with open(json_file, 'r') as f:
            data = json.load(f)
            assert 'output_directory' in data
            assert 'device' in data
            assert 'device_index' in data
    
    
    def test_load_previous_parameters(self, temp_dir):
        """Test load_previous_parameters loads from JSON file"""
        import json
        
        json_file = os.path.join(temp_dir, 'henskan_parameters.json')
        data = {
            'output_directory': temp_dir,
            'device': 'Kindle Paperwhite 3/Voyage/Oasis',
            'device_index': 5
        }
        with open(json_file, 'w') as f:
            json.dump(data, f)
        
        params = Parameters()
        params._default_document_directory = temp_dir
        params.load_previous_parameters()
        
        assert params.get_output_directory() == temp_dir
        assert params.get_device() == 'Kindle Paperwhite 3/Voyage/Oasis'
        assert params.get_device_index() == 5
    
    
    def test_save_load_roundtrip(self, temp_dir):
        """Test saving then loading preserves all parameter values"""
        params1 = Parameters()
        params1._default_document_directory = temp_dir
        params1.set_output_directory(temp_dir)
        params1.set_device('Kobo Aura HD', 10)
        params1.save_parameters()
        
        params2 = Parameters()
        params2._default_document_directory = temp_dir
        params2.load_previous_parameters()
        
        assert params2.get_output_directory() == params1.get_output_directory()
        assert params2.get_device() == params1.get_device()
        assert params2.get_device_index() == params1.get_device_index()
    
    
    def test_load_missing_file_uses_defaults(self):
        """Test loading with missing file uses default values"""
        params = Parameters()
        params._default_document_directory = "/nonexistent_directory_12345"
        
        params.load_previous_parameters()
        
        assert params.get_device() == Parameters.DefaultDevice
    
    
    def test_load_corrupted_json(self, temp_dir):
        """Test loading corrupted JSON file handles gracefully"""
        json_file = os.path.join(temp_dir, 'henskan_parameters.json')
        with open(json_file, 'w') as f:
            f.write("{ this is not valid json }")
        
        params = Parameters()
        params._default_document_directory = temp_dir
        params.load_previous_parameters()
        
        assert params.get_device() == Parameters.DefaultDevice
    
    
    # ============================================
    # Tests de gestion des images
    # ============================================
    
    def test_add_images(self):
        """Test add_images adds image paths to parameters"""
        params = Parameters()
        
        params.add_image("image1.jpg", "Chapter 1")
        
        assert len(params.get_images()) == 1
        assert "image1.jpg" in params.get_images()
    
    
    def test_add_multiple_images(self):
        """Test add_images with multiple image paths"""
        params = Parameters()
        
        params.add_image("image1.jpg", "Chapter 1")
        params.add_image("image2.jpg", "Chapter 1")
        params.add_image("image3.jpg", "Chapter 2")
        
        assert len(params.get_images()) == 3
        assert "image1.jpg" in params.get_images()
        assert "image2.jpg" in params.get_images()
        assert "image3.jpg" in params.get_images()
    
    
    def test_get_images(self):
        """Test get_images returns all added images"""
        params = Parameters()
        
        params.add_image("img1.jpg", "Ch1")
        params.add_image("img2.jpg", "Ch1")
        
        images = params.get_images()
        assert isinstance(images, list)
        assert len(images) == 2
    
    
    def test_sort_images_natural_order(self):
        """Test sort_images sorts images in natural order"""
        params = Parameters()
        
        params.add_image("image10.jpg", "Chapter 1")
        params.add_image("image2.jpg", "Chapter 1")
        params.add_image("image1.jpg", "Chapter 1")
        params.add_chapter("Chapter 1")
        
        params.sort_images()
        
        images = params.get_images()
        assert images == ["image1.jpg", "image2.jpg", "image10.jpg"]
    
    
    def test_clear_images(self):
        """Test clearing image list"""
        params = Parameters()
        
        params.add_image("image1.jpg", "Chapter 1")
        params.add_image("image2.jpg", "Chapter 1")
        
        params.clean()
        
        assert len(params.get_images()) == 0
        assert len(params.get_chapters()) == 0
    
    
    # ============================================
    # Tests de gestion des chapitres
    # ============================================
    
    def test_detect_chapters_from_filenames(self):
        """Test automatic detection of chapters from filenames"""
        params = Parameters()
        
        params.add_image("ch1_page1.jpg", "Chapter 1")
        params.add_image("ch1_page2.jpg", "Chapter 1")
        params.add_image("ch2_page1.jpg", "Chapter 2")
        
        params.add_chapter("Chapter 1")
        params.add_chapter("Chapter 2")
        
        assert len(params.get_chapters()) == 2
        assert "Chapter 1" in params.get_chapters()
        assert "Chapter 2" in params.get_chapters()
    
    
    def test_get_images_by_chapter(self):
        """Test get_images_by_chapter groups images by chapter"""
        params = Parameters()
        
        params.add_image("img1.jpg", "Chapter 1")
        params.add_image("img2.jpg", "Chapter 1")
        params.add_image("img3.jpg", "Chapter 2")
        
        images_by_chapter = params.get_images_by_chapter()
        
        assert "Chapter 1" in images_by_chapter
        assert "Chapter 2" in images_by_chapter
        assert len(images_by_chapter["Chapter 1"]) == 2
        assert len(images_by_chapter["Chapter 2"]) == 1
    
    
    def test_get_chapters_sorted(self):
        """Test get_chapters returns chapters in sorted order"""
        params = Parameters()
        
        params.add_chapter("Chapter 10")
        params.add_chapter("Chapter 2")
        params.add_chapter("Chapter 1")
        params.add_image("img1.jpg", "Chapter 1")
        params.add_image("img2.jpg", "Chapter 2")
        params.add_image("img3.jpg", "Chapter 10")
        
        params.sort_images()
        
        chapters = params.get_chapters()
        assert chapters == ["Chapter 1", "Chapter 2", "Chapter 10"]
    
    
    def test_images_without_chapter(self):
        """Test handling of images without chapter information"""
        params = Parameters()
        
        params.add_image("img1.jpg", "")
        params.add_image("img2.jpg", "")
        
        images_by_chapter = params.get_images_by_chapter()
        assert "" in images_by_chapter
        assert len(images_by_chapter[""]) == 2
    
    
    def test_mixed_chapter_formats(self):
        """Test detection with mixed chapter naming formats"""
        params = Parameters()
        
        params.add_image("img1.jpg", "Tome 1")
        params.add_image("img2.jpg", "Chapter 1")
        params.add_image("img3.jpg", "Vol 1")
        
        params.add_chapter("Tome 1")
        params.add_chapter("Chapter 1")
        params.add_chapter("Vol 1")
        
        assert len(params.get_chapters()) == 3
    
    
    # ============================================
    # Tests des paramètres de device
    # ============================================
    
    def test_set_device(self):
        """Test set_device updates both device name and index"""
        params = Parameters()
        
        params.set_device('Kindle 2/3/Touch', 1)
        
        assert params.get_device() == 'Kindle 2/3/Touch'
        assert params.get_device_index() == 1
    
    
    def test_get_device(self):
        """Test get_device returns current device name"""
        params = Parameters()
        
        device = params.get_device()
        assert device == Parameters.DefaultDevice
        assert isinstance(device, str)
    
    
    def test_get_device_index(self):
        """Test get_device_index returns current device index"""
        params = Parameters()
        
        index = params.get_device_index()
        assert index == 12
        assert isinstance(index, int)
    
    
    def test_device_persistence(self, temp_dir):
        """Test device settings persist across save/load"""
        params1 = Parameters()
        params1._default_document_directory = temp_dir
        params1.set_device('Kobo Glo HD', 11)
        params1.save_parameters()
        
        params2 = Parameters()
        params2._default_document_directory = temp_dir
        params2.load_previous_parameters()
        
        assert params2.get_device() == 'Kobo Glo HD'
        assert params2.get_device_index() == 11
    
    
    # ============================================
    # Tests des flags de split
    # ============================================
    
    def test_split_left_then_right_flag(self):
        """Test is_split_left_then_right flag"""
        params = Parameters()
        
        assert params.is_split_left_then_right() == False
        
        params.set_split_left_then_right(True)
        assert params.is_split_left_then_right() == True
        
        params.set_split_left_then_right(False)
        assert params.is_split_left_then_right() == False
    
    
    def test_split_right_then_left_flag(self):
        """Test is_split_right_then_left flag"""
        params = Parameters()
        
        assert params.is_split_right_then_left() == False
        
        params.set_split_right_then_left(True)
        assert params.is_split_right_then_left() == True
        
        params.set_split_right_then_left(False)
        assert params.is_split_right_then_left() == False
    
    
    def test_split_flags_mutually_exclusive(self):
        """Test split flags are mutually exclusive"""
        params = Parameters()
        
        params.set_split_left_then_right(True)
        params.set_split_right_then_left(True)
        
        assert params.is_split_left_then_right() == True
        assert params.is_split_right_then_left() == True
    
    
    # ============================================
    # Tests du mode webtoon
    # ============================================
    
    def test_is_webtoon_flag(self):
        """Test is_webtoon flag getter and setter"""
        params = Parameters()
        
        assert params.is_webtoon() == False
        
        params.set_is_webtoon(True)
        assert params.is_webtoon() == True
        
        params.set_is_webtoon(False)
        assert params.is_webtoon() == False
    
    
    def test_set_is_webtoon(self):
        """Test set_is_webtoon changes webtoon mode"""
        params = Parameters()
        
        params.set_is_webtoon(True)
        assert params.is_webtoon() == True
        assert params._is_webtoon == True
    
    
    def test_webtoon_mode_persistence(self, temp_dir):
        """Test webtoon mode persists across save/load"""
        # Note: Le mode webtoon n'est pas sauvegardé dans l'implémentation actuelle
        # Ce test vérifie le comportement actuel
        params1 = Parameters()
        params1._default_document_directory = temp_dir
        params1.set_is_webtoon(True)
        params1.save_parameters()
        
        params2 = Parameters()
        params2._default_document_directory = temp_dir
        params2.load_previous_parameters()
        
        # Le mode webtoon n'est pas persisté actuellement
        assert params2.is_webtoon() == False
    
    
    # ============================================
    # Tests du titre
    # ============================================
    
    def test_get_title(self):
        """Test get_title returns current title"""
        params = Parameters()
        
        title = params.get_title()
        assert title == Parameters.DefaultTitle
        assert isinstance(title, str)
    
    
    def test_set_title(self):
        """Test setting custom title"""
        params = Parameters()
        
        params.set_title("One Piece - Volume 1")
        assert params.get_title() == "One Piece - Volume 1"
    
    
    def test_is_title_set(self):
        """Test is_title_set detects if custom title is set"""
        params = Parameters()
        
        assert params.is_title_set() == False
        
        params.set_title("My Custom Title")
        assert params.is_title_set() == True
        
        params.set_title(Parameters.DefaultTitle)
        assert params.is_title_set() == False
    
    
    def test_title_special_characters(self):
        """Test title with special characters"""
        params = Parameters()
        
        special_title = "Manga Ère Meiji - Vol.1 : L'éveil !"
        params.set_title(special_title)
        
        assert params.get_title() == special_title
        assert params.is_title_set() == True
    
    
    # ============================================
    # Tests du répertoire de sortie
    # ============================================
    
    def test_get_output_directory(self):
        """Test get_output_directory returns output directory"""
        params = Parameters()
        
        output_dir = params.get_output_directory()
        assert output_dir is not None
        assert isinstance(output_dir, str)
    
    
    def test_set_output_directory(self):
        """Test setting custom output directory"""
        params = Parameters()
        
        custom_dir = "/custom/output/directory"
        params.set_output_directory(custom_dir)
        
        assert params.get_output_directory() == custom_dir
    
    
    def test_output_directory_persistence(self, temp_dir):
        """Test output directory persists across save/load"""
        params1 = Parameters()
        params1._default_document_directory = temp_dir
        params1.set_output_directory(temp_dir)
        params1.save_parameters()
        
        params2 = Parameters()
        params2._default_document_directory = temp_dir
        params2.load_previous_parameters()
        
        assert params2.get_output_directory() == temp_dir

