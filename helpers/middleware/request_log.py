"""
Middleware to log all requests and responses.
Uses a logger configured by the name of django.request
to log all requests and responses according to configuration
specified for django.request.
"""

from django.utils.deprecation import MiddlewareMixin
from django.apps import apps

import socket
import time
import json


class RequestLogMiddleware(MiddlewareMixin):
    """Request Logging Middleware."""

    def __init__(self, *args, **kwargs):
        """Constructor method."""
        super().__init__(*args, **kwargs)

    def process_request(self, request):
        """Set Request Start Time to measure time taken to service request."""
        if request.method in ['GET', 'POST', 'PUT', 'PATCH']:
            request.req_body = request.body
        # if str(request.get_full_path()).startswith('/api/'):
            request.start_time = time.time()

    def extract_log_info(self, request, response=None, exception=None):
        """Extract appropriate log info from requests/responses/exceptions."""
        log_data = {
            'remote_address': request.META['REMOTE_ADDR'],
            'domain_url': request.META['HTTP_HOST'],
            'server_hostname': socket.gethostname(),
            'request_method': request.method,
            'request_path': request.get_full_path(),
            'run_time': time.time() - request.start_time,
            'request_body': '',
        }

        if request.method in ['PUT', 'POST', 'PATCH']:
            try:
                log_data['request_body'] = json.loads(
                    str(request.req_body, 'utf-8'))
            except Exception:
                try:
                    log_data['request_body'] = str(request.req_body, 'utf-8')
                except Exception:
                    pass

            # if response:
            #     if response['content-type'] == 'application/json':
            #         response_body = response.content
            #         log_data['response_body'] = response_body

        return log_data

    def process_response(self, request, response):
        """Log data using logger."""
        if request.method in ['GET', 'POST', 'PUT', 'PATCH']:
            log_data = self.extract_log_info(request=request,
                                             response=response)

            LogModel = apps.get_model('audit_module', 'RequestLog')

            LogModel.objects.create(
                remote_address=log_data['remote_address'],
                domain_url=log_data['domain_url'],
                server_hostname=log_data['server_hostname'],
                request_method=log_data['request_method'],
                request_path=log_data['request_path'],
                request_body=log_data['request_body'],
                run_time=log_data['run_time']
            )
            # if str(request.get_full_path()).startswith('/api/'):
        return response

    def process_exception(self, request, exception):
        """Log Exceptions."""
        try:
            raise exception
        except Exception:
            raise
        return exception
