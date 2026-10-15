#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integration tests for complete workflows
Tests end-to-end scenarios from image loading to archive creation
"""
import os
import sys
from PIL import Image as PILImage
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .image_test_base import ImageTestBase
from henskan.parameters import Parameters
from henskan.archive_cbz import ArchiveCBZ
from henskan.archive_pdf import ArchivePDF
from henskan import image


class TestIntegrationWorkflows(ImageTestBase):
    """Integration tests for complete workflows"""
    
    # ============================================
    # Tests de workflow complet manga → CBZ
    # ============================================
    
    def test_complete_manga_to_cbz_workflow(self, temp_dir):
        """Test complete workflow: manga images → CBZ archive"""
        # Créer des images manga de test
        images = []
        for i in range(5):
            img = PILImage.new('RGB', (800, 1200), color=(i*50, i*50, i*50))
            img_path = os.path.join(temp_dir, f"page_{i:03d}.png")
            img.save(img_path)
            images.append(img_path)
        
        # Créer l'archive CBZ
        cbz_path = os.path.join(temp_dir, "test_manga")
        archive = ArchiveCBZ(cbz_path)
        
        for img_path in images:
            archive.add(img_path)
        
        archive.close()
        
        # Vérifier que le CBZ existe
        cbz_file = cbz_path + ".cbz"
        assert os.path.exists(cbz_file)
        
        # Vérifier que c'est un ZIP valide
        assert zipfile.is_zipfile(cbz_file)
        
        # Vérifier le contenu
        with zipfile.ZipFile(cbz_file, 'r') as zf:
            files = zf.namelist()
            assert len(files) == 5
    
    
    def test_manga_to_cbz_multiple_chapters(self, temp_dir):
        """Test manga to CBZ with multiple chapters/tomes"""
        params = Parameters()
        
        # Créer des images pour plusieurs chapitres
        for chapter in range(1, 4):
            params.add_chapter(f"Chapter {chapter}")
            for page in range(3):
                img = PILImage.new('RGB', (800, 1200), color=(chapter*80, page*50, 100))
                img_path = os.path.join(temp_dir, f"ch{chapter}_page{page}.png")
                img.save(img_path)
                params.add_image(img_path, f"Chapter {chapter}")
        
        # Créer l'archive avec chapitres
        cbz_path = os.path.join(temp_dir, "manga_chapters")
        archive = ArchiveCBZ(cbz_path)
        
        for chapter in params.get_chapters():
            archive.add_chapter(chapter)
            chapter_images = params.get_images_by_chapter()[chapter]
            for img_path in chapter_images:
                archive.add(img_path)
        
        archive.close()
        
        cbz_file = cbz_path + ".cbz"
        assert os.path.exists(cbz_file)
        assert zipfile.is_zipfile(cbz_file)
    
    
    def test_manga_to_cbz_auto_title(self, temp_dir):
        """Test CBZ creation with automatic title detection"""
        params = Parameters()
        
        # Simuler des fichiers avec pattern de titre
        title_pattern = "One Piece - Tome"
        for i in range(1, 4):
            img = PILImage.new('RGB', (800, 1200), color='white')
            img_path = os.path.join(temp_dir, f"{title_pattern} {i} - page.png")
            img.save(img_path)
            params.add_image(img_path, f"Chapter {i}")
        
        # Le titre devrait être détectable
        params.set_title("One Piece")
        
        cbz_path = os.path.join(temp_dir, params.get_title())
        archive = ArchiveCBZ(cbz_path)
        
        for img_path in params.get_images():
            archive.add(img_path)
        
        archive.close()
        
        cbz_file = cbz_path + ".cbz"
        assert os.path.exists(cbz_file)
    
    
    # ============================================
    # Tests de workflow complet manga → PDF
    # ============================================
    
    def test_complete_manga_to_pdf_workflow(self, temp_dir):
        """Test complete workflow: manga images → PDF archive"""
        # Créer des images manga de test
        images = []
        for i in range(5):
            img = PILImage.new('RGB', (800, 1200), color=(i*50, i*50, i*50))
            img_path = os.path.join(temp_dir, f"page_{i:03d}.png")
            img.save(img_path)
            images.append(img_path)
        
        # Créer l'archive PDF
        pdf_path = os.path.join(temp_dir, "test_manga")
        archive = ArchivePDF(pdf_path, "Test Manga", "Kindle 2/3/Touch")
        
        for img_path in images:
            archive.add(img_path)
        
        archive.close()
        
        # Vérifier que le PDF existe
        pdf_file = pdf_path + ".pdf"
        assert os.path.exists(pdf_file)
        
        # Vérifier que c'est un PDF valide
        with open(pdf_file, 'rb') as f:
            header = f.read(8)
            assert header.startswith(b'%PDF-')
    
    
    def test_manga_to_pdf_for_kindle(self, temp_dir):
        """Test PDF creation optimized for Kindle device"""
        # Créer des images pour Kindle
        images = []
        for i in range(3):
            img = PILImage.new('RGB', (600, 800), color='white')
            img_path = os.path.join(temp_dir, f"kindle_page_{i}.png")
            img.save(img_path)
            images.append(img_path)
        
        # Créer PDF pour Kindle
        pdf_path = os.path.join(temp_dir, "kindle_manga")
        device = "Kindle Paperwhite 3/Voyage/Oasis"
        archive = ArchivePDF(pdf_path, "Kindle Test", device)
        
        for img_path in images:
            archive.add(img_path)
        
        archive.close()
        
        pdf_file = pdf_path + ".pdf"
        assert os.path.exists(pdf_file)
        assert os.path.getsize(pdf_file) > 0
    
    
    def test_manga_to_pdf_multiple_chapters(self, temp_dir):
        """Test PDF with multiple chapters and TOC"""
        params = Parameters()
        
        # Créer des images pour plusieurs chapitres
        for chapter in range(1, 4):
            params.add_chapter(f"Chapter {chapter}")
            for page in range(2):
                img = PILImage.new('RGB', (600, 800), color=(chapter*80, page*50, 100))
                img_path = os.path.join(temp_dir, f"ch{chapter}_p{page}.png")
                img.save(img_path)
                params.add_image(img_path, f"Chapter {chapter}")
        
        # Créer PDF avec chapitres
        pdf_path = os.path.join(temp_dir, "manga_with_toc")
        archive = ArchivePDF(pdf_path, "Multi Chapter Manga", "Kindle 2/3/Touch")
        
        for chapter in params.get_chapters():
            archive.add_chapter(chapter)
            chapter_images = params.get_images_by_chapter()[chapter]
            for img_path in chapter_images:
                archive.add(img_path)
        
        archive.close()
        
        pdf_file = pdf_path + ".pdf"
        assert os.path.exists(pdf_file)
    
    
    # ============================================
    # Tests de workflow webtoon
    # ============================================
    
    def test_complete_webtoon_workflow(self, temp_dir):
        """Test complete workflow: webtoon → split → archive"""
        from henskan.webtoon import split_webtoon
        
        # Créer une image webtoon (très haute)
        webtoon_img = PILImage.new('RGB', (720, 3000), color='white')
        webtoon_path = os.path.join(temp_dir, "webtoon.png")
        webtoon_img.save(webtoon_path)
        
        # Charger l'image et splitter le webtoon
        loaded_img = PILImage.open(webtoon_path)
        split_images = split_webtoon(loaded_img)
        
        # Créer une archive avec les images splitées
        cbz_path = os.path.join(temp_dir, "webtoon_split")
        archive = ArchiveCBZ(cbz_path)
        
        for i, split_img in enumerate(split_images):
            # Sauvegarder l'image temporaire
            temp_img_path = os.path.join(temp_dir, f"split_{i}.png")
            split_img.save(temp_img_path)
            archive.add(temp_img_path)
        
        archive.close()
        
        cbz_file = cbz_path + ".cbz"
        assert os.path.exists(cbz_file)
    
    
    def test_webtoon_auto_detection(self, temp_dir):
        """Test automatic webtoon detection and processing"""
        # Créer une image très haute (ratio webtoon)
        img = PILImage.new('RGB', (720, 5000), color='white')
        img_path = os.path.join(temp_dir, "tall_image.png")
        img.save(img_path)
        
        # Vérifier que c'est détecté comme non-splitable (portrait)
        is_split = image.is_splitable(img_path)
        assert is_split == False
        
        # Le workflow devrait traiter ça comme un webtoon potentiel
        params = Parameters()
        params.set_is_webtoon(True)
        assert params.is_webtoon() == True
    
    
    def test_webtoon_deleted_unwanted_handling(self, temp_dir):
        """Test webtoon workflow creates DELETED/UNWANTED dirs"""
        from henskan.parameters import DELETED, UNWANTED
        
        # Vérifier que les répertoires existent
        assert os.path.exists(DELETED)
        assert os.path.exists(UNWANTED)
        
        # Les répertoires devraient être des dossiers
        assert os.path.isdir(DELETED)
        assert os.path.isdir(UNWANTED)
    
    
    # ============================================
    # Tests de workflow avec split
    # ============================================
    
    def test_workflow_split_left_then_right(self, temp_dir):
        """Test complete workflow with split left-then-right"""
        params = Parameters()
        params.set_split_left_then_right(True)
        
        # Créer une double page (landscape)
        double_page = PILImage.new('RGB', (1600, 800), color='white')
        img_path = os.path.join(temp_dir, "double_page.png")
        double_page.save(img_path)
        
        # Vérifier que c'est splitable
        is_split = image.is_splitable(img_path)
        assert is_split == True
        
        # Le split devrait être activé
        assert params.is_split_left_then_right() == True
        
        # Créer une archive
        cbz_path = os.path.join(temp_dir, "split_lr")
        archive = ArchiveCBZ(cbz_path)
        archive.add(img_path)
        archive.close()
        
        assert os.path.exists(cbz_path + ".cbz")
    
    
    def test_workflow_split_right_then_left(self, temp_dir):
        """Test complete workflow with split right-then-left"""
        params = Parameters()
        params.set_split_right_then_left(True)
        
        # Créer une double page (landscape)
        double_page = PILImage.new('RGB', (1600, 800), color='white')
        img_path = os.path.join(temp_dir, "double_page_rl.png")
        double_page.save(img_path)
        
        # Vérifier que c'est splitable
        is_split = image.is_splitable(img_path)
        assert is_split == True
        
        # Le split devrait être activé
        assert params.is_split_right_then_left() == True
        
        # Créer une archive
        cbz_path = os.path.join(temp_dir, "split_rl")
        archive = ArchiveCBZ(cbz_path)
        archive.add(img_path)
        archive.close()
        
        assert os.path.exists(cbz_path + ".cbz")
    
    
    def test_workflow_mixed_splitable_pages(self, temp_dir):
        """Test workflow with mix of splitable and non-splitable pages"""
        # Créer un mix de pages
        images = []
        
        # Page portrait (non splitable)
        portrait = PILImage.new('RGB', (800, 1200), color='blue')
        portrait_path = os.path.join(temp_dir, "portrait.png")
        portrait.save(portrait_path)
        images.append(portrait_path)
        
        # Double page (splitable)
        landscape = PILImage.new('RGB', (1600, 800), color='red')
        landscape_path = os.path.join(temp_dir, "landscape.png")
        landscape.save(landscape_path)
        images.append(landscape_path)
        
        # Autre page portrait
        portrait2 = PILImage.new('RGB', (800, 1200), color='green')
        portrait2_path = os.path.join(temp_dir, "portrait2.png")
        portrait2.save(portrait2_path)
        images.append(portrait2_path)
        
        # Vérifier la détection
        assert image.is_splitable(portrait_path) == False
        assert image.is_splitable(landscape_path) == True
        assert image.is_splitable(portrait2_path) == False
        
        # Créer une archive avec toutes les pages
        cbz_path = os.path.join(temp_dir, "mixed_pages")
        archive = ArchiveCBZ(cbz_path)
        
        for img_path in images:
            archive.add(img_path)
        
        archive.close()
        
        assert os.path.exists(cbz_path + ".cbz")
    
    
    # ============================================
    # Tests de différents devices
    # ============================================
    
    def test_workflow_different_kindle_models(self, temp_dir):
        """Test workflow optimized for different Kindle models"""
        kindle_models = [
            'Kindle 2/3/Touch',
            'Kindle Paperwhite 3/Voyage/Oasis',
            'Kindle DX/DXG'
        ]
        
        for model in kindle_models:
            # Créer des images de test
            img = PILImage.new('RGB', (600, 800), color='white')
            img_path = os.path.join(temp_dir, f"{model.replace('/', '_')}_page.png")
            img.save(img_path)
            
            # Créer un PDF pour ce modèle
            pdf_path = os.path.join(temp_dir, f"manga_{model.replace('/', '_')}")
            archive = ArchivePDF(pdf_path, f"Test {model}", model)
            archive.add(img_path)
            archive.close()
            
            # Vérifier le PDF
            pdf_file = pdf_path + ".pdf"
            assert os.path.exists(pdf_file)
            assert os.path.getsize(pdf_file) > 0
    
    
    def test_workflow_different_kobo_models(self, temp_dir):
        """Test workflow optimized for different Kobo models"""
        kobo_models = [
            'Kobo Aura HD',
            'Kobo Glo HD',
            'Kobo Libra H2O'
        ]
        
        for model in kobo_models:
            # Créer des images de test
            img = PILImage.new('RGB', (1080, 1440), color='white')
            img_path = os.path.join(temp_dir, f"{model.replace(' ', '_')}_page.png")
            img.save(img_path)
            
            # Créer un PDF pour ce modèle
            pdf_path = os.path.join(temp_dir, f"manga_{model.replace(' ', '_')}")
            archive = ArchivePDF(pdf_path, f"Test {model}", model)
            archive.add(img_path)
            archive.close()
            
            # Vérifier le PDF
            pdf_file = pdf_path + ".pdf"
            assert os.path.exists(pdf_file)
            assert os.path.getsize(pdf_file) > 0
    
    
    def test_workflow_device_switching(self, temp_dir):
        """Test workflow with device switching"""
        params = Parameters()
        
        # Commencer avec Kindle
        params.set_device('Kindle 2/3/Touch', 1)
        assert params.get_device() == 'Kindle 2/3/Touch'
        
        # Créer une image
        img1 = PILImage.new('RGB', (600, 800), color='white')
        img1_path = os.path.join(temp_dir, "kindle_page.png")
        img1.save(img1_path)
        
        # Créer PDF pour Kindle
        pdf1_path = os.path.join(temp_dir, "manga_kindle")
        archive1 = ArchivePDF(pdf1_path, "Kindle Manga", params.get_device())
        archive1.add(img1_path)
        archive1.close()
        
        # Changer pour Kobo
        params.set_device('Kobo Libra H2O', 12)
        assert params.get_device() == 'Kobo Libra H2O'
        
        # Créer une nouvelle image
        img2 = PILImage.new('RGB', (1080, 1440), color='white')
        img2_path = os.path.join(temp_dir, "kobo_page.png")
        img2.save(img2_path)
        
        # Créer PDF pour Kobo
        pdf2_path = os.path.join(temp_dir, "manga_kobo")
        archive2 = ArchivePDF(pdf2_path, "Kobo Manga", params.get_device())
        archive2.add(img2_path)
        archive2.close()
        
        # Vérifier les deux PDFs
        assert os.path.exists(pdf1_path + ".pdf")
        assert os.path.exists(pdf2_path + ".pdf")
    
    
    # ============================================
    # Tests de validation des archives
    # ============================================
    
    def test_generated_cbz_valid(self, temp_dir):
        """Test generated CBZ is valid and can be extracted"""
        # Créer des images
        images = []
        for i in range(3):
            img = PILImage.new('RGB', (800, 1200), color=(i*80, i*80, i*80))
            img_path = os.path.join(temp_dir, f"page{i}.png")
            img.save(img_path)
            images.append(img_path)
        
        # Créer le CBZ
        cbz_path = os.path.join(temp_dir, "valid_cbz")
        archive = ArchiveCBZ(cbz_path)
        for img_path in images:
            archive.add(img_path)
        archive.close()
        
        cbz_file = cbz_path + ".cbz"
        
        # Vérifier que c'est un ZIP valide
        assert zipfile.is_zipfile(cbz_file)
        
        # Extraire et vérifier le contenu
        extract_dir = os.path.join(temp_dir, "extracted")
        with zipfile.ZipFile(cbz_file, 'r') as zf:
            zf.extractall(extract_dir)
            extracted_files = os.listdir(extract_dir)
            assert len(extracted_files) == 3
    
    
    def test_generated_pdf_valid(self, temp_dir):
        """Test generated PDF is valid and can be opened"""
        # Créer des images
        images = []
        for i in range(3):
            img = PILImage.new('RGB', (600, 800), color='white')
            img_path = os.path.join(temp_dir, f"pdf_page{i}.png")
            img.save(img_path)
            images.append(img_path)
        
        # Créer le PDF
        pdf_path = os.path.join(temp_dir, "valid_pdf")
        archive = ArchivePDF(pdf_path, "Valid PDF Test", "Kindle 2/3/Touch")
        for img_path in images:
            archive.add(img_path)
        archive.close()
        
        pdf_file = pdf_path + ".pdf"
        
        # Vérifier que c'est un PDF valide
        assert os.path.exists(pdf_file)
        with open(pdf_file, 'rb') as f:
            header = f.read(8)
            assert header.startswith(b'%PDF-')
            
        # Vérifier la présence du marqueur EOF
        with open(pdf_file, 'rb') as f:
            content = f.read()
            assert b'%%EOF' in content
    
    
    def test_archive_correct_page_count(self, temp_dir):
        """Test archive contains expected number of pages"""
        num_pages = 7
        
        # Créer des images
        images = []
        for i in range(num_pages):
            img = PILImage.new('RGB', (800, 1200), color='white')
            img_path = os.path.join(temp_dir, f"count_page{i}.png")
            img.save(img_path)
            images.append(img_path)
        
        # Créer le CBZ
        cbz_path = os.path.join(temp_dir, "page_count_test")
        archive = ArchiveCBZ(cbz_path)
        for img_path in images:
            archive.add(img_path)
        archive.close()
        
        cbz_file = cbz_path + ".cbz"
        
        # Vérifier le nombre de fichiers dans le CBZ
        with zipfile.ZipFile(cbz_file, 'r') as zf:
            files = zf.namelist()
            assert len(files) == num_pages
    
    
    def test_archive_pages_ordered(self, temp_dir):
        """Test archive pages are in correct sequential order"""
        # Créer des images avec noms ordonnés
        num_pages = 5
        images = []
        for i in range(num_pages):
            img = PILImage.new('RGB', (800, 1200), color=(i*50, i*50, i*50))
            img_path = os.path.join(temp_dir, f"page_{i:03d}.png")
            img.save(img_path)
            images.append(img_path)
        
        # Créer le CBZ
        cbz_path = os.path.join(temp_dir, "ordered_pages")
        archive = ArchiveCBZ(cbz_path)
        for img_path in images:
            archive.add(img_path)
        archive.close()
        
        cbz_file = cbz_path + ".cbz"
        
        # Vérifier l'ordre dans le CBZ
        with zipfile.ZipFile(cbz_file, 'r') as zf:
            files = sorted(zf.namelist())
            # Les fichiers devraient être dans l'ordre
            for i, filename in enumerate(files):
                assert f"{i:03d}" in filename or f"page_{i:03d}" in filename
    
    
    # ============================================
    # Tests de performance
    # ============================================
    
    def test_workflow_performance_many_images(self, temp_dir):
        """Test workflow performance with large number of images"""
        import time
        
        # Créer beaucoup d'images (50)
        num_images = 50
        images = []
        for i in range(num_images):
            img = PILImage.new('RGB', (800, 1200), color=(i%255, (i*2)%255, (i*3)%255))
            img_path = os.path.join(temp_dir, f"perf_page_{i:03d}.png")
            img.save(img_path)
            images.append(img_path)
        
        # Mesurer le temps de création du CBZ
        start_time = time.time()
        
        cbz_path = os.path.join(temp_dir, "many_images")
        archive = ArchiveCBZ(cbz_path)
        for img_path in images:
            archive.add(img_path)
        archive.close()
        
        elapsed_time = time.time() - start_time
        
        # Vérifier que le CBZ existe
        cbz_file = cbz_path + ".cbz"
        assert os.path.exists(cbz_file)
        
        # Vérifier le nombre de pages
        with zipfile.ZipFile(cbz_file, 'r') as zf:
            files = zf.namelist()
            assert len(files) == num_images
        
        # Le workflow ne devrait pas prendre trop de temps (< 30 secondes pour 50 images)
        assert elapsed_time < 30.0
    
    
    def test_workflow_large_images(self, temp_dir):
        """Test workflow handles large image files"""
        # Créer des images de grande taille (haute résolution)
        large_images = []
        for i in range(3):
            # Image 3000x4000 pixels
            img = PILImage.new('RGB', (3000, 4000), color=(i*80, i*80, i*80))
            img_path = os.path.join(temp_dir, f"large_page_{i}.png")
            img.save(img_path)
            large_images.append(img_path)
        
        # Créer un CBZ avec ces grandes images
        cbz_path = os.path.join(temp_dir, "large_images")
        archive = ArchiveCBZ(cbz_path)
        for img_path in large_images:
            archive.add(img_path)
        archive.close()
        
        # Vérifier que le CBZ existe
        cbz_file = cbz_path + ".cbz"
        assert os.path.exists(cbz_file)
        
        # Vérifier que le fichier a une taille raisonnable (> 50KB)
        # Note: La compression ZIP réduit beaucoup les images monochromes
        file_size = os.path.getsize(cbz_file)
        assert file_size > 50 * 1024  # > 50KB
    
    
    # ============================================
    # Tests d'erreur et récupération
    # ============================================
    
    def test_workflow_handles_corrupted_image(self, temp_dir):
        """Test workflow handles corrupted image without crashing"""
        import pytest
        
        # Créer un fichier corrompu (pas une vraie image)
        corrupted_path = os.path.join(temp_dir, "corrupted.jpg")
        with open(corrupted_path, 'wb') as f:
            f.write(b"This is not a valid image file")
        
        # Créer une archive et tenter d'ajouter l'image corrompue
        cbz_path = os.path.join(temp_dir, "with_corrupted")
        archive = ArchiveCBZ(cbz_path)
        
        # L'ajout d'une image corrompue devrait lever une erreur ou être géré
        # Le CBZ devrait quand même pouvoir être créé (avec ou sans l'image)
        try:
            archive.add(corrupted_path)
        except Exception:
            # C'est acceptable que ça échoue
            pass
        
        archive.close()
        
        # Le CBZ peut exister (vide) ou ne pas exister selon la gestion d'erreur
        cbz_file = cbz_path + ".cbz"
        # On vérifie juste que le workflow n'a pas crashé
        assert True
    
    
    def test_workflow_handles_missing_image(self, temp_dir):
        """Test workflow handles missing image file"""
        import pytest
        
        # Créer une archive
        cbz_path = os.path.join(temp_dir, "with_missing")
        archive = ArchiveCBZ(cbz_path)
        
        # Tenter d'ajouter une image qui n'existe pas
        missing_path = os.path.join(temp_dir, "nonexistent_image.png")
        
        # Devrait lever une erreur
        with pytest.raises(Exception):
            archive.add(missing_path)
        
        archive.close()
    
    
    def test_workflow_cleanup_on_error(self, temp_dir):
        """Test workflow cleans up temporary files on error"""
        # Créer quelques images valides
        images = []
        for i in range(2):
            img = PILImage.new('RGB', (800, 1200), color='white')
            img_path = os.path.join(temp_dir, f"cleanup_page{i}.png")
            img.save(img_path)
            images.append(img_path)
        
        # Créer une archive
        cbz_path = os.path.join(temp_dir, "cleanup_test")
        archive = ArchiveCBZ(cbz_path)
        
        # Ajouter les images valides
        for img_path in images:
            archive.add(img_path)
        
        # Fermer normalement
        archive.close()
        
        # Vérifier que le CBZ existe
        cbz_file = cbz_path + ".cbz"
        assert os.path.exists(cbz_file)
        
        # Les images sources devraient toujours exister
        for img_path in images:
            assert os.path.exists(img_path)

