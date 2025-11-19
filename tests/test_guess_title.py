import unittest
from henskan.util import find_compact_title


class TestFindCompactTitle(unittest.TestCase):
    
    def test_no_directory_names(self):
        self.assertEqual(find_compact_title([]), '')
    
    
    def test_one_volume_number(self):
        directory_names = ['Title T1']
        self.assertEqual(find_compact_title(directory_names), 'Title T1')
    
    
    def test_different_volume_numbers(self):
        directory_names = ['Title T1', 'Title T2', 'Title T3']
        self.assertEqual(find_compact_title(directory_names), 'Title -- 1-3')
    
    
    def test_same_volume_number(self):
        directory_names = ['Title T1', 'Title T1']
        self.assertEqual(find_compact_title(directory_names), 'Title T1')
    
    
    def test_no_volume_numbers(self):
        directory_names = ['Title', 'Another Title', 'Yet Another Title']
        self.assertEqual(find_compact_title(directory_names), '')  # cannot find a common base title
    
    
    def test_remove_tome_numbers(self):
        directory_names = ['Afro Samurai Tome 01', 'Afro Samurai Tome 02']
        self.assertEqual(find_compact_title(directory_names), 'Afro Samurai -- 1-2')
    
    
    def test_remove_useless_part(self):
        directory_names = ['Assassination Classroom T02 [800]', 'Assassination Classroom T03 [1261]', 'Assassination Classroom T04[1258]']
        self.assertEqual(find_compact_title(directory_names), 'Assassination Classroom -- 2-4')
    
    
    def test_remove_useless_characters(self):
        directory_names = ['Hellsing.Ultimate.T01.(tory).[Digital][1920x3018]', 'Hellsing.Ultimate.T02.(tory).[PapriKa][Digital][1920x3018]']
        self.assertEqual(find_compact_title(directory_names), 'Hellsing Ultimate -- 1-2')
    
    
    def test_remove_useless_characters_and_spaces(self):
        directory_names = ['Battle Royale - Perfect Edition - Tome 01', 'Battle Royale - Perfect Edition - Tome 02']  # Read battle royale!
        self.assertEqual(find_compact_title(directory_names), 'Battle Royale Perfect Edition -- 1-2')
    
    
    def test_remove_useless_parts_after_tome(self):
        directory_names = ['Black Clover T19 - C173 à 183 [161p] (Yuuki TABATA) [Scantrads]',
                           'Black Clover T20 - C184 à 194 [157p] (Yuuki TABATA) [Scantrads]',
                           'Black Clover T21']
        self.assertEqual(find_compact_title(directory_names), 'Black Clover -- 19-21')
    
    
    def test_remove_useless_underscore(self):
        directory_names = ['Chainsaw_Man_T01_French',
                           'Chainsaw_Man_T02_French',
                           'Chainsaw_Man_T3']
        self.assertEqual(find_compact_title(directory_names), 'Chainsaw Man -- 1-3')
    
    
    def test_huge_numbers(self):
        directory_names = ['Detective Conan T99', 'Detective Conan T100', 'Detective Conan T101']
        self.assertEqual(find_compact_title(directory_names), 'Detective Conan -- 99-101')
    
    
    def test_tome_and_space(self):
        directory_names = ['Dragon Ball Kakumei - Tome 01', 'Dragon Ball Kakumei - Tome 02']
        self.assertEqual(find_compact_title(directory_names), 'Dragon Ball Kakumei -- 1-2')
    
    
    def test_no_tome_only_last_digits(self):
        directory_names = ['ELDEN RING – Le chemin vers l’Arbre-Monde - 1', 'ELDEN RING – Le chemin vers l’Arbre-Monde - 2']
        self.assertEqual(find_compact_title(directory_names), 'ELDEN RING – Le chemin vers l’ArbreMonde -- 1-2')
    
    
    def test_no_tome_only_last_digits_and_dash(self):
        directory_names = ['Exaxxion-01', 'Exaxxion-02']
        self.assertEqual(find_compact_title(directory_names), 'Exaxxion -- 1-2')
    
    
    def test_starting_number_in_middle(self):
        directory_names = ['Hellboy (Delcourt) - 01 - Les germes de la destruction',
                           'Hellboy (Delcourt) - 02 - Au nom du diable']
        self.assertEqual('Hellboy -- 1-2', find_compact_title(directory_names))


if __name__ == '__main__':
    unittest.main()
