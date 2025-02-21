# Copyright 2011-2019 Alex Yatskov
# Copyright 2020+     Gabès Jean (naparuba@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os.path
import re


# Sort function use to sort files in a natural order, by lowering
# characters, and manage multi levels of integers (tome 1/ page 1.jpg, etc etc)
# cf: See http://www.codinghorror.com/blog/archives/001018.html
def natural_key(string_):
    # type: (str) -> list
    l = []
    for s in re.split(r'(\d+)', string_):
        if s.isdigit():
            l.append(int(s))
        else:
            l.append(s.lower())
    return l


def get_ui_path(relative):
    # type: (str) -> str
    my_dir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(my_dir, relative)


def _find_base_dir_without_tome_number(directory_name):
    # type: (str) -> str
    print(f'\n{directory_name=}')
    lookup_patterns = [r'\sT\d+.*',  # ELDEN RING – T02
                       r'\sTome\s*\d+.*',  # ELDEN RING – Tome 2
                       r'\s*\d+$',  # ELDEN RING – Le chemin vers l’Arbre-Monde - 1
                       r'\s*\d+.*',  # Hellboy (Delcourt) - 01 - Les germes de la destruction
                       ]
    
    # Extract the base title by removing volume/chapter , and remove ALL that is AFTER T03 or Tome03
    for lookup_pattern in lookup_patterns:
        print('lookup_pattern:', lookup_pattern)
        dir_base_title = re.sub(lookup_pattern, '', directory_name, flags=re.IGNORECASE).strip()
        if dir_base_title == directory_name:
            print(f'lookup_pattern: {lookup_pattern=} not found, still {dir_base_title=}')
            continue  # not found
        return dir_base_title
    
    return ''


def find_compact_title(directory_names):
    # type: (list[str]) -> str
    
    directory_names = list(set(directory_names))
    
    if not directory_names:
        return ''
    
    if len(directory_names) == 1:
        return directory_names[0]
    
    # Clean up directory names, remove all () or [] content
    directory_names = [re.sub(r'\[.*?\]', '', re.sub(r'\(.*?\)', '', directory_name)).strip() for directory_name in directory_names]
    
    # Clean up directory by removing all . and _ characters, and replace them by space
    directory_names = [re.sub(r'\.', ' ', re.sub(r'_', ' ', directory_name)).strip() for directory_name in directory_names]
    
    to_del = (r'-', r'#', r'''%''')
    for c in to_del:
        # Clean up directory by removing all - characters
        directory_names = [re.sub(c, '', directory_name).strip() for directory_name in directory_names]
    
    # Clean up directory by removing all multiple spaces and change it by one space
    directory_names = [re.sub(r'\s+', ' ', directory_name).strip() for directory_name in directory_names]
    
    base_title = ''
    for directory_name in directory_names:
        dir_base_title = _find_base_dir_without_tome_number(directory_name)
        
        if not base_title:
            print(f'First match {directory_name=} => {dir_base_title=}')
            base_title = dir_base_title
            continue
        # All subdirectory must match the same base title
        if base_title != dir_base_title:
            print(f'Error: cannot find a common base title for sub directories {base_title=} != {dir_base_title=}')
            return ''
    
    if not base_title:
        return ''
    
    print(f'Base title: {base_title=}')
    
    # Extract volume numbers
    volume_numbers = [int(re.search(r'\d+', chapter, flags=re.IGNORECASE).group()) for chapter in directory_names if re.search(r'\d+', chapter)]
    
    if not volume_numbers:
        return base_title
    
    # Generate the title suffix
    min_volume = min(volume_numbers)
    max_volume = max(volume_numbers)
    
    if min_volume == max_volume:
        title_suffix = f'{min_volume}'
    else:
        title_suffix = f'{min_volume}-{max_volume}'
    
    return f'{base_title} -- {title_suffix}'
