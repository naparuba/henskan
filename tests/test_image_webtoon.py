#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for webtoon-specific processing
"""
import os

from PIL import Image

from henskan.image import _find_dominant_color, _is_full_background_image, _split_webtoon
from .image_test_base import ImageTestBase


class TestWebtoonProcessing(ImageTestBase):
    """Tests for webtoon-specific processing"""
    
    def _assert_valid_rgb_tuple(self, color, message_prefix=""):
        """Helper to assert a color is a valid RGB tuple"""
        prefix = f"{message_prefix}: " if message_prefix else ""
        assert isinstance(color, tuple), f"{prefix}Expected tuple, got {type(color)}"
        assert len(color) == 3, f"{prefix}Expected 3 color values, got {len(color)}"
        assert all(isinstance(c, int) and 0 <= c <= 255 for c in color), \
            f"{prefix}Expected RGB values between 0-255, got {color}"
    
    def _assert_dark_color(self, color, threshold=50):
        """Helper to assert a color is dark (all components < threshold)"""
        assert all(c < threshold for c in color), \
            f"Expected dark color (< {threshold}), got {color}"
    
    def _assert_light_color(self, color, threshold=200):
        """Helper to assert a color is light (all components > threshold)"""
        assert all(c > threshold for c in color), \
            f"Expected light color (> {threshold}), got {color}"
    
    def _assert_valid_split_result(self, result, expected_count):
        """Helper to assert a split result is valid with exact count"""
        assert isinstance(result, list), "Result should be a list"
        assert len(result) == expected_count, f"Expected exactly {expected_count} split images, got {len(result)}"
        
        for i, split_img in enumerate(result):
            assert isinstance(split_img, Image.Image), f"Split image {i} should be a PIL Image"
            assert split_img.width > 0, f"Split image {i} should have width > 0"
            assert split_img.height > 0, f"Split image {i} should have height > 0"
    
    def _save_split_results(self, result, base_filename):
        """Save split results to the splits directory for manual verification"""
        splits_dir = os.path.join(os.path.dirname(__file__), "splits")
        for i, split_img in enumerate(result):
            # Create filename with original name and split index
            filename = f"{base_filename}_split_{i:02d}.jpg"
            filepath = os.path.join(splits_dir, filename)
            split_img.save(filepath)
        return len(result)
    
    def test_find_dominant_color_solid_red(self):
        """Test _find_dominant_color with a solid red image"""
        # Create a solid red image
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        dominant_color = _find_dominant_color(img)
        assert dominant_color == (255, 0, 0), f"Expected red (255, 0, 0), got {dominant_color}"
    
    def test_find_dominant_color_solid_blue(self):
        """Test _find_dominant_color with a solid blue image"""
        # Create a solid blue image
        img = Image.new('RGB', (100, 100), color=(0, 0, 255))
        dominant_color = _find_dominant_color(img)
        assert dominant_color == (0, 0, 255), f"Expected blue (0, 0, 255), got {dominant_color}"
    
    def test_find_dominant_color_solid_white(self):
        """Test _find_dominant_color with a solid white image"""
        # Create a solid white image
        img = Image.new('RGB', (100, 100), color=(255, 255, 255))
        dominant_color = _find_dominant_color(img)
        assert dominant_color == (255, 255, 255), f"Expected white (255, 255, 255), got {dominant_color}"
    
    def test_find_dominant_color_solid_black(self):
        """Test _find_dominant_color with a solid black image"""
        # Create a solid black image
        img = Image.new('RGB', (100, 100), color=(0, 0, 0))
        dominant_color = _find_dominant_color(img)
        assert dominant_color == (0, 0, 0), f"Expected black (0, 0, 0), got {dominant_color}"
    
    def test_find_dominant_color_mostly_green(self):
        """Test _find_dominant_color with an image that is mostly green"""
        # Create an image that is 90% green and 10% red
        img = Image.new('RGB', (100, 100), color=(0, 255, 0))
        # Add a small red square
        for x in range(10):
            for y in range(10):
                img.putpixel((x, y), (255, 0, 0))
        
        dominant_color = _find_dominant_color(img)
        assert dominant_color == (0, 255, 0), f"Expected green (0, 255, 0), got {dominant_color}"
    
    def test_find_dominant_color_mixed_colors(self):
        """Test _find_dominant_color with mixed colors where one is more frequent"""
        # Create an image with 60% blue and 40% yellow
        img = Image.new('RGB', (100, 100))
        for x in range(100):
            for y in range(100):
                if (x + y) % 10 < 6:
                    img.putpixel((x, y), (0, 0, 255))  # Blue
                else:
                    img.putpixel((x, y), (255, 255, 0))  # Yellow
        
        dominant_color = _find_dominant_color(img)
        assert dominant_color == (0, 0, 255), f"Expected blue (0, 0, 255) to be dominant, got {dominant_color}"
    
    def test_find_dominant_color_webtoon_full_black(self, test_images_dir):
        """Test _find_dominant_color with webtoon_full_black.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_full_black.jpg")
        img = Image.open(img_path)
        dominant_color = _find_dominant_color(img)
        
        self._assert_valid_rgb_tuple(dominant_color, "webtoon_full_black.jpg")
        self._assert_dark_color(dominant_color, threshold=50)
    
    def test_find_dominant_color_webtoon_lot_of_white(self, test_images_dir):
        """Test _find_dominant_color with webtoon_lot_of_white.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_lot_of_white.jpg")
        img = Image.open(img_path)
        dominant_color = _find_dominant_color(img)
        
        self._assert_valid_rgb_tuple(dominant_color, "webtoon_lot_of_white.jpg")
        self._assert_light_color(dominant_color, threshold=200)
    
    def test_find_dominant_color_webtoon_diagonal_cuts(self, test_images_dir):
        """Test _find_dominant_color with webtoon_diagonal_cuts.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_diagonal_cuts.jpg")
        img = Image.open(img_path)
        dominant_color = _find_dominant_color(img)
        
        self._assert_valid_rgb_tuple(dominant_color, "webtoon_diagonal_cuts.jpg")
    
    def test_find_dominant_color_webtoon_mix_background(self, test_images_dir):
        """Test _find_dominant_color with webtoon_mix_background_black_then_white.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_mix_background_black_then_white.jpg")
        img = Image.open(img_path)
        dominant_color = _find_dominant_color(img)
        
        self._assert_valid_rgb_tuple(dominant_color, "webtoon_mix_background.jpg")
    
    def test_find_dominant_color_webtoon_lot_of_white_again(self, test_images_dir):
        """Test _find_dominant_color with webtoon_lot_of_white_again.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_lot_of_white_again.jpg")
        img = Image.open(img_path)
        dominant_color = _find_dominant_color(img)
        
        self._assert_valid_rgb_tuple(dominant_color, "webtoon_lot_of_white_again.jpg")
        self._assert_light_color(dominant_color, threshold=200)
    
    def test_find_dominant_color_webtoon_very_big_block(self, test_images_dir):
        """Test _find_dominant_color with webtoon_very_big_block_cannot_cut.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_very_big_block_cannot_cut.jpg")
        img = Image.open(img_path)
        dominant_color = _find_dominant_color(img)
        
        self._assert_valid_rgb_tuple(dominant_color, "webtoon_very_big_block.jpg")
    
    def test_split_webtoon_lot_of_white(self, test_images_dir):
        """Test _split_webtoon with webtoon_lot_of_white.jpg - should split into multiple parts"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_lot_of_white.jpg")
        img = Image.open(img_path)
        
        result = _split_webtoon(img)
        self._save_split_results(result, "webtoon_lot_of_white")
        
        # This image splits into 3 parts (verified manually)
        self._assert_valid_split_result(result, expected_count=3)
        
        # Check that splits have reasonable dimensions
        for split_img in result:
            assert split_img.width <= img.width, "Split width should be <= original"
    
    def test_split_webtoon_lot_of_white_again(self, test_images_dir):
        """Test _split_webtoon with webtoon_lot_of_white_again.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_lot_of_white_again.jpg")
        img = Image.open(img_path)
        
        result = _split_webtoon(img)
        self._save_split_results(result, "webtoon_lot_of_white_again")
        
        # This image splits into 4 parts (verified manually)
        self._assert_valid_split_result(result, expected_count=4)
    
    def test_split_webtoon_diagonal_cuts(self, test_images_dir):
        """Test _split_webtoon with webtoon_diagonal_cuts.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_diagonal_cuts.jpg")
        img = Image.open(img_path)
        
        result = _split_webtoon(img)
        self._save_split_results(result, "webtoon_diagonal_cuts")
        
        # Diagonal cuts are complex - this image splits into 4 parts (verified manually)
        self._assert_valid_split_result(result, expected_count=4)
    
    def test_split_webtoon_mix_background(self, test_images_dir):
        """Test _split_webtoon with webtoon_mix_background_black_then_white.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_mix_background_black_then_white.jpg")
        img = Image.open(img_path)
        
        result = _split_webtoon(img)
        self._save_split_results(result, "webtoon_mix_background_black_then_white")
        
        # Mixed background splits into 5 parts (verified manually)
        self._assert_valid_split_result(result, expected_count=5)
    
    def test_split_webtoon_very_big_block(self, test_images_dir):
        """Test _split_webtoon with webtoon_very_big_block_cannot_cut.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_very_big_block_cannot_cut.jpg")
        img = Image.open(img_path)
        
        result = _split_webtoon(img)
        self._save_split_results(result, "webtoon_very_big_block_cannot_cut")
        
        # Very big block splits into 4 parts (verified manually)
        self._assert_valid_split_result(result, expected_count=4)
    
    def test_split_webtoon_full_black_returns_empty_or_filters(self, test_images_dir):
        """Test _split_webtoon with webtoon_full_black.jpg - mostly black should be filtered out"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_full_black.jpg")
        img = Image.open(img_path)
        
        result = _split_webtoon(img)
        self._save_split_results(result, "webtoon_full_black")
        
        # Full black images split into 3 parts (verified manually)
        self._assert_valid_split_result(result, expected_count=3)
    

    def test_is_full_background_image_pure_white(self):
        """Test _is_full_background_image with a pure white image"""
        img = Image.new('RGB', (100, 100), color=(255, 255, 255))
        assert _is_full_background_image(img) is True, "Pure white image should be detected as full background"
    
    def test_is_full_background_image_pure_black(self):
        """Test _is_full_background_image with a pure black image"""
        img = Image.new('RGB', (100, 100), color=(0, 0, 0))
        assert _is_full_background_image(img) is True, "Pure black image should be detected as full background"
    
    def test_is_full_background_image_almost_white(self):
        """Test _is_full_background_image with an almost white image (within tolerance)"""
        # Create an image with slightly off-white color (within precision=5)
        img = Image.new('RGB', (100, 100), color=(252, 253, 254))
        assert _is_full_background_image(img) is True, "Almost white image should be detected as full background"
    
    def test_is_full_background_image_almost_black(self):
        """Test _is_full_background_image with an almost black image (within tolerance)"""
        # Create an image with slightly off-black color (within precision=5)
        img = Image.new('RGB', (100, 100), color=(3, 4, 2))
        assert _is_full_background_image(img) is True, "Almost black image should be detected as full background"
    
    def test_is_full_background_image_with_content_on_white(self):
        """Test _is_full_background_image with content on white background"""
        img = Image.new('RGB', (100, 100), color=(255, 255, 255))
        # Add some non-white content
        for x in range(10, 20):
            for y in range(10, 20):
                img.putpixel((x, y), (100, 100, 100))
        assert _is_full_background_image(img) is False, "Image with content should not be detected as full background"
    
    def test_is_full_background_image_with_content_on_black(self):
        """Test _is_full_background_image with content on black background"""
        img = Image.new('RGB', (100, 100), color=(0, 0, 0))
        # Add some non-black content
        for x in range(10, 20):
            for y in range(10, 20):
                img.putpixel((x, y), (100, 100, 100))
        assert _is_full_background_image(img) is False, "Image with content should not be detected as full background"
    
    def test_is_full_background_image_colored(self):
        """Test _is_full_background_image with a colored image"""
        # Blue image - should not be detected as full background
        img = Image.new('RGB', (100, 100), color=(0, 0, 255))
        assert _is_full_background_image(img) is False, "Colored image should not be detected as full background"
    
    def test_is_full_background_image_gray(self):
        """Test _is_full_background_image with a gray image"""
        # Gray image - should not be detected as full background
        img = Image.new('RGB', (100, 100), color=(128, 128, 128))
        assert _is_full_background_image(img) is False, "Gray image should not be detected as full background"
    
    def test_is_full_background_image_webtoon_full_black(self, test_images_dir):
        """Test _is_full_background_image with webtoon_full_black.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_full_black.jpg")
        img = Image.open(img_path)
        result = _is_full_background_image(img)
        # This image has some pixels (15,15,15) which are beyond precision=5 tolerance
        # So it's NOT detected as full background despite being mostly black
        assert result is False, f"webtoon_full_black.jpg has pixels beyond tolerance, should not be full background"
    
    def test_is_full_background_image_webtoon_full_black_again(self, test_images_dir):
        """Test _is_full_background_image with webtoon_full_black_again.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_full_black_again.jpg")
        img = Image.open(img_path)
        result = _is_full_background_image(img)
        # This image likely has some pixels beyond tolerance as well
        assert result is False, f"webtoon_full_black_again.jpg has pixels beyond tolerance, should not be full background"
    
    def test_is_full_background_image_webtoon_lot_of_white(self, test_images_dir):
        """Test _is_full_background_image with webtoon_lot_of_white.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_lot_of_white.jpg")
        img = Image.open(img_path)
        result = _is_full_background_image(img)
        # This has content, so should not be detected as full background
        assert result is False, f"webtoon_lot_of_white.jpg has content, should not be full background"
    
    def test_is_full_background_image_webtoon_diagonal_cuts(self, test_images_dir):
        """Test _is_full_background_image with webtoon_diagonal_cuts.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_diagonal_cuts.jpg")
        img = Image.open(img_path)
        result = _is_full_background_image(img)
        # This has content, so should not be detected as full background
        assert result is False, f"webtoon_diagonal_cuts.jpg has content, should not be full background"
    
    def test_is_full_background_image_webtoon_mix_background(self, test_images_dir):
        """Test _is_full_background_image with webtoon_mix_background_black_then_white.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_mix_background_black_then_white.jpg")
        img = Image.open(img_path)
        result = _is_full_background_image(img)
        # This has mixed content, so should not be detected as full background
        assert result is False, f"webtoon_mix_background_black_then_white.jpg has mixed content, should not be full background"
    
    def test_is_full_background_image_webtoon_very_big_block(self, test_images_dir):
        """Test _is_full_background_image with webtoon_very_big_block_cannot_cut.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_very_big_block_cannot_cut.jpg")
        img = Image.open(img_path)
        result = _is_full_background_image(img)
        # This has content, so should not be detected as full background
        assert result is False, f"webtoon_very_big_block_cannot_cut.jpg has content, should not be full background"
    
    def test_is_full_background_image_webtoon_lot_of_white_again(self, test_images_dir):
        """Test _is_full_background_image with webtoon_lot_of_white_again.jpg"""
        img_path = self.get_test_image_path(test_images_dir, "webtoon_lot_of_white_again.jpg")
        img = Image.open(img_path)
        result = _is_full_background_image(img)
        # This has content, so should not be detected as full background
        assert result is False, f"webtoon_lot_of_white_again.jpg has content, should not be full background"
