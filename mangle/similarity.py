import time

try:
    from imagehash import imagehash
except ImportError:
    imagehash = None
    print "Missing imagehash lib"
import os
from image import Image

UNWANTED = r'C:\Users\j.gabes\Desktop\export\unwanted'
DELETED = r'C:\Users\j.gabes\Desktop\export\deleted'

# Mine are for debug, on other pc, use documents ones
if not os.path.exists(UNWANTED):
    UNWANTED = os.path.expanduser('~/Documents/mangle_unwanted')
    if not os.path.exists(UNWANTED):
        os.mkdir(UNWANTED)
if not os.path.exists(DELETED):
    DELETED = os.path.expanduser('~/Documents/mangle_deleted')
    if not os.path.exists(DELETED):
        os.mkdir(DELETED)

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
            print "CANNOT SAVE DELETED"
            return
        print " * Cleaning deleted dir: %s" % DELETED
        for f_path in os.listdir(DELETED):
            full_path = os.path.join(DELETED, f_path)
            os.unlink(full_path)
    
    
    def _load(self):
        t0 = time.time()
        print " * Loading unwanted images: %s" % UNWANTED
        for f_path in os.listdir(UNWANTED):
            full_path = os.path.join(UNWANTED, f_path)
            hash = imagehash.average_hash(Image.open(full_path), hash_size=HASH_SIZE)
            self._unwanted_hashes[f_path] = hash
        print "   - %s hashed loaded in %.3fs" % (len(self._unwanted_hashes), time.time() - t0)
    
    
    def add_deleted_image(self, f_path, image, diff, do_move):
        self._nb_deleted += 1
        print " * Image is unwanted (from %s), deleted=%s" % (f_path, self._nb_deleted)
        save_deleted_path = os.path.join(DELETED, 'deleted_%s--diff_%s__%s.jpg' % (f_path, diff, self._nb_deleted))
        if do_move:
            image.save(save_deleted_path)
    
    
    def is_valid_image(self, image, do_move=True):
        if imagehash is None:
            print "ERROR: cannot compare unwanted image"
            return True
        elapsed_at_start = int(self._sum_time)
        t0 = time.time()
        hash = imagehash.average_hash(image, hash_size=HASH_SIZE)
        is_valid = True
        for (f_path, ref_hash) in self._unwanted_hashes.iteritems():
            diff = hash - ref_hash
            if diff <= THRESHOLD:
                self.add_deleted_image(f_path, image, diff, do_move=do_move)
                # self._nb_deleted += 1
                # print " * Image is unwanted (from %s), deleted=%s" % (f_path, self._nb_deleted)
                # save_deleted_path = os.path.join(DELETED, 'deleted_%s--diff_%s__%s.jpg' % (f_path, diff, self._nb_deleted))
                # if do_move:
                #     image.save(save_deleted_path)
                is_valid = False
                break
        self._sum_time += (time.time() - t0)
        if int(self._sum_time) != elapsed_at_start:
            print "[UNWANTED:] Consume time= %s" % int(self._sum_time)
        return is_valid


similarity = Similarity()
