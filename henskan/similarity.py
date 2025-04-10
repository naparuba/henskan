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

import time
import os
import imagehash

from .image import Image
from .parameters import UNWANTED, DELETED

THRESHOLD = 6

HASH_SIZE = 10


class Similarity(object):
    def __init__(self):
        self._unwanted_hashes = {}
        
        self._clean()
        self._load()
        
        self._sum_time = 0.0
        self._nb_deleted = 0
    
    
    def _clean(self):
        if not os.path.exists(DELETED):
            print("CANNOT SAVE DELETED")
            return
        print(" * Cleaning deleted dir: %s" % DELETED)
        for f_path in os.listdir(DELETED):
            full_path = os.path.join(DELETED, f_path)
            os.unlink(full_path)
    
    
    def _load(self):
        t0 = time.time()
        print(" * Loading unwanted images: %s" % UNWANTED)
        for f_path in os.listdir(UNWANTED):
            full_path = os.path.join(UNWANTED, f_path)
            try:
                img = Image.open(full_path)
            except Exception as e:
                print(" * Cannot open image %s: %s" % (full_path, e))
                continue
            hash = imagehash.average_hash(img, hash_size=HASH_SIZE)
            self._unwanted_hashes[f_path] = hash
        print("   - %s hashed loaded in %.3fs" % (len(self._unwanted_hashes), time.time() - t0))
    
    
    def _add_deleted_image(self, f_path, image, diff, do_move):
        self._nb_deleted += 1
        print(" * Image is unwanted (from %s), deleted=%s" % (f_path, self._nb_deleted))
        save_deleted_path = os.path.join(DELETED, 'unwanted_similarity_%s--diff_%s__%s.jpg' % (f_path, diff, self._nb_deleted))
        if do_move:
            image.save(save_deleted_path)
    
    
    def is_valid_image(self, image, do_move=True):
        elapsed_at_start = int(self._sum_time)
        t0 = time.time()
        hash = imagehash.average_hash(image, hash_size=HASH_SIZE)
        is_valid = True
        for (f_path, ref_hash) in self._unwanted_hashes.items():
            diff = hash - ref_hash
            #print(f'[SIMILARITY] {f_path} - {diff}')
            if diff <= THRESHOLD:
                self._add_deleted_image(f_path, image, diff, do_move=do_move)
                is_valid = False
                break
        self._sum_time += (time.time() - t0)
        if int(self._sum_time) != elapsed_at_start:
            print("[UNWANTED:] Consume time= %s" % int(self._sum_time))
        return is_valid


similarity = Similarity()
