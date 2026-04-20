# -*- encoding: utf-8 -*-
from django import forms
from django.contrib.admin import widgets
from django.utils.translation import gettext_lazy as _

from helpers.constants import LANGUAGE_CHOICES, PARAMETER_TYPE, ENDPOINT_MODEL_TYPE, ENDPOINT_MODEL_AUTHENTICATION_TYPE, \
	ENDPOINT_MODEL_AUTHENTICATION_JWT_TYPE
from app.transversal.models import (
	Perfil, Parameter, Endpoint
)
from helpers.functions.utils import tenant_custom_language

from admin_auto_filters.filters import AutocompleteFilter


class PerfilAdminForm(forms.ModelForm):
	password_imed = forms.CharField(
		widget=forms.PasswordInput, required=False, label='Contraseña I-MED',
		help_text=_('Es utilizado para la venta de bonos con I-MED')
	)

	class Meta:
		model = Perfil
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		super(PerfilAdminForm, self).__init__(*args, **kwargs)

		self.fields['language'].choices = LANGUAGE_CHOICES
		result = tenant_custom_language()
		if result['language']:
			self.fields['language'].choices += ((result['language'], result['client']),)
		if not self.instance.id:
			self.initial['reset_password'] = True


class ParametroAdminForm(forms.ModelForm):
	class Meta:
		model = Parameter
		fields = ('key', 'value', 'parameter_type', 'parameter_choices',)

	def __init__(self, *args, **kwargs):
		super(ParametroAdminForm, self).__init__(*args, **kwargs)
		instance = kwargs.get('instance', None)
		if instance and instance.parameter_type == PARAMETER_TYPE['SELECT']:
			choices = (('1', _('Si')), ('0', _('No')))
			parameter_choices = instance.parameter_choices
			if len(parameter_choices):
				choices_structure = [(choice, choice) for choice in parameter_choices]
				choices = tuple(choices_structure)
			self.fields['value'] = forms.ChoiceField(
				required=True,
				choices=choices,
				widget=forms.Select()
			)
