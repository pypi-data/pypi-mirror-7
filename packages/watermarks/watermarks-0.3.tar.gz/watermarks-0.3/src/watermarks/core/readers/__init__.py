import abc
import logging
import os

from PIL import Image

from watermarks.core.method import BaseMethod


logger = logging.getLogger()


class BaseReader(BaseMethod):
    __metaclass__ = abc.ABCMeta

    def __init__(self, destination, format_, suffix='', is_in_chain=False):
        '''
        :param str destination:
            Destination where extracted watermarks will be stored.

        :param str format_:
            Watermark format.

        :param str suffix:
            Suffix added to generated files.

        :param bool is_in_chain:
            True if method is called in chain (more methods are applied).
        '''
        self.destination = destination
        self.format = format_
        self.suffix = suffix
        self.is_in_chain = is_in_chain

    def _generate_files(self, filepath, src_img):
        generated_filepaths = []
        base_name, _ = os.path.splitext(os.path.basename(filepath))
        logger.info('Processing file "%s"', filepath)
        dst_imgs = self._create_watermarked(src_img)
        class_name = self.__class__.__name__.lower()
        for band_name, dst_img in zip(src_img.getbands(), dst_imgs):
            dst_filepath = os.path.join(self.destination, '%s_%s%s%s.%s' % (
                base_name, band_name,
                '_%s' % class_name if self.is_in_chain else '',
                self.suffix, self.format))
            dst_img.save(dst_filepath)
            logger.info('Generated file "%s".', dst_filepath)
            generated_filepaths.append(dst_filepath)
        return generated_filepaths
