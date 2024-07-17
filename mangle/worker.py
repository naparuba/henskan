import os
import shutil
import time
import traceback

from PyQt6.QtCore import QObject, pyqtSignal, QThread

from .archive import ARCHIVE_FORMATS
from .archive_cbz import ArchiveCBZ
from .archive_pdf import ArchivePDF
from .image import EReaderData, convert_image, save_image, is_splitable
from .parameters import parameters


class Worker(QObject):
    updateProgress = pyqtSignal(int)  # will be called
    
    
    def _convert_and_save(self, source, target, split_right=False, split_left=False):
        # type: (str, str, bool, bool) -> None
        begin = time.time()
        
        converted_images = convert_image(source, split_right=split_right, split_left=split_left)
        
        if split_right:
            print(f"  - Split right {source}")
        if split_left:
            print(f"  - Split left  {source}")
        
        print(f"* convert for {source} => {target}({len(converted_images)})")
        
        # If we have only one image, we can directly use the target
        if len(converted_images) == 1:
            try:
                save_image(converted_images[0], target)
            except:
                print(f'convertAndSave:: ERROR in saveImage: {traceback.format_exc()}')
                return
            if self._archive is not None:
                self._archive.add(target)
        
        else:
            print(f"* convert2 for {target} => {converted_images}")
            base_target = target.replace('.png', '')
            for (idx, converted_image) in enumerate(converted_images):
                n_target = '%s_%04d.png' % (base_target, idx)
                print(f"Want to saves {converted_image} with target: {n_target}")
                try:
                    save_image(converted_image, n_target)
                except:
                    print(f'convertAndSave:: ERROR in saveImage: {traceback.format_exc()}')
                    return
                if self._archive is not None:
                    self._archive.add(n_target)
        
        print(f" * Convert & save in {time.time() - begin:.3f}s for {target}")
    
    
    def _tick(self):
        index = self._index_value
        pages_split = self._split_page_offset
        target = os.path.join(self._book_path, '%05d.png' % (index + pages_split))
        source = parameters._images[index]
        
        if index == 0:
            try:
                if not os.path.isdir(self._book_path):
                    os.makedirs(self._book_path)
            except OSError:
                print(f'Cannot create directory {self._book_path} {traceback.format_exc()}')
                raise
        
        print(f'Processing {os.path.split(source)[1]}...')
        
        try:
            # Asked for split: maybe we cannot
            if parameters.is_split_left_then_right() or parameters.is_split_right_then_left():
                can_be_split = is_splitable(source)  # is image large enough to be split?
                if can_be_split:
                    # Generate 2 images: right, then left
                    if parameters.is_split_right_then_left():
                        self._convert_and_save(source, target, split_right=True)
                        
                        # Change target for left page
                        target = os.path.join(self._book_path, '%05d.png' % (index + pages_split + 1))
                        self._split_page_offset += 1
                        self._convert_and_save(source, target, split_left=True)
                    
                    # just the other order
                    else:
                        self._convert_and_save(source, target, split_left=True)
                        
                        # Change target for left page
                        target = os.path.join(self._book_path, '%05d.png' % (index + pages_split + 1))
                        self._split_page_offset += 1
                        self._convert_and_save(source, target, split_right=True)
                
                else:  # simple page (un-splitable) on a split manga
                    self._convert_and_save(source, target)
            else:
                # Convert page
                self._convert_and_save(source, target)
        
        except RuntimeError:
            raise RuntimeError(f'Error while processing {source} {traceback.format_exc()}')
        
        self._index_value += 1
    
    
    def run(self):
        self._index_value = 0
        self._split_page_offset = 0
        parameters.set_title('test')
        
        directory = r'C:\Users\napar\Desktop\export'
        self._split_page_offset = 0
        self._book_path = os.path.join(directory, parameters.get_title())
        self._archive = None
        device = parameters.get_device()
        output_format = EReaderData.get_archive_format(device)
        if ARCHIVE_FORMATS.CBZ == output_format:
            self._archive = ArchiveCBZ(self._book_path)
        elif ARCHIVE_FORMATS.PDF == output_format:
            self._archive = ArchivePDF(self._book_path, parameters.get_title(), parameters.get_device())
        
        for i in range(len(parameters.get_images())):
            self._tick()
            pct = int(i / len(parameters.get_images()) * 100)
            self.updateProgress.emit(pct)
            QThread.msleep(1)
        print(f'Worker::run::Finished processing images')
        
        # Close the CBZ/PDF
        if self._archive is not None:
            self._archive.close()
        
        print(f'Cleaning temporary directory {self._book_path}')
        shutil.rmtree(self._book_path)
        
        print(f'Worker::run::Exiting')
