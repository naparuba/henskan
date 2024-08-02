import time
import shutil
import imagehash
import os
from image import Image, _is_full_background_image
from similarity import similarity

SIM_DIR = 'resources/similaires'

all_hashes = {}

print
" * Hashing: %s" % SIM_DIR
files = os.listdir(SIM_DIR)
files.sort()
for f_path in files:
    full_path = os.path.join(SIM_DIR, f_path)
    before = time.time()
    hash = imagehash.average_hash(Image.open(full_path), hash_size=12)
    after = time.time()
    # print "  - %20s : %s (%.3f)" % (f_path, hash, after - before)
    all_hashes[f_path] = hash

already_found = set()
similaires = []

for f_path in files:
    if f_path in already_found:
        continue
    like_me = [f_path]
    already_found.add(f_path)
    my_hash = all_hashes.get(f_path)
    other_files = all_hashes.keys()
    other_files.sort()
    for other_f in other_files:
        if other_f in already_found:
            continue
        other_hash = all_hashes.get(other_f)
        diff = my_hash - other_hash
        if diff <= 6:
            # print "Similaire: %20s - %20s => %s" % (f_path, other_f, diff)
            like_me.append(other_f)
            already_found.add(other_f)
    similaires.append(like_me)

for lst in similaires:
    lst.sort()
    if len(lst) == 1:
        print
        " ** Alone: %s" % lst[0]
    else:
        print
        " - Similaires: %s" % ', '.join(lst)

SRC = r'C:\Users\j.gabes\Desktop\export\Solo Leveling'
DELETED = r'C:\Users\j.gabes\Desktop\export\deleted'
VALID = r'C:\Users\j.gabes\Desktop\export\valid'

valids = os.listdir(VALID)
for f_path in valids:
    os.unlink(os.path.join(VALID, f_path))

files = os.listdir(SRC)
files.sort()
total = len(files)
i = 0
for f_path in files:
    i += 1
    print
    "\r %s %s/%s" % (f_path, i, total)
    full_path = os.path.join(SRC, f_path)
    img = Image.open(full_path)
    
    is_valid = similarity.is_valid_image(img, do_move=False)
    is_full_background = _is_full_background_image(img)
    if is_valid and not is_full_background:
        pth = os.path.join(VALID, f_path)
        shutil.copy(full_path, pth)
    else:
        pth = os.path.join(DELETED, f_path)
        shutil.copy(full_path, pth)
