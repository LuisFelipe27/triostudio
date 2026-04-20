import django
from threading import current_thread

_requests = {}


def get_current_request():
	t = current_thread()
	if t not in _requests:
		return None
	return _requests[t]


class RequestMiddleware(django.utils.deprecation.MiddlewareMixin):
	def process_request(self, request):
		_requests[current_thread()] = request
