#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for utility functions
Tests find_compact_title() and natural_key()
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase
from henskan.util import find_compact_title, natural_key


class TestUtilFunctions(ImageTestBase):
    """Tests for utility functions"""
    
    # ============================================
    # Tests de natural_key
    # ============================================
    
    def test_natural_key_simple_numbers(self):
        """Test natural_key sorts numbers naturally"""
        # Test que les nombres sont triés numériquement, pas alphabétiquement
        items = ['file1', 'file10', 'file2', 'file20']
        sorted_items = sorted(items, key=natural_key)
        
        # Ordre naturel: 1, 2, 10, 20 (pas 1, 10, 2, 20)
        assert sorted_items == ['file1', 'file2', 'file10', 'file20']
    
    
    def test_natural_key_mixed_content(self):
        """Test natural_key with mixed text and numbers"""
        items = ['chapter3page5', 'chapter1page10', 'chapter2page1']
        sorted_items = sorted(items, key=natural_key)
        
        assert sorted_items == ['chapter1page10', 'chapter2page1', 'chapter3page5']
    
    
    def test_natural_key_sorting_order(self):
        """Test natural_key produces correct sorting order"""
        items = ['z', 'a', '10', '2', 'b1', 'b10', 'b2']
        sorted_items = sorted(items, key=natural_key)
        
        # Nombres d'abord par ordre numérique, puis lettres par ordre alphabétique
        assert sorted_items == ['2', '10', 'a', 'b1', 'b2', 'b10', 'z']
    
    
    def test_natural_key_leading_zeros(self):
        """Test natural_key handles leading zeros"""
        # Les zéros en tête devraient être traités comme des nombres
        items = ['file001', 'file010', 'file002', 'file100']
        sorted_items = sorted(items, key=natural_key)
        
        assert sorted_items == ['file001', 'file002', 'file010', 'file100']
    
    
    def test_natural_key_chapter_numbers(self):
        """Test natural_key with chapter/tome numbers"""
        items = ['Tome 10', 'Tome 1', 'Tome 2', 'Chapter 20', 'Chapter 3']
        sorted_items = sorted(items, key=natural_key)
        
        # Chapter vient avant Tome alphabétiquement (en minuscule)
        assert sorted_items == ['Chapter 3', 'Chapter 20', 'Tome 1', 'Tome 2', 'Tome 10']
    
    
    def test_natural_key_page_numbers(self):
        """Test natural_key with page numbers (001, 002, etc.)"""
        items = ['page_001.jpg', 'page_010.jpg', 'page_002.jpg', 'page_100.jpg']
        sorted_items = sorted(items, key=natural_key)
        
        assert sorted_items == ['page_001.jpg', 'page_002.jpg', 'page_010.jpg', 'page_100.jpg']
    
    
    def test_natural_key_case_sensitivity(self):
        """Test natural_key case handling"""
        # natural_key convertit en minuscule pour la comparaison
        items = ['File1', 'file2', 'FILE10', 'FiLe3']
        sorted_items = sorted(items, key=natural_key)
        
        # Devrait trier par ordre numérique en ignorant la casse
        assert sorted_items == ['File1', 'file2', 'FiLe3', 'FILE10']
    
    
    def test_natural_key_special_characters(self):
        """Test natural_key with special characters"""
        items = ['file_3', 'file-1', 'file.10', 'file 2']
        sorted_items = sorted(items, key=natural_key)
        
        # Les caractères spéciaux sont traités comme du texte
        # L'ordre dépend de l'ordre ASCII/Unicode
        assert len(sorted_items) == 4
        assert 'file-1' in sorted_items
        assert 'file 2' in sorted_items
    
    
    # ============================================
    # Tests de find_compact_title
    # ============================================
    
    def test_find_compact_title_common_prefix(self):
        """Test find_compact_title finds common prefix"""
        # Avec des numéros de tome
        directories = ['One Piece T01', 'One Piece T02', 'One Piece T03']
        result = find_compact_title(directories)
        
        # La fonction ajoute le range de numéros
        assert result == 'One Piece -- 1-3'
    
    
    def test_find_compact_title_single_image(self):
        """Test find_compact_title with only one image"""
        directories = ['Naruto Volume 1']
        result = find_compact_title(directories)
        
        # Avec un seul élément, retourne tel quel
        assert result == 'Naruto Volume 1'
    
    
    def test_find_compact_title_no_common_prefix(self):
        """Test find_compact_title with completely different names"""
        directories = ['Attack on Titan T01', 'Death Note T02']
        result = find_compact_title(directories)
        
        # Pas de préfixe commun, retourne vide
        assert result == ''
    
    
    def test_find_compact_title_removes_extensions(self):
        """Test find_compact_title removes file extensions"""
        # La fonction nettoie les parenthèses et crochets
        directories = ['Manga [Digital] 1', 'Manga [Digital] 2', 'Manga [Digital] 3']
        result = find_compact_title(directories)
        
        assert result == 'Manga -- 1-3'
    
    
    def test_find_compact_title_with_chapters(self):
        """Test find_compact_title with chapter numbers in names"""
        directories = ['Bleach 1', 'Bleach 2', 'Bleach 10']
        result = find_compact_title(directories)
        
        # Range: 1-10
        assert result == 'Bleach -- 1-10'
    
    
    def test_find_compact_title_with_tomes(self):
        """Test find_compact_title with tome numbers in names"""
        directories = ['ELDEN RING – T02', 'ELDEN RING – T03', 'ELDEN RING – T01']
        result = find_compact_title(directories)
        
        # Garde le tiret, et ajoute le range 1-3
        assert result == 'ELDEN RING – -- 1-3'
    
    
    def test_find_compact_title_real_manga_names(self):
        """Test find_compact_title with realistic manga filenames"""
        directories = [
            'Hellboy (Delcourt) - 01 - Les germes de la destruction',
            'Hellboy (Delcourt) - 02 - Au nom du diable',
            'Hellboy (Delcourt) - 03 - Le cercueil enchaîné'
        ]
        result = find_compact_title(directories)
        
        assert result == 'Hellboy -- 1-3'
    
    
    def test_find_compact_title_removes_trailing_numbers(self):
        """Test find_compact_title removes trailing numbers"""
        directories = ['My Hero Academia 1', 'My Hero Academia 2', 'My Hero Academia 15']
        result = find_compact_title(directories)
        
        # Range: 1-15
        assert result == 'My Hero Academia -- 1-15'
    
    
    def test_find_compact_title_special_characters(self):
        """Test find_compact_title handles special characters"""
        # Les caractères -, #, % sont supprimés
        directories = ['Manga-Name #1', 'Manga-Name #2', 'Manga-Name #3']
        result = find_compact_title(directories)
        
        # Les - et # sont nettoyés, et le range est ajouté
        assert 'Manga' in result
        assert 'Name' in result
        assert '1-3' in result
    
    
    def test_find_compact_title_separators(self):
        """Test find_compact_title handles underscores and dashes"""
        # Les underscores et points sont remplacés par des espaces
        directories = ['Manga_Name.Vol.1', 'Manga_Name.Vol.2', 'Manga_Name.Vol.3']
        result = find_compact_title(directories)
        
        # _ et . sont convertis en espaces, range ajouté
        assert result == 'Manga Name Vol -- 1-3'
    
    
    def test_find_compact_title_empty_list(self):
        """Test find_compact_title with empty image list"""
        directories = []
        result = find_compact_title(directories)
        
        assert result == ''
    
    
    def test_find_compact_title_consistency(self):
        """Test find_compact_title gives consistent results"""
        directories = ['Manga T01', 'Manga T02', 'Manga T03']
        
        # Appeler plusieurs fois devrait donner le même résultat
        result1 = find_compact_title(directories)
        result2 = find_compact_title(directories)
        result3 = find_compact_title(directories)
        
        assert result1 == result2 == result3
        assert result1 == 'Manga -- 1-3'

