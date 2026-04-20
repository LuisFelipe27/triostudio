from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from tenant_schemas.storage import TenantFileSystemStorage

import unicodedata


class LocalMediaStorage(TenantFileSystemStorage):
    """
    Convert unicode characters in name to ASCII characters.
    """
    def get_valid_name(self, name):
        name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore')
        return super(LocalMediaStorage, self).get_valid_name(name)

    def url(self, name):
        from helpers.functions.utils import tenant_current
        if tenant_current().domain_url in name or tenant_current(is_massiveload=True).domain_url in name:
            return f'{settings.MEDIA_URL_SELF}{name}'
        else:
            return f'{settings.MEDIA_URL_SELF}{tenant_current().domain_url}/{name}'

    def path(self, name):
        from helpers.functions.utils import tenant_current
        if tenant_current().domain_url in name or tenant_current(is_massiveload=True).domain_url in name:
            return f'{settings.MEDIA_ROOT}/{name}'
        else:
            return f'{settings.MEDIA_ROOT}/{tenant_current().domain_url}/{name}'

class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'


class PublicMediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False


class PrivateMediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False

    @property  # not cached like in parent of S3Boto3Storage class
    def location(self):
        try:
            from helpers.functions.utils import tenant_current
            _location = f'{settings.PRIVATE_MEDIA_LOCATION}/{tenant_current().domain_url}'
        except Exception:
            _location = f'{settings.PRIVATE_MEDIA_LOCATION}'
        return _location
