from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import magic
import os


def file_path_mime(file_path):
    mime = magic.from_file(file_path, mime=True)
    return mime


def check_in_memory_mime(in_memory_file, read_file=True):
    if read_file:
        file = in_memory_file.read()
    else:
        file = in_memory_file

    mime = magic.from_buffer(file, mime=True)

    return mime


def validate_file_extension(value):

    valid_extensions = [
        '.jpg',
        '.jpeg',
        '.png',
        '.pdf',
        '.doc',
        # '.docx',
        '.xlsx',
        '.xls',
        '.ppt',
        '.pptx',
        '.tif',
        '.tiff',
        '.bmp',
        '.jfif',
        '.ics',
    ]
    valid_contenttype = [
        'image/jpeg',
        'image/png',
        'image/tif',
        'image/tiff',
        'image/bmp',
        'image/x-ms-bmp',
        'image/jfif',
        'application/pdf',
        'application/msword',
        # 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'text/calendar'
    ]

    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'La extensión "%s" no está permitida.' % (ext.lower()))

    elif value._file and not check_in_memory_mime(value._file) in valid_contenttype:
        raise ValidationError(u'El formato del archivo es incorrecto.')


def validate_file_extension_odt(value):
    valid_extensions = ['.odt']
    valid_contenttype = ['application/vnd.oasis.opendocument.text']

    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Solo se permite la extensión ".odt".')

    elif value._file and not check_in_memory_mime(value._file) in valid_contenttype:
        raise ValidationError(u'El formato del archivo es incorrecto.')


def validate_file_extension_img(value):
    valid_extensions = [
        '.jpg',
        '.jpeg',
        '.png'
    ]
    valid_contenttype = [
        'image/jpeg',
        'image/png'
    ]

    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Solo se permiten imágenes con las extensiones ".jpg", ".png".')

    elif value._file and not check_in_memory_mime(value._file) in valid_contenttype:
        raise ValidationError(u'El formato del archivo es incorrecto.')


def validate_file_extension_xls(value):
    valid_extensions = ['.xls', '.xlsx']
    valid_contenttype = [
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/zip'
    ]

    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    if not ext.lower() in valid_extensions:
        raise ValidationError(
            _('Solo se permiten archivos con la extensión ".xls" / ".xlsx".')
        )

    elif value._file and not check_in_memory_mime(value._file) in valid_contenttype:
        raise ValidationError(_('El formato del archivo es incorrecto.'))


def validate_file_extension_doc(value):
    valid_extensions = ['.pdf', '.doc']
    valid_contenttype = [
        'application/pdf',
        'application/msword'
    ]

    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    if not ext.lower() in valid_extensions:
        raise ValidationError(
            _('Solo se permiten archivos con la extensión ".pdf" o ".doc".')
        )

    elif value._file and not check_in_memory_mime(value._file) in valid_contenttype:
        raise ValidationError(_('El formato del archivo es incorrecto.'))


def validate_file_extension_pdf(value):
    valid_extensions = ['.pdf']
    valid_contenttype = [
        'application/pdf'
    ]

    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    if not ext.lower() in valid_extensions:
        raise ValidationError(
            _('Solo se permiten archivos con la extensión ".pdf".')
        )

    elif value._file and not check_in_memory_mime(value._file) in valid_contenttype:
        raise ValidationError(_('El formato del archivo es incorrecto.'))
