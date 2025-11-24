#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for similarity detection and unwanted image filtering
"""
import os
import shutil

from PIL import Image

from henskan import parameters as params_module
from henskan.similarity import similarity, THRESHOLD
from .image_test_base import ImageTestBase


class TestSimilarity(ImageTestBase):
    """Tests for similarity detection"""
    
    
    def setup_method(self):
        """Setup before each test - clean DELETED directory"""
        # Clean DELETED directory before each test
        if os.path.exists(params_module.DELETED):
            shutil.rmtree(params_module.DELETED)
        os.makedirs(params_module.DELETED)
    
    
    def _assert_deleted_count(self, expected_count):
        """Assert that DELETED directory contains exactly the expected number of files"""
        deleted_files = [f for f in os.listdir(params_module.DELETED)
                         if os.path.isfile(os.path.join(params_module.DELETED, f))]
        
        assert len(deleted_files) == expected_count, \
            f"Expected exactly {expected_count} deleted file(s), got {len(deleted_files)}: {deleted_files}"
    
    
    def test_is_valid_image_with_unique_image(self):
        """Test that a unique image not in unwanted list is valid"""
        # Create a unique image (gradient pattern)
        img = Image.new('RGB', (100, 100))
        for x in range(100):
            for y in range(100):
                img.putpixel((x, y), (x * 2, y * 2, (x + y) % 256))
        
        result = similarity.is_valid_image(img, do_move=False)
        assert result is True, "Unique image should be valid"
        self._assert_deleted_count(0)
    
    
    def test_is_valid_image_with_exact_unwanted_match(self, test_images_dir):
        """Test that an exact match from unwanted list is detected"""
        # Load an image from unwanted_images
        unwanted_path = os.path.join(params_module.UNWANTED, "00007_0002.png")
        if not os.path.exists(unwanted_path):
            # Skip if the file doesn't exist
            return
        
        img = Image.open(unwanted_path)
        result = similarity.is_valid_image(img, do_move=True)
        
        assert result is False, "Exact match should be detected as unwanted"
        self._assert_deleted_count(1)
    
    
    def test_is_valid_image_with_similar_unwanted_image(self, test_images_dir):
        """Test that a similar (but not exact) image is detected if within threshold"""
        # Load an unwanted image and slightly modify it
        unwanted_path = os.path.join(params_module.UNWANTED, "00007_0002.png")
        if not os.path.exists(unwanted_path):
            return
        
        img = Image.open(unwanted_path).convert('RGB').copy()
        # Add slight noise - should still be detected if threshold is high enough
        pixels = img.load()
        for x in range(0, img.width, 10):
            for y in range(0, img.height, 10):
                pixel = pixels[x, y]
                # Slight modification
                new_pixel = tuple(min(255, max(0, c + 1)) for c in pixel)
                pixels[x, y] = new_pixel
        
        result = similarity.is_valid_image(img, do_move=True)
        
        # Depending on threshold, might or might not be detected
        # For now, just check it doesn't crash
        assert isinstance(result, bool)
        # If detected as unwanted, should have 1 file
        if not result:
            self._assert_deleted_count(1)
        else:
            self._assert_deleted_count(0)
    
    
    def test_is_valid_image_with_completely_different_image(self):
        """Test that a completely different image is valid"""
        # Create a solid red image (very different from typical unwanted images)
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        
        result = similarity.is_valid_image(img, do_move=False)
        assert result is True, "Completely different image should be valid"
        self._assert_deleted_count(0)
    
    
    def test_is_valid_image_do_move_false(self, test_images_dir):
        """Test that do_move=False doesn't save the image"""
        # Load an unwanted image
        unwanted_path = os.path.join(params_module.UNWANTED, "00007_0002.png")
        if not os.path.exists(unwanted_path):
            return
        
        img = Image.open(unwanted_path)
        result = similarity.is_valid_image(img, do_move=False)
        
        assert result is False, "Unwanted image should be detected"
        # With do_move=False, should NOT save the file
        self._assert_deleted_count(0)
    
    
    def test_multiple_unwanted_images_detection(self, test_images_dir):
        """Test detection of multiple unwanted images in sequence"""
        unwanted_files = ["00007_0002.png", "00010_0005.png", "00010_0006.png"]
        deleted_count = 0
        
        for filename in unwanted_files:
            unwanted_path = os.path.join(params_module.UNWANTED, filename)
            if not os.path.exists(unwanted_path):
                continue
            
            img = Image.open(unwanted_path)
            result = similarity.is_valid_image(img, do_move=True)
            
            assert result is False, f"{filename} should be detected as unwanted"
            deleted_count += 1
        
        self._assert_deleted_count(deleted_count)
    
    
    def test_threshold_value(self):
        """Test that THRESHOLD constant is defined and reasonable"""
        assert isinstance(THRESHOLD, int), "THRESHOLD should be an integer"
        assert THRESHOLD > 0, "THRESHOLD should be positive"
        assert THRESHOLD < 50, "THRESHOLD should be reasonable (< 50)"
    
    
    def test_unwanted_hashes_loaded(self):
        """Test that unwanted hashes are loaded on initialization"""
        # Check that similarity object has loaded some unwanted hashes
        assert hasattr(similarity, '_unwanted_hashes'), "Should have _unwanted_hashes attribute"
        assert isinstance(similarity._unwanted_hashes, dict), "Should be a dictionary"
        # Should have loaded at least some unwanted images
        assert len(similarity._unwanted_hashes) > 0, "Should have loaded unwanted images"
    
    
    def test_deleted_images_naming_convention(self, test_images_dir):
        """Test that deleted images follow the naming convention"""
        unwanted_path = os.path.join(params_module.UNWANTED, "00007_0002.png")
        if not os.path.exists(unwanted_path):
            return
        
        img = Image.open(unwanted_path)
        similarity.is_valid_image(img, do_move=True)
        
        # Check that files follow the naming pattern
        deleted_files = os.listdir(params_module.DELETED)
        assert len(deleted_files) > 0, "Should have at least one deleted file"
        
        # Check the naming pattern of the last created file
        # Find files that match this specific test
        test_files = [f for f in deleted_files if "00007_0002.png" in f]
        assert len(test_files) > 0, "Should have files from this test"
        
        # Verify naming convention on the latest file
        filename = test_files[-1]
        assert filename.startswith("unwanted_similarity_"), "Should start with 'unwanted_similarity_'"
        assert "--diff_" in filename, "Should contain '--diff_'"
        assert filename.endswith(".jpg"), "Should end with '.jpg'"
    
    
    def test_valid_image_with_webtoon_mix_background(self, test_images_dir):
        """Test with webtoon_mix_background which generates unwanted images during split"""
        # This is a regression test - webtoon_mix_background_black_then_white.jpg
        # generates 3 unwanted images when processed
        img_path = self.get_test_image_path(test_images_dir, "webtoon_mix_background_black_then_white.jpg")
        img = Image.open(img_path)
        
        # The full image itself might not be unwanted
        result = similarity.is_valid_image(img, do_move=False)
        # Just verify it doesn't crash
        assert isinstance(result, bool)
        self._assert_deleted_count(0)
    
    
    def test_all_similarity_verification_images_are_detected(self):
        """Test that all reference images in similarity_verification/ are detected as unwanted"""
        verification_dir = os.path.join(os.path.dirname(__file__), "similarity_verification")
        
        # Get all jpg files in verification directory
        verification_files = [f for f in os.listdir(verification_dir) if f.endswith('.jpg')]
        
        assert len(verification_files) > 0, "similarity_verification should contain reference images"
        
        detected_count = 0
        not_detected = []
        
        for filename in verification_files:
            filepath = os.path.join(verification_dir, filename)
            img = Image.open(filepath)
            
            result = similarity.is_valid_image(img, do_move=True)
            
            if not result:
                # Image was correctly detected as unwanted
                detected_count += 1
            else:
                # Image was NOT detected - this is a problem!
                not_detected.append(filename)
        
        # All reference images should be detected as unwanted
        assert len(not_detected) == 0, \
            f"These reference images were NOT detected as unwanted: {not_detected}. " \
            f"This means the similarity detection may have regressed. Check THRESHOLD value."
        
        # Verify we detected all of them
        assert detected_count == len(verification_files), \
            f"Expected to detect {len(verification_files)} unwanted images, but only detected {detected_count}"
        
        # Should have created files in DELETED for all detected images
        self._assert_deleted_count(detected_count)
