from rest_framework.authentication import SessionAuthentication as OldSessionAuthentication, BaseAuthentication
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import exceptions
from django.contrib.auth.models import User, AnonymousUser
from config.settings import CSRF_COOKIE_SECURE


class CSRFCheck(CsrfViewMiddleware):
	def _reject(self, request, reason):
		# Return the failure reason instead of an HttpResponse
		return reason


class SessionAuthentication(OldSessionAuthentication):
	def enforce_csrf(self, request):
		if CSRF_COOKIE_SECURE:
			check = CSRFCheck()
			check.process_request(request)
			reason = check.process_view(request, None, (), {})
			if reason:
				raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)

		else:
			return True


class SessionAuthenticationAnonymous(BaseAuthentication):
	def anonymous_or_real(request):
		
		if request.user.is_authenticated:
			return request.user
		else:
			u = AnonymousUser()
			u.username = 'anon'
			u.first_name = 'Anonymous'
			u.last_name = 'User'
			u.set_unusable_password()

			# comment out the next two lines if you aren't using profiles
			#p = UserProfile(user=u, anonymous=True)
			#p.save()
			self.authenticate(user=u)
			return (request, AnonymousUser())

	def enforce_csrf(self, request):
		return True

	def authenticate(self, request):
		user = getattr(request._request, 'user', None)
		if not user or not user.is_active:
			return (AnonymousUser(), None)


class SessionAuthenticationWithoutCSRF(OldSessionAuthentication):
	def enforce_csrf(self, request):
		return True
