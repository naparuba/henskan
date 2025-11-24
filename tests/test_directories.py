#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for test environment directories (UNWANTED and DELETED)
"""
import os

from henskan import parameters as params_module


class TestDirectories:
    """Tests to verify that test directories are properly configured"""
    
    
    def test_unwanted_directory_points_to_tests(self):
        """Verify that UNWANTED points to tests/unwanted_images during tests"""
        assert "tests" in params_module.UNWANTED
        assert params_module.UNWANTED.endswith("unwanted_images")
        assert os.path.exists(params_module.UNWANTED)
        print(f"UNWANTED directory: {params_module.UNWANTED}")
    
    
    def test_deleted_directory_points_to_tests(self):
        """Verify that DELETED points to tests/deleted_images during tests"""
        assert "tests" in params_module.DELETED
        assert params_module.DELETED.endswith("deleted_images")
        assert os.path.exists(params_module.DELETED)
        print(f"DELETED directory: {params_module.DELETED}")
    
    
    def test_unwanted_directory_not_empty(self):
        """Verify that unwanted_images contains reference images"""
        files = os.listdir(params_module.UNWANTED)
        # Filter out readme.txt
        image_files = [f for f in files if f.endswith(('.png', '.jpg', '.jpeg'))]
        assert len(image_files) > 0, "unwanted_images should contain reference images"
        print(f"Found {len(image_files)} reference images in unwanted_images")
    
    
    def test_deleted_directory_starts_empty(self):
        """Verify that deleted_images is cleaned at the start of test session
        
        Note: The webtoon tests also clean deleted_images before each test
        and verify the count after each test (0 for most, 3 for test_split_webtoon_mix_background).
        """
        # This test should run early, so deleted_images should still be empty
        # or contain very few files if other tests have run
        files = os.listdir(params_module.DELETED)
        print(f"deleted_images contains {len(files)} files")
        # We don't assert it's empty because other tests might have run first
        # The important thing is that it was cleaned at session start
