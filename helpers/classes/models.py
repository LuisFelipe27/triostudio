from django.db import models
from django.utils.translation import gettext_lazy as _
from helpers.middleware.request_current import get_current_request


class RecordsModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True, verbose_name=_('Fecha creación'))
    created_by = models.ForeignKey('auth.User', models.CASCADE,
                                   related_name='%(app_label)s_%(class)s_created_by',
                                   null=True, blank=True, verbose_name=_('Creado por'))
    modified = models.DateTimeField(auto_now=True, null=True, verbose_name=_('Fecha modificación'))
    modified_by = models.ForeignKey('auth.User', models.CASCADE,
                                    related_name='%(app_label)s_%(class)s_modified_by',
                                    null=True, blank=True, verbose_name=_('Modificado por'))

    def save(self, *args, **kwargs):
        request = get_current_request()
        if request and not request.user.is_anonymous:
            if not self.id:
                self.created_by = request.user

            else:
                self.modified_by = request.user

        super(RecordsModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True
