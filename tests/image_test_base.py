#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base class and fixtures for image tests
"""
import os
import shutil
import tempfile

import pytest


class ImageTestBase:
    """Base class for all image tests with common fixtures and helpers"""
    
    
    @pytest.fixture
    def test_images_dir(self):
        """Get the test images directory path"""
        return os.path.join(os.path.dirname(__file__), "images")
    
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        # Cleanup after test
        shutil.rmtree(temp_path, ignore_errors=True)
    
    
    def get_test_image_path(self, test_images_dir, filename):
        """Get full path to a test image"""
        return os.path.join(test_images_dir, filename)
    
    
    def image_exists(self, test_images_dir, filename):
        """Check if test image exists"""
        return os.path.exists(self.get_test_image_path(test_images_dir, filename))
