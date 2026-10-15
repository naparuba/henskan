#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for image type detection (manga vs webtoon)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase
from henskan.webtoon import guess_manga_or_webtoon_image


class TestImageDetection(ImageTestBase):
    """Tests for image type detection (manga vs webtoon)"""
    
    
    def test_detect_manga_portrait(self, test_images_dir):
        """Test detection of portrait manga (not webtoon)"""
        img_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
        result = guess_manga_or_webtoon_image(img_path)
        assert result == "manga", f"Expected 'manga' but got '{result}'"
    
    
    def test_detect_webtoon_vertical(self, test_images_dir):
        """Test detection of vertical webtoon"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_lot_of_white.jpg")
        result = guess_manga_or_webtoon_image(img_path)
        # 720x5342 -> ratio 7.42 > 4 donc webtoon
        assert result == "webtoon", f"Expected 'webtoon' but got '{result}'"
    
    
    def test_detect_all_webtoons(self, test_images_dir):
        """Test that all webtoon_*.jpg are detected as webtoon"""
        webtoon_files = [
            "webtoon_lot_of_white.jpg",
            "webtoon_lot_of_white_again.jpg",
            "webtoon_mix_background_black_then_white.jpg",
            "webtoon_very_big_block_cannot_cut.jpg",
        ]
        
        for filename in webtoon_files:
            img_path = self.get_test_image_path(test_images_dir, filename)
            result = guess_manga_or_webtoon_image(img_path)
            assert result == "webtoon", f"{filename}: expected 'webtoon' but got '{result}'"
    
    
    def test_detect_manga_double_page(self, test_images_dir):
        """Test detection of manga double page (landscape but still manga)"""
        img_path = self.get_test_image_path(test_images_dir, "manga_scan_double_page.jpg")
        result = guess_manga_or_webtoon_image(img_path)
        # 1600x1200 -> ratio 0.75 < 4 donc manga
        assert result == "manga", f"Expected 'manga' but got '{result}'"
    
    
    def test_detect_comics_portrait(self, test_images_dir):
        """Test detection of comics portrait (should be manga)"""
        img_path = self.get_test_image_path(test_images_dir, "comics_classic.jpg")
        result = guess_manga_or_webtoon_image(img_path)
        # 563x800 -> ratio 1.42 < 4 donc manga
        assert result == "manga", f"Expected 'manga' but got '{result}'"
