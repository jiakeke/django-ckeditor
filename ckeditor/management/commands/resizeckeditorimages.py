import os

from django.conf import settings
from django.core.management.base import NoArgsCommand

from ckeditor.views import get_image_files
from ckeditor.utils import get_thumb_filename
from ckeditor.image_processing import get_backend


class Command(NoArgsCommand):
    """
    Creates thumbnail files for the CKEditor file image browser.
    Useful if starting to use django-ckeditor with existing images.
    """
    def handle_noargs(self, **options):
        if getattr(settings, 'CKEDITOR_IMAGE_BACKEND', None):
            backend = get_backend()
            for image in get_image_files():
                max_width = getattr(settings, 'CKEDITOR_LIMIT_WIDTH', 0)
                if max_width:
                    self.stdout.write("Resizing for %s" % image)
                    try:
                        backend.resize(image, max_width)
                    except Exception as e:
                        self.stdout.write("Couldn't resize for %s: %s" % (image, e))
            self.stdout.write("Finished")
        else:
            self.stdout.write("No image backend is enabled")

