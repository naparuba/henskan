#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for ArchiveCBZ class
"""
import os
import sys
import tempfile
import shutil
from zipfile import ZipFile
from pathlib import Path

# Add parent directory to path to import henskan modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from henskan.archive_cbz import ArchiveCBZ


class TestArchiveCBZ:
    """Test suite for ArchiveCBZ class"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        # Cleanup after test
        shutil.rmtree(temp_path, ignore_errors=True)
    
    @pytest.fixture
    def temp_image_file(self, temp_dir):
        """Create a temporary test image file"""
        # Create a simple dummy file to simulate an image
        test_file = os.path.join(temp_dir, "test_image.jpg")
        with open(test_file, 'wb') as f:
            # Write some dummy data (1KB)
            f.write(b'0' * 1024)
        return test_file
    
    @pytest.fixture
    def temp_large_image_file(self, temp_dir):
        """Create a large temporary test file (10MB)"""
        test_file = os.path.join(temp_dir, "large_image.jpg")
        with open(test_file, 'wb') as f:
            # Write 10MB of dummy data
            f.write(b'0' * (10 * 1024 * 1024))
        return test_file
    
    def test_create_cbz_basic(self, temp_dir):
        """Test basic CBZ creation"""
        output_path = os.path.join(temp_dir, "test_archive")
        
        archive = ArchiveCBZ(output_path)
        assert archive is not None
        archive.close()
        
        # Check that the CBZ file was created
        expected_cbz = os.path.join(temp_dir, "test_archive.cbz")
        assert os.path.exists(expected_cbz)
    
    def test_add_single_file(self, temp_dir, temp_image_file):
        """Test adding a single file to CBZ"""
        output_path = os.path.join(temp_dir, "test_archive")
        
        archive = ArchiveCBZ(output_path)
        archive.add(temp_image_file)
        archive.close()
        
        # Verify the CBZ contains the file
        cbz_path = os.path.join(temp_dir, "test_archive.cbz")
        with ZipFile(cbz_path, 'r') as zf:
            namelist = zf.namelist()
            assert len(namelist) == 1
            assert "test_image.jpg" in namelist
    
    def test_add_multiple_files(self, temp_dir):
        """Test adding multiple files to CBZ"""
        output_path = os.path.join(temp_dir, "test_archive")
        
        # Create multiple test files
        test_files = []
        for i in range(5):
            test_file = os.path.join(temp_dir, f"image_{i:03d}.jpg")
            with open(test_file, 'wb') as f:
                f.write(b'0' * 1024)
            test_files.append(test_file)
        
        archive = ArchiveCBZ(output_path)
        for test_file in test_files:
            archive.add(test_file)
        archive.close()
        
        # Verify all files are in the CBZ
        cbz_path = os.path.join(temp_dir, "test_archive.cbz")
        with ZipFile(cbz_path, 'r') as zf:
            namelist = zf.namelist()
            assert len(namelist) == 5
            for i in range(5):
                assert f"image_{i:03d}.jpg" in namelist
    
    def test_custom_max_size(self, temp_dir):
        """Test creating CBZ with custom max size"""
        output_path = os.path.join(temp_dir, "test_archive")
        custom_max_size = 1024 * 1024  # 1MB
        
        archive = ArchiveCBZ(output_path, max_size=custom_max_size)
        assert archive._max_size == custom_max_size
        archive.close()
    
    def test_split_on_size_limit(self, temp_dir):
        """Test that CBZ splits when size limit is reached"""
        output_path = os.path.join(temp_dir, "test_archive")
        
        # Set a small max size to force splitting (5MB)
        small_max_size = 5 * 1024 * 1024
        
        archive = ArchiveCBZ(output_path, max_size=small_max_size)
        
        # Add files that will exceed the limit
        for i in range(3):
            test_file = os.path.join(temp_dir, f"large_{i}.jpg")
            with open(test_file, 'wb') as f:
                # Write 3MB per file = 9MB total > 5MB limit
                f.write(b'0' * (3 * 1024 * 1024))
            archive.add(test_file)
        
        archive.close()
        
        # Should have created 2 parts (first 5MB, second 4MB)
        part1_path = os.path.join(temp_dir, "test_archive.cbz")
        part2_path = os.path.join(temp_dir, "test_archive_part2.cbz")
        
        assert os.path.exists(part1_path)
        assert os.path.exists(part2_path)
        
        # Verify both parts contain files
        with ZipFile(part1_path, 'r') as zf:
            assert len(zf.namelist()) > 0
        
        with ZipFile(part2_path, 'r') as zf:
            assert len(zf.namelist()) > 0
    
    def test_filename_only_in_archive(self, temp_dir, temp_image_file):
        """Test that only filename is stored in archive, not full path"""
        output_path = os.path.join(temp_dir, "test_archive")
        
        archive = ArchiveCBZ(output_path)
        archive.add(temp_image_file)
        archive.close()
        
        cbz_path = os.path.join(temp_dir, "test_archive.cbz")
        with ZipFile(cbz_path, 'r') as zf:
            namelist = zf.namelist()
            # Should only have filename, not full path
            assert namelist[0] == "test_image.jpg"
            assert "/" not in namelist[0] or "\\" not in namelist[0]
    
    def test_add_chapter_does_nothing(self, temp_dir):
        """Test that add_chapter method exists but does nothing for CBZ"""
        output_path = os.path.join(temp_dir, "test_archive")
        
        archive = ArchiveCBZ(output_path)
        # Should not raise an error
        archive.add_chapter("Chapter 1")
        archive.close()
    
    def test_default_max_size(self, temp_dir):
        """Test that default max size is set correctly"""
        output_path = os.path.join(temp_dir, "test_archive")
        
        archive = ArchiveCBZ(output_path)
        assert archive._max_size == ArchiveCBZ.DEFAULT_MAX_SIZE
        assert archive._max_size == 1500 * 1024 * 1024  # 1.5GB
        archive.close()
    
    def test_current_part_starts_at_one(self, temp_dir):
        """Test that part numbering starts at 1"""
        output_path = os.path.join(temp_dir, "test_archive")
        
        archive = ArchiveCBZ(output_path)
        assert archive._current_part == 1
        archive.close()
    
    def test_all_output_paths_tracking(self, temp_dir):
        """Test that all output paths are tracked"""
        output_path = os.path.join(temp_dir, "test_archive")
        small_max_size = 2 * 1024 * 1024  # 2MB
        
        archive = ArchiveCBZ(output_path, max_size=small_max_size)
        
        # Add files to create multiple parts
        for i in range(3):
            test_file = os.path.join(temp_dir, f"file_{i}.jpg")
            with open(test_file, 'wb') as f:
                f.write(b'0' * int(1.5 * 1024 * 1024))  # 1.5MB each
            archive.add(test_file)
        
        archive.close()
        
        # Should have tracked all created parts
        assert len(archive._all_output_paths) >= 2
        for path in archive._all_output_paths:
            assert os.path.exists(path)
    
    def test_get_current_size(self, temp_dir, temp_image_file):
        """Test _get_current_size method"""
        output_path = os.path.join(temp_dir, "test_archive")
        
        archive = ArchiveCBZ(output_path)
        
        # Initially should be small
        initial_size = archive._get_current_size()
        
        # Add a file
        archive.add(temp_image_file)
        
        # Size should increase
        new_size = archive._get_current_size()
        assert new_size > initial_size
        
        archive.close()
    
    def test_should_split_logic(self, temp_dir):
        """Test _should_split method logic"""
        output_path = os.path.join(temp_dir, "test_archive")
        max_size = 1024 * 1024  # 1MB
        
        archive = ArchiveCBZ(output_path, max_size=max_size)
        
        # Small file should not trigger split
        assert not archive._should_split(100)
        
        # Large file exceeding max size should trigger split
        assert archive._should_split(2 * 1024 * 1024)
        
        archive.close()


if __name__ == '__main__':
    # Allow running this test file directly
    pytest.main([__file__, '-v'])

