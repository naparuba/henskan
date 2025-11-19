#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration des images de test et leurs caractéristiques attendues

Ce fichier centralise toutes les métadonnées des images de test.
Les valeurs sont basées sur les vraies images présentes dans tests/images/
"""

# ==============================================================================
# CARACTÉRISTIQUES DES IMAGES DE TEST
# ==============================================================================

TEST_IMAGES = {
    
    # ========== MANGA IMAGES (15 images) ==========
    
    "manga_full_page.jpg":                                           {
        "category":      "manga",
        "description":   "Manga page simple portrait",
        "dimensions":    (800, 1200),
        "aspect_ratio":  0.67,
        "is_landscape":  False,
        "is_splitable":  False,
        "expected_type": "manga",
    },
    
    "manga_full_page_landscape.jpg":                                 {
        "category":      "manga",
        "description":   "Manga page paysage",
        "dimensions":    (1600, 1139),
        "aspect_ratio":  1.40,
        "is_landscape":  True,
        "is_splitable":  True,
        "expected_type": "manga",
    },
    
    "manga_bad_quality.jpg":                                         {
        "category":      "manga",
        "description":   "Manga basse qualité/résolution",
        "dimensions":    (391, 645),
        "aspect_ratio":  0.61,
        "is_landscape":  False,
        "quality":       "low",
        "expected_type": "manga",
    },
    
    "manga_scan_double_page.jpg":                                    {
        "category":             "manga",
        "description":          "Manga double page scannée",
        "dimensions":           (1600, 1200),
        "aspect_ratio":         1.33,
        "is_landscape":         True,
        "is_splitable":         True,
        "expected_split_count": 2,
        "expected_type":        "manga",
    },
    
    "manga_double_page_old_school_can_remove_page_number.jpg":       {
        "category":             "manga",
        "description":          "Double page ancienne avec numéros",
        "dimensions":           (1654, 1200),
        "aspect_ratio":         1.38,
        "is_landscape":         True,
        "is_splitable":         True,
        "has_page_numbers":     True,
        "expected_split_count": 2,
        "expected_type":        "manga",
    },
    
    "manga_double_page_old_school_can_remove_page_number_again.jpg": {
        "category":             "manga",
        "description":          "Double page ancienne variante",
        "dimensions":           (1100, 894),
        "aspect_ratio":         1.23,
        "is_landscape":         True,
        "is_splitable":         True,
        "has_page_numbers":     True,
        "expected_split_count": 2,
        "expected_type":        "manga",
    },
    
    "manga_old_double_page_bad_quality.jpg":                         {
        "category":             "manga",
        "description":          "Double page ancienne basse qualité",
        "dimensions":           (1525, 1207),
        "aspect_ratio":         1.26,
        "is_landscape":         True,
        "is_splitable":         True,
        "quality":              "low",
        "expected_split_count": 2,
        "expected_type":        "manga",
    },
    
    "manga_can_remove_page_number.jpg":                              {
        "category":         "manga",
        "description":      "Manga avec numéro de page à retirer",
        "dimensions":       (1258, 1920),
        "aspect_ratio":     0.66,
        "is_landscape":     False,
        "has_page_numbers": True,
        "expected_type":    "manga",
    },
    
    "manga_clean_can_remove_page_number.jpg":                        {
        "category":         "manga",
        "description":      "Manga propre avec numéro de page",
        "dimensions":       (1920, 2730),
        "aspect_ratio":     0.70,
        "is_landscape":     False,
        "has_page_numbers": True,
        "quality":          "high",
        "expected_type":    "manga",
    },
    
    "manga_can_remove_white_on_top.jpg":                             {
        "category":        "manga",
        "description":     "Manga avec bordure blanche en haut",
        "dimensions":      (1200, 1800),
        "aspect_ratio":    0.67,
        "is_landscape":    False,
        "has_borders":     True,
        "border_location": "top",
        "should_crop":     True,
        "expected_type":   "manga",
    },
    
    "manga_clean_only_white_on_left.jpg":                            {
        "category":        "manga",
        "description":     "Manga avec bordure blanche à gauche",
        "dimensions":      (1200, 1884),
        "aspect_ratio":    0.64,
        "is_landscape":    False,
        "has_borders":     True,
        "border_location": "left",
        "should_crop":     True,
        "expected_type":   "manga",
    },
    
    "manga_lot_of_white_around.jpg":                                 {
        "category":        "manga",
        "description":     "Manga avec beaucoup de bordures blanches",
        "dimensions":      (1661, 2407),
        "aspect_ratio":    0.69,
        "is_landscape":    False,
        "has_borders":     True,
        "border_location": "all",
        "should_crop":     True,
        "border_size":     "large",
        "expected_type":   "manga",
    },
    
    "manga_lot_of_white_around_again.jpg":                           {
        "category":        "manga",
        "description":     "Manga variante bordures blanches",
        "dimensions":      (1661, 2407),
        "aspect_ratio":    0.69,
        "is_landscape":    False,
        "has_borders":     True,
        "border_location": "all",
        "should_crop":     True,
        "border_size":     "large",
        "expected_type":   "manga",
    },
    
    "manga_whit_onomatope.jpg":                                      {
        "category":         "manga",
        "description":      "Manga avec onomatopées",
        "dimensions":       (1258, 1920),
        "aspect_ratio":     0.66,
        "is_landscape":     False,
        "has_onomatopoeia": True,
        "expected_type":    "manga",
    },
    
    # ========== COMICS IMAGES (12 images) ==========
    
    "comics_classic.jpg":                                            {
        "category":      "comics",
        "description":   "Comics style classique",
        "dimensions":    (563, 800),
        "aspect_ratio":  0.70,
        "is_landscape":  False,
        "style":         "classic",
        "expected_type": "manga",  # Pas assez vertical pour webtoon
    },
    
    "comics_full_page.jpg":                                          {
        "category":      "comics",
        "description":   "Comics page complète",
        "dimensions":    (500, 774),
        "aspect_ratio":  0.65,
        "is_landscape":  False,
        "expected_type": "manga",
    },
    
    "comics_double_page.jpg":                                        {
        "category":             "comics",
        "description":          "Comics double page haute résolution",
        "dimensions":           (3840, 2931),
        "aspect_ratio":         1.31,
        "is_landscape":         True,
        "is_splitable":         True,
        "quality":              "very_high",
        "expected_split_count": 2,
        "expected_type":        "manga",
    },
    
    "comics_linear.jpg":                                             {
        "category":      "comics",
        "description":   "Comics disposition linéaire",
        "dimensions":    (700, 1098),
        "aspect_ratio":  0.64,
        "is_landscape":  False,
        "layout":        "linear",
        "expected_type": "manga",
    },
    
    "comics_homonope.jpg":                                           {
        "category":         "comics",
        "description":      "Comics avec onomatopées",
        "dimensions":       (492, 800),
        "aspect_ratio":     0.62,
        "is_landscape":     False,
        "has_onomatopoeia": True,
        "expected_type":    "manga",
    },
    
    "comics_not_in_blocs.jpg":                                       {
        "category":      "comics",
        "description":   "Comics sans structure en blocs",
        "dimensions":    (500, 800),
        "aspect_ratio":  0.63,
        "is_landscape":  False,
        "layout":        "free",
        "expected_type": "manga",
    },
    
    "comics_old_colors.jpg":                                         {
        "category":      "comics",
        "description":   "Comics anciennes couleurs",
        "is_color":      True,
        "style":         "vintage",
        "expected_type": "manga",
    },
    
    "comics_very_vertical.jpg":                                      {
        "category":           "comics",
        "description":        "Comics très vertical (webtoon-like)",
        "is_landscape":       False,
        "height_width_ratio": None,  # > 4.0 probablement
        "expected_type":      "webtoon",  # Si ratio > 4
    },
    
    "comics_white_background.jpg":                                   {
        "category":         "comics",
        "description":      "Comics fond blanc",
        "dimensions":       (1404, 1872),
        "aspect_ratio":     0.75,
        "is_landscape":     False,
        "background_color": "white",
        "dominant_color":   (255, 255, 255),
        "expected_type":    "manga",
    },
    
    "comics_black_background.jpg":                                   {
        "category":         "comics",
        "description":      "Comics fond noir (noir dominant)",
        "background_color": "black",
        "dominant_color":   (0, 0, 0),
        "high_contrast":    True,
        "expected_type":    "manga",
    },
    
    "comics_bull_black_background.jpg":                              {
        "category":         "comics",
        "description":      "Comics 'Bull' fond noir",
        "dimensions":       (1920, 2857),
        "aspect_ratio":     0.67,
        "is_landscape":     False,
        "background_color": "black",
        "dominant_color":   (0, 0, 0),
        "high_contrast":    True,
        "expected_type":    "manga",
    },
    
    "comics_lot_of_black.jpg":                                       {
        "category":       "comics",
        "description":    "Comics beaucoup de noir",
        "dimensions":     (940, 1475),
        "aspect_ratio":   0.64,
        "is_landscape":   False,
        "has_dark_areas": True,
        "expected_type":  "manga",
    },
    
    "comics_can_remove_page_number.jpg":                             {
        "category":         "comics",
        "description":      "Comics avec numéro de page",
        "dimensions":       (1920, 2533),
        "aspect_ratio":     0.76,
        "is_landscape":     False,
        "has_page_numbers": True,
        "expected_type":    "manga",
    },
    
    # ========== WEBTOON IMAGES (4 images) ==========
    
    "webtoon_lot_of_white.jpg":                                      {
        "category":             "webtoon",
        "description":          "Webtoon avec beaucoup de zones blanches séparatrices",
        "dimensions":           (720, 5342),
        "aspect_ratio":         0.13,
        "height_width_ratio":   7.42,  # 5342 / 720
        "is_landscape":         False,
        "is_vertical":          True,
        "background_color":     "white",
        "has_white_separators": True,
        "exceeds_soft_max":     True,  # > 1500px
        "exceeds_hard_max":     True,  # > 3000px
        "expected_type":        "webtoon",  # ratio > 4
        "should_split":         True,
    },
    
    "webtoon_lot_of_white_again.jpg":                                {
        "category":             "webtoon",
        "description":          "Webtoon variante avec zones blanches",
        "dimensions":           (720, 4615),
        "aspect_ratio":         0.16,
        "height_width_ratio":   6.41,  # 4615 / 720
        "is_landscape":         False,
        "is_vertical":          True,
        "background_color":     "white",
        "has_white_separators": True,
        "exceeds_soft_max":     True,  # > 1500px
        "exceeds_hard_max":     True,  # > 3000px
        "expected_type":        "webtoon",  # ratio > 4
        "should_split":         True,
    },
    
    "webtoon_mix_background_black_then_white.jpg":                   {
        "category":             "webtoon",
        "description":          "Webtoon avec fond noir puis blanc (mixte)",
        "dimensions":           (720, 5276),
        "aspect_ratio":         0.14,
        "height_width_ratio":   7.33,  # 5276 / 720
        "is_landscape":         False,
        "is_vertical":          True,
        "background_color":     "mixed",  # Noir puis blanc
        "has_mixed_background": True,
        "exceeds_soft_max":     True,  # > 1500px
        "exceeds_hard_max":     True,  # > 3000px
        "expected_type":        "webtoon",  # ratio > 4
        "should_split":         True,
    },
    
    "webtoon_very_big_block_cannot_cut.jpg":                         {
        "category":           "webtoon",
        "description":        "Webtoon avec très gros bloc difficile à découper",
        "dimensions":         (720, 5147),
        "aspect_ratio":       0.14,
        "height_width_ratio": 7.15,  # 5147 / 720
        "is_landscape":       False,
        "is_vertical":        True,
        "has_large_block":    True,
        "difficult_to_split": True,  # Gros bloc sans séparateur clair
        "exceeds_soft_max":   True,  # > 1500px
        "exceeds_hard_max":   True,  # > 3000px
        "expected_type":      "webtoon",  # ratio > 4
        "should_split":       True,  # Mais difficile
    },
}

# ==============================================================================
# CONSTANTES DE RÉFÉRENCE (du module image.py)
# ==============================================================================

MIN_BOX_ALLOWED_HEIGHT = 36  # Hauteur minimale pour une box valide
SOFT_MAX_BLOC_HEIGHT = 1500  # Hauteur soft max, essaie de split
HARD_MAX_BLOC_HEIGHT = 3000  # Hauteur hard max, force le split
QUITE_BLACK_LIMIT = 25  # Seuil pour "presque noir"
MIN_COLOR_HEIGHT = 30  # Hauteur minimale pour une partie colorée
WEBTOON_RATIO_THRESHOLD = 4.0  # height > 4 * width = webtoon


# ==============================================================================
# HELPERS
# ==============================================================================

def get_image_config(filename):
    """Récupère la configuration d'une image de test"""
    return TEST_IMAGES.get(filename, {})


def is_image_configured(filename):
    """Vérifie si une image a sa configuration remplie"""
    config = get_image_config(filename)
    if not config:
        return False
    
    # Vérifier si au moins une caractéristique importante est renseignée
    return config.get("dimensions") is not None


def get_images_by_category(category):
    """Récupère toutes les images d'une catégorie"""
    return {
        name: config
        for name, config in TEST_IMAGES.items()
        if config.get("category") == category
    }


def get_all_image_names():
    """Récupère tous les noms d'images de test"""
    return list(TEST_IMAGES.keys())
