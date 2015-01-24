from io import BytesIO
import os.path

try:
    from PIL import Image, ImageOps
except ImportError:
    import Image
    import ImageOps

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile

from ckeditor import utils

THUMBNAIL_SIZE = (75, 75)


def image_verify(f):
    try:
        Image.open(f).verify()
    except IOError:
        raise utils.NotAnImageException


def resize(file_path, max_width):
    thumbnail_format = utils.get_image_format(os.path.splitext(file_path)[1])
    file_format = thumbnail_format.split('/')[1]

    image = default_storage.open(file_path)
    image = Image.open(image)

    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')

    size_orig = image.size
    width_orig = size_orig[0]

    if width_orig <= max_width:
        size = size_orig
        return
    else:
        height = int(1.0*max_width/width_orig*size_orig[1])
        size = (max_width, height)

    default_storage.delete(file_path)

    # scale and crop to thumbnail
    imagefit = ImageOps.fit(image, size, Image.ANTIALIAS)
    thumbnail_io = BytesIO()
    imagefit.save(thumbnail_io, format=file_format)

    thumbnail = InMemoryUploadedFile(
        thumbnail_io,
        None,
        file_path,
        thumbnail_format,
        len(thumbnail_io.getvalue()),
        None)
    thumbnail.seek(0)

    return default_storage.save(file_path, thumbnail)

def create_thumbnail(file_path):
    thumbnail_filename = utils.get_thumb_filename(file_path)
    thumbnail_format = utils.get_image_format(os.path.splitext(file_path)[1])
    file_format = thumbnail_format.split('/')[1]

    image = default_storage.open(file_path)
    image = Image.open(image)

    # Convert to RGB if necessary
    # Thanks to Limodou on DjangoSnippets.org
    # http://www.djangosnippets.org/snippets/20/
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')

    # scale and crop to thumbnail
    imagefit = ImageOps.fit(image, THUMBNAIL_SIZE, Image.ANTIALIAS)
    thumbnail_io = BytesIO()
    imagefit.save(thumbnail_io, format=file_format)

    thumbnail = InMemoryUploadedFile(
        thumbnail_io,
        None,
        thumbnail_filename,
        thumbnail_format,
        len(thumbnail_io.getvalue()),
        None)
    thumbnail.seek(0)

    return default_storage.save(thumbnail_filename, thumbnail)


def should_create_thumbnail(file_path):
    image = default_storage.open(file_path)
    try:
        Image.open(image)
    except IOError:
        return False
    else:
        return True
