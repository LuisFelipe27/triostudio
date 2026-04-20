from pathlib import Path
from copy import copy

from django.conf import settings
from django.core import mail
from django.template import Context, Engine
from django.utils.log import AdminEmailHandler
from django.views.debug import ExceptionReporter

DEBUG_ENGINE = Engine(
    debug=True,
    libraries={'i18n': 'django.templatetags.i18n'},
)


class CustomErrorReport(ExceptionReporter):

    def get_traceback_text(self, admins=True):
        """Return plain text version of debug 500 HTTP error page."""
        if admins:
            template = 'technical_500_admins.txt'
        else:
            template = 'technical_500_managers.txt'

        with Path('app/transversal/templates/django/reports', template).open(encoding='utf-8') as fh:
            t = DEBUG_ENGINE.from_string(fh.read())
        c = Context(self.get_traceback_data(), autoescape=False, use_l10n=False)
        return t.render(c)


class CustomAdminEmailHandler(AdminEmailHandler):
    def send_mail(self, subject, message, admins=True, *args, **kwargs):
        if admins:
            mail.mail_admins(subject, message, *args, connection=self.connection(), **kwargs)
        else:
            mail.mail_managers(subject, message, *args, connection=self.connection(), **kwargs)

    def emit(self, record):
        try:
            request = record.request
            subject = '%s (%s IP): %s' % (
                record.levelname,
                ('internal' if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS
                 else 'EXTERNAL'),
                record.getMessage()
            )
        except Exception as e:
            subject = '%s: %s' % (
                record.levelname,
                record.getMessage()
            )
            request = None
        subject = self.format_subject(subject)

        no_exc_record = copy(record)
        no_exc_record.exc_info = None
        no_exc_record.exc_text = None

        if record.exc_info:
            exc_info = record.exc_info
        else:
            exc_info = (None, record.getMessage(), None)

        reporter = CustomErrorReport(request, is_email=True, *exc_info)
        message_admins = "%s\n\n%s" % (self.format(no_exc_record), reporter.get_traceback_text())
        message_managers = "%s\n\n%s" % (self.format(no_exc_record), reporter.get_traceback_text(admins=False))

        # Email to admins
        self.send_mail(subject, message_admins, admins=True, fail_silently=True, html_message=None)

        # Email to managers
        self.send_mail(subject, message_managers, admins=False, fail_silently=True, html_message=None)
