#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for image helper functions and utilities
"""
import os

from .image_test_base import ImageTestBase


class TestImageHelpers(ImageTestBase):
    """Test helper functions and utilities"""
    
    
    def test_test_images_directory_exists(self, test_images_dir):
        """Test that the test images directory exists"""
        assert os.path.exists(test_images_dir)
        assert os.path.isdir(test_images_dir)
    
    
    def test_test_images_are_present(self, test_images_dir):
        """Test that we have at least some test images"""
        jpg_files = [f for f in os.listdir(test_images_dir) if f.endswith('.jpg')]
        assert len(jpg_files) > 0, "No test images found in tests/images/"
    
    
    def test_temp_dir_fixture(self, temp_dir):
        """Test that temp directory fixture works"""
        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)
        
        # Test we can create a file in it
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        assert os.path.exists(test_file)
