# -*- encoding: utf-8 -*-
from admin_auto_filters.filters import AutocompleteFilter
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _


class ContentTypeAppLabelAutocompleteFilter(AutocompleteFilter):
    title = str(_('Módulo'))
    field_name = 'app_label'
    parameter_name = 'content_type__app_label'
    rel_model = ContentType


class ContentTypeModelAutocompleteFilter(AutocompleteFilter):
    title = str(_('Mantenedor'))
    field_name = 'model'
    parameter_name = 'content_type__model'
    rel_model = ContentType