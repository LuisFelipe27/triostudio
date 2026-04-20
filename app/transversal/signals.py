# -*- encoding: utf-8 -*-
from django.db.models.signals import pre_save, pre_delete, post_save, post_delete, m2m_changed
from django.dispatch import receiver

from django.db import connection
from django.apps import apps
from jinja2 import Template
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.utils.html import escape
from django.core.mail.backends.smtp import EmailBackend
from app.multi_tenant.models import Tenant
from app.transversal.models import *
from config.settings import MEDIA_ROOT
from helpers.functions.utils import get_parameter, tenant_current
from helpers.constants import TEMPLATE_NOTIFICATION
import inspect
import os
import json
import requests
import time
import threading


def save_message(model):
    sends = []
    new_mail = NotificationEmail(
        notification=model,
        is_send=False
    )
    new_mail.save()
    sends.append(new_mail)

    return sends

# --------------------------------------------Functions ---------------------------------------------------------------#
def send_mail_message(sender, instance, tenant_schema_name, **kwargs):
    #create_html_content
    def create_html_content(instance):
        context = Template(instance.notification.template.html)

        def escape_dict(object_dict):
            if isinstance(object_dict, dict):
                for key in object_dict:
                    if isinstance(object_dict[key], list):
                        for obj in object_dict[key]:
                            escape_dict(obj)
                    elif isinstance(object_dict[key], dict):
                        escape_dict(object_dict[key])
                    else:
                        object_dict[key] = escape(object_dict[key])

        try:
            cont = json.loads(instance.notification.context)
            escape_dict(cont)
        except Exception as e:
            cont = {}
            print('ERROR ESCAPE_DICT')
            print(e)

        try:
            email_header = Parameter.objects.get(key='EMAIL_HEADER').value
        except Exception:
            email_header = None
        try:
            email_footer = Parameter.objects.get(key='EMAIL_FOOTER').value
        except Exception:
            email_footer = None

        try:
            body_context = context.render(context=cont)
        except Exception:
            try:
                body_context = createtag(context, cont, str(e))
            except Exception as e:
                body_context = {}
                pass

        html_content = render_to_string(
            'email/template.html',
            {
                'body': body_context,
                'email_header': email_header,
                'email_footer': email_footer
            }
        )

        return html_content
    #END

    #createtag
    def createtag(context, cont, new_tag):
        try:
            cont[new_tag] = {}
            body = context.render(context=cont)
            return body
        except Exception as e:
            createtag(context, str(e))
    #END

    if not instance.is_send:
        connection.schema_name = tenant_schema_name
        tenant_data = tenant_current()
        html_content = create_html_content(instance)
        to = []
        mail_provider = instance.notification.template.mail_provider
        mailconfig = mail_provider.parameters()
        if mail_provider.is_active:
            try:
                use_tls = bool(mailconfig.EMAIL_USE_TLS == 'TRUE')
            except Exception:
                use_tls = False
            try:
                use_ssl = bool(mailconfig.EMAIL_USE_SSL == 'TRUE')
            except Exception:
                use_ssl = False

            mailbackend = EmailBackend(host=mailconfig.EMAIL_HOST, port=int(mailconfig.EMAIL_PORT),
                                       username=mailconfig.EMAIL_HOST_USER,
                                       password=mailconfig.EMAIL_HOST_PASSWORD,
                                       use_ssl=use_ssl, use_tls=use_tls)

            destinations = str(instance.notification.destination).split(',')
            for email in destinations:
                if email:
                    to.append(email)

            text = strip_tags(html_content).replace("\n","<br>").replace('\t', '&emsp;')
            msg = EmailMultiAlternatives(
                instance.notification.subject,
                text,
                mailconfig.DEFAULT_FROM_EMAIL,
                to,
                bcc=['lvergara23@gmail.com', 'alma.entretenis@gmail.com'],
                cc=[],
                connection=mailbackend
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            instance.is_send = True
            instance.save()

    return instance.is_send
# -------------------------------------------------------------------------------------------------------------------------#

#------------------------------------------Signals-------------------------------------------------------------------------#
@receiver(post_save, sender=NotificationEmail)
def send_background_mail(sender, instance, **kwargs):
    tenant_schema_name = connection.schema_name
    mail_thread = threading.Thread(target=send_mail_message, args=(sender, instance, tenant_schema_name))
    mail_thread.start()


@receiver(post_save, sender=Notification)
def setting_notificacion(sender, instance, **kwargs):
    if instance.is_read == False:
        tenant_schema_name = connection.schema_name
        res = save_message(instance)
        return res
# ------------------------------------------------------------------------------------------------------------------------#
