from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class AuthenticationCustomForm(AuthenticationForm):
	error_messages = {
		"invalid_login": _("Su nombre de usuario o contraseña son incorrectos, por favor intente nuevamente"),
		"inactive": _("Su cuenta esta desactivada."),
		"no_access": _("No tiene autorización para acceder al sistema")
	}

	def clean(self):
		username = self.cleaned_data.get("username")
		password = self.cleaned_data.get("password")

		if username is not None and password:
			self.user_cache = authenticate(
				self.request, username=username, password=password
			)

			only_access_to_apis = False

			try:
				profile = self.user_cache and self.user_cache.perfil or None
				if profile and profile.access_only_for_api:
					only_access_to_apis = True
			except Exception:
				pass

			if self.user_cache is None:
				raise self.get_invalid_login_error()

			elif only_access_to_apis:
				raise ValidationError(
					self.error_messages["no_access"],
					code="no_access",
				)
			else:
				self.confirm_login_allowed(self.user_cache)

		return self.cleaned_data
