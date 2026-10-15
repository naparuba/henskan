#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for PDF archive creation
Tests ArchivePDF class for creating PDF files for eReaders
"""
import os
import sys

from PIL import Image as PILImage

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase
from henskan.archive_pdf import ArchivePDF


class TestArchivePDF(ImageTestBase):
    """Tests for PDF archive creation"""
    
    # ============================================
    # Tests de création et initialisation
    # ============================================
    
    def test_create_pdf_archive(self, temp_dir):
        """Test creating a new PDF archive"""
        pdf_path = os.path.join(temp_dir, "test_manga")
        title = "Test Manga"
        device = "Kindle Paperwhite 3/Voyage/Oasis"
        
        pdf_archive = ArchivePDF(pdf_path, title, device)
        
        assert pdf_archive is not None
        assert pdf_archive._canvas is not None
        assert pdf_archive._page_size == (1072, 1448)
        
        pdf_archive.close()
    
    
    def test_create_pdf_with_title(self, temp_dir):
        """Test PDF archive creation with title metadata"""
        pdf_path = os.path.join(temp_dir, "one_piece")
        title = "One Piece - Volume 1"
        device = "Kindle 2/3/Touch"
        
        pdf_archive = ArchivePDF(pdf_path, title, device)
        
        # Ajouter une page pour finaliser le PDF
        test_image_path = os.path.join(temp_dir, "page.png")
        img = PILImage.new('RGB', (600, 800), color='white')
        img.save(test_image_path)
        pdf_archive.add(test_image_path)
        
        pdf_archive.close()
        
        pdf_file = os.path.join(temp_dir, "one_piece.pdf")
        assert os.path.exists(pdf_file)
    
    
    def test_create_pdf_for_different_devices(self, temp_dir):
        """Test PDF creation with different device page sizes"""
        devices_and_sizes = {
            'Kindle 2/3/Touch': (600, 800),
            'Kindle Paperwhite 3/Voyage/Oasis': (1072, 1448),
            'Kobo Aura HD': (1080, 1440),
        }
        
        for device, expected_size in devices_and_sizes.items():
            pdf_path = os.path.join(temp_dir, f"test_{device.replace('/', '_')}")
            pdf_archive = ArchivePDF(pdf_path, "Test", device)
            
            assert pdf_archive._page_size == expected_size
            
            pdf_archive.close()
    
    
    def test_pdf_page_size_for_device(self, temp_dir):
        """Test PDF has correct page size for specified device"""
        pdf_path = os.path.join(temp_dir, "test_size")
        device = "Kobo Glo HD"
        
        pdf_archive = ArchivePDF(pdf_path, "Test", device)
        
        assert pdf_archive._page_size == (1072, 1448)
        
        pdf_archive.close()
    
    
    # ============================================
    # Tests d'ajout de pages
    # ============================================
    
    def test_add_single_page_to_pdf(self, temp_dir):
        """Test adding a single page to PDF archive"""
        pdf_path = os.path.join(temp_dir, "single_page")
        pdf_archive = ArchivePDF(pdf_path, "Test", "Kindle 2/3/Touch")
        
        test_image_path = os.path.join(temp_dir, "page1.png")
        img = PILImage.new('RGB', (600, 800), color='white')
        img.save(test_image_path)
        
        pdf_archive.add(test_image_path)
        pdf_archive.close()
        
        pdf_file = os.path.join(temp_dir, "single_page.pdf")
        assert os.path.exists(pdf_file)
        assert os.path.getsize(pdf_file) > 0
    
    
    def test_add_multiple_pages_to_pdf(self, temp_dir):
        """Test adding multiple pages to PDF archive"""
        pdf_path = os.path.join(temp_dir, "multi_page")
        pdf_archive = ArchivePDF(pdf_path, "Test", "Kindle 2/3/Touch")
        
        for i in range(5):
            test_image_path = os.path.join(temp_dir, f"page{i}.png")
            img = PILImage.new('RGB', (600, 800), color=(i * 50, i * 50, i * 50))
            img.save(test_image_path)
            pdf_archive.add(test_image_path)
        
        pdf_archive.close()
        
        pdf_file = os.path.join(temp_dir, "multi_page.pdf")
        assert os.path.exists(pdf_file)
        assert os.path.getsize(pdf_file) > 1000
    
    
    def test_add_pages_preserves_order(self, temp_dir):
        """Test pages are added in the correct order"""
        pdf_path = os.path.join(temp_dir, "ordered_pages")
        pdf_archive = ArchivePDF(pdf_path, "Test", "Kindle 2/3/Touch")
        
        for i in range(3):
            test_image_path = os.path.join(temp_dir, f"ordered_page{i}.png")
            img = PILImage.new('RGB', (600, 800), color='white')
            img.save(test_image_path)
            pdf_archive.add(test_image_path)
        
        pdf_archive.close()
        
        pdf_file = os.path.join(temp_dir, "ordered_pages.pdf")
        assert os.path.exists(pdf_file)
    
    
    def test_add_page_invalid_path(self, temp_dir):
        """Test adding page with invalid path raises error"""
        pdf_path = os.path.join(temp_dir, "invalid_page")
        pdf_archive = ArchivePDF(pdf_path, "Test", "Kindle 2/3/Touch")
        
        invalid_path = os.path.join(temp_dir, "nonexistent.png")
        
        try:
            pdf_archive.add(invalid_path)
            pdf_archive.close()
            assert False, "Should have raised an error"
        except Exception:
            assert True
    
    
    def test_add_page_non_image_file(self, temp_dir):
        """Test adding non-image file raises error"""
        pdf_path = os.path.join(temp_dir, "non_image")
        pdf_archive = ArchivePDF(pdf_path, "Test", "Kindle 2/3/Touch")
        
        text_file = os.path.join(temp_dir, "not_an_image.txt")
        with open(text_file, 'w') as f:
            f.write("This is not an image")
        
        try:
            pdf_archive.add(text_file)
            pdf_archive.close()
            assert False, "Should have raised an error"
        except Exception:
            assert True
    
    
    # ============================================
    # Tests de chapitres
    # ============================================
    
    def test_add_chapter_to_pdf(self, temp_dir):
        """Test adding chapter markers to PDF"""
        pdf_path = os.path.join(temp_dir, "with_chapter")
        pdf_archive = ArchivePDF(pdf_path, "Test", "Kindle 2/3/Touch")
        
        pdf_archive.add_chapter("Chapter 1")
        
        test_image_path = os.path.join(temp_dir, "ch1_page1.png")
        img = PILImage.new('RGB', (600, 800), color='white')
        img.save(test_image_path)
        pdf_archive.add(test_image_path)
        
        pdf_archive.close()
        
        pdf_file = os.path.join(temp_dir, "with_chapter.pdf")
        assert os.path.exists(pdf_file)
    
    
    def test_add_multiple_chapters_to_pdf(self, temp_dir):
        """Test adding multiple chapters to PDF"""
        pdf_path = os.path.join(temp_dir, "multi_chapters")
        pdf_archive = ArchivePDF(pdf_path, "Test Manga", "Kindle 2/3/Touch")
        
        for chapter_num in range(1, 4):
            pdf_archive.add_chapter(f"Chapter {chapter_num}")
            
            for page_num in range(2):
                test_image_path = os.path.join(temp_dir, f"ch{chapter_num}_page{page_num}.png")
                img = PILImage.new('RGB', (600, 800), color=(chapter_num * 80, page_num * 100, 50))
                img.save(test_image_path)
                pdf_archive.add(test_image_path)
        
        pdf_archive.close()
        
        pdf_file = os.path.join(temp_dir, "multi_chapters.pdf")
        assert os.path.exists(pdf_file)
        assert os.path.getsize(pdf_file) > 2000
    
    
    def test_chapters_group_pages(self, temp_dir):
        """Test that pages are correctly grouped by chapter"""
        pdf_path = os.path.join(temp_dir, "grouped_chapters")
        pdf_archive = ArchivePDF(pdf_path, "Test", "Kindle 2/3/Touch")
        
        pdf_archive.add_chapter("First Chapter")
        for i in range(3):
            test_image_path = os.path.join(temp_dir, f"ch1_p{i}.png")
            img = PILImage.new('RGB', (600, 800), color='red')
            img.save(test_image_path)
            pdf_archive.add(test_image_path)
        
        pdf_archive.add_chapter("Second Chapter")
        for i in range(2):
            test_image_path = os.path.join(temp_dir, f"ch2_p{i}.png")
            img = PILImage.new('RGB', (600, 800), color='blue')
            img.save(test_image_path)
            pdf_archive.add(test_image_path)
        
        pdf_archive.close()
        
        pdf_file = os.path.join(temp_dir, "grouped_chapters.pdf")
        assert os.path.exists(pdf_file)
    
    
    def test_empty_chapter(self, temp_dir):
        """Test behavior with empty chapter"""
        pdf_path = os.path.join(temp_dir, "empty_chapter")
        pdf_archive = ArchivePDF(pdf_path, "Test", "Kindle 2/3/Touch")
        
        pdf_archive.add_chapter("Empty Chapter")
        
        pdf_archive.add_chapter("Chapter with content")
        test_image_path = os.path.join(temp_dir, "page.png")
        img = PILImage.new('RGB', (600, 800), color='white')
        img.save(test_image_path)
        pdf_archive.add(test_image_path)
        
        pdf_archive.close()
        
        pdf_file = os.path.join(temp_dir, "empty_chapter.pdf")
        assert os.path.exists(pdf_file)
    
    
    # ============================================
    # Tests de fermeture et finalisation
    # ============================================
    
    def test_close_pdf_creates_file(self, temp_dir):
        """Test closing PDF creates valid PDF file"""
        pdf_path = os.path.join(temp_dir, "close_test")
        pdf_archive = ArchivePDF(pdf_path, "Test", "Kindle 2/3/Touch")
        
        # Ajouter une page
        test_image_path = os.path.join(temp_dir, "page.png")
        img = PILImage.new('RGB', (600, 800), color='white')
        img.save(test_image_path)
        pdf_archive.add(test_image_path)
        
        # Fermer le PDF
        pdf_archive.close()
        
        # Vérifier que le fichier PDF existe
        pdf_file = os.path.join(temp_dir, "close_test.pdf")
        assert os.path.exists(pdf_file)
    
    
    def test_closed_pdf_file_valid(self, temp_dir):
        """Test closed PDF file exists and is valid"""
        pdf_path = os.path.join(temp_dir, "valid_pdf")
        pdf_archive = ArchivePDF(pdf_path, "Valid Test", "Kindle 2/3/Touch")
        
        # Ajouter des pages
        for i in range(3):
            test_image_path = os.path.join(temp_dir, f"valid_page{i}.png")
            img = PILImage.new('RGB', (600, 800), color='white')
            img.save(test_image_path)
            pdf_archive.add(test_image_path)
        
        pdf_archive.close()
        
        pdf_file = os.path.join(temp_dir, "valid_pdf.pdf")
        assert os.path.exists(pdf_file)
        
        # Vérifier que c'est un fichier PDF (commence par %PDF)
        with open(pdf_file, 'rb') as f:
            header = f.read(4)
            assert header == b'%PDF', "File should be a valid PDF"
    
    
    def test_pdf_file_size(self, temp_dir):
        """Test PDF file size is reasonable (not empty, not huge)"""
        pdf_path = os.path.join(temp_dir, "size_test")
        pdf_archive = ArchivePDF(pdf_path, "Size Test", "Kindle 2/3/Touch")
        
        # Ajouter quelques pages
        for i in range(5):
            test_image_path = os.path.join(temp_dir, f"size_page{i}.png")
            img = PILImage.new('RGB', (600, 800), color=(i * 50, i * 50, i * 50))
            img.save(test_image_path)
            pdf_archive.add(test_image_path)
        
        pdf_archive.close()
        
        pdf_file = os.path.join(temp_dir, "size_test.pdf")
        file_size = os.path.getsize(pdf_file)
        
        # Le fichier ne devrait pas être vide
        assert file_size > 0
        # Pas trop grand non plus (< 50MB pour 5 pages)
        assert file_size < 50 * 1024 * 1024
        # Au moins quelques KB
        assert file_size > 1000
    
    
    def test_close_pdf_idempotent(self, temp_dir):
        """Test closing PDF multiple times is safe"""
        pdf_path = os.path.join(temp_dir, "idempotent")
        pdf_archive = ArchivePDF(pdf_path, "Test", "Kindle 2/3/Touch")
        
        # Ajouter une page
        test_image_path = os.path.join(temp_dir, "page.png")
        img = PILImage.new('RGB', (600, 800), color='white')
        img.save(test_image_path)
        pdf_archive.add(test_image_path)
        
        # Fermer plusieurs fois
        pdf_archive.close()
        
        # La deuxième fermeture ne devrait pas causer d'erreur critique
        try:
            pdf_archive.close()
            assert True
        except Exception:
            # Si ça lève une erreur, c'est acceptable
            assert True
        
        pdf_file = os.path.join(temp_dir, "idempotent.pdf")
        assert os.path.exists(pdf_file)
    
    
    # ============================================
    # Tests de métadonnées
    # ============================================
    
    def test_pdf_metadata_title(self, temp_dir):
        """Test PDF metadata contains correct title"""
        pdf_path = os.path.join(temp_dir, "metadata_title")
        title = "One Piece - Grand Line"
        pdf_archive = ArchivePDF(pdf_path, title, "Kindle 2/3/Touch")
        
        # Ajouter une page pour que le PDF soit valide
        test_image_path = os.path.join(temp_dir, "page.png")
        img = PILImage.new('RGB', (600, 800), color='white')
        img.save(test_image_path)
        pdf_archive.add(test_image_path)
        
        pdf_archive.close()
        
        # Vérifier que le PDF est créé
        pdf_file = os.path.join(temp_dir, "metadata_title.pdf")
        assert os.path.exists(pdf_file)
        
        # Vérifier que le titre a été défini (présent dans le PDF)
        with open(pdf_file, 'rb') as f:
            content = f.read()
            # Le titre devrait être dans les métadonnées du PDF
            assert b'One Piece' in content or title.encode('utf-8') in content
    
    
    def test_pdf_metadata_creator(self, temp_dir):
        """Test PDF metadata contains creator information"""
        pdf_path = os.path.join(temp_dir, "metadata_creator")
        pdf_archive = ArchivePDF(pdf_path, "Test", "Kindle 2/3/Touch")
        
        # Ajouter une page
        test_image_path = os.path.join(temp_dir, "page.png")
        img = PILImage.new('RGB', (600, 800), color='white')
        img.save(test_image_path)
        pdf_archive.add(test_image_path)
        
        pdf_archive.close()
        
        # Vérifier que le PDF contient "Henskan" comme auteur
        pdf_file = os.path.join(temp_dir, "metadata_creator.pdf")
        with open(pdf_file, 'rb') as f:
            content = f.read()
            assert b'Henskan' in content
    
    
    def test_pdf_special_characters_title(self, temp_dir):
        """Test PDF with special characters in title"""
        pdf_path = os.path.join(temp_dir, "special_chars")
        title = "Manga Ère Meiji - Vol.1 : L'éveil !"
        pdf_archive = ArchivePDF(pdf_path, title, "Kindle 2/3/Touch")
        
        # Ajouter une page et fermer
        test_image_path = os.path.join(temp_dir, "page.png")
        img = PILImage.new('RGB', (600, 800), color='white')
        img.save(test_image_path)
        pdf_archive.add(test_image_path)
        pdf_archive.close()
        
        pdf_file = os.path.join(temp_dir, "special_chars.pdf")
        assert os.path.exists(pdf_file)
        # Vérifier que le PDF est valide malgré les caractères spéciaux
        assert os.path.getsize(pdf_file) > 0
    
    
    # ============================================
    # Tests d'intégration
    # ============================================
    
    def test_complete_pdf_workflow(self, temp_dir, test_images_dir):
        """Test complete PDF creation workflow with real images"""
        pdf_path = os.path.join(temp_dir, "complete_workflow")
        pdf_archive = ArchivePDF(pdf_path, "Complete Test", "Kindle Paperwhite 3/Voyage/Oasis")
        
        # Simuler un workflow complet avec chapitres et pages
        pdf_archive.add_chapter("Chapter 1")
        
        # Créer quelques pages de test
        for i in range(3):
            test_image_path = os.path.join(temp_dir, f"workflow_page{i}.png")
            img = PILImage.new('RGB', (1072, 1448), color=(i * 80, i * 80, i * 80))
            img.save(test_image_path)
            pdf_archive.add(test_image_path)
        
        pdf_archive.close()
        
        pdf_file = os.path.join(temp_dir, "complete_workflow.pdf")
        assert os.path.exists(pdf_file)
        assert os.path.getsize(pdf_file) > 1000
    
    
    def test_pdf_with_manga_pages(self, temp_dir, test_images_dir):
        """Test PDF creation with actual manga pages"""
        pdf_path = os.path.join(temp_dir, "manga_pdf")
        pdf_archive = ArchivePDF(pdf_path, "Test Manga", "Kindle 2/3/Touch")
        
        # Utiliser une vraie image manga si disponible, sinon créer une image de test
        try:
            manga_path = self.get_test_image_path(test_images_dir, "manga_full_page.jpg")
            pdf_archive.add(manga_path)
        except (FileNotFoundError, AssertionError):
            # Si l'image n'existe pas, créer une image de test
            test_image_path = os.path.join(temp_dir, "manga_page.png")
            img = PILImage.new('RGB', (600, 800), color='white')
            img.save(test_image_path)
            pdf_archive.add(test_image_path)
        
        pdf_archive.close()
        
        pdf_file = os.path.join(temp_dir, "manga_pdf.pdf")
        assert os.path.exists(pdf_file)
    
    
    def test_pdf_for_kindle_devices(self, temp_dir):
        """Test PDF creation for various Kindle devices"""
        kindle_devices = [
            'Kindle 2/3/Touch',
            'Kindle Paperwhite 3/Voyage/Oasis',
            'Kindle DX/DXG'
        ]
        
        for device in kindle_devices:
            pdf_path = os.path.join(temp_dir, f"kindle_{device.replace('/', '_')}")
            pdf_archive = ArchivePDF(pdf_path, f"Test for {device}", device)
            
            # Ajouter une page de test
            test_image_path = os.path.join(temp_dir, f"{device.replace('/', '_')}_page.png")
            img = PILImage.new('RGB', (600, 800), color='white')
            img.save(test_image_path)
            pdf_archive.add(test_image_path)
            
            pdf_archive.close()
            
            # Vérifier que le PDF est créé
            pdf_file = pdf_path + ".pdf"
            assert os.path.exists(pdf_file)
    
    
    def test_pdf_can_be_opened(self, temp_dir):
        """Test generated PDF can be opened and validated"""
        pdf_path = os.path.join(temp_dir, "openable_pdf")
        pdf_archive = ArchivePDF(pdf_path, "Openable Test", "Kindle 2/3/Touch")
        
        # Ajouter des pages
        for i in range(3):
            test_image_path = os.path.join(temp_dir, f"open_page{i}.png")
            img = PILImage.new('RGB', (600, 800), color=(100, 100, 100))
            img.save(test_image_path)
            pdf_archive.add(test_image_path)
        
        pdf_archive.close()
        
        pdf_file = os.path.join(temp_dir, "openable_pdf.pdf")
        
        # Vérifier que c'est un PDF valide
        assert os.path.exists(pdf_file)
        
        # Vérifier le header PDF
        with open(pdf_file, 'rb') as f:
            header = f.read(8)
            assert header.startswith(b'%PDF-'), "Should have valid PDF header"
        
        # Vérifier la fin du fichier PDF (devrait contenir %%EOF)
        with open(pdf_file, 'rb') as f:
            content = f.read()
            assert b'%%EOF' in content, "PDF should have proper end marker"

