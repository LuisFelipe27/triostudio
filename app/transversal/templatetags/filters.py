#!/usr/bin/env python
import os
from django import template
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_text
from django.contrib.auth.models import Permission

from math import ceil

from helpers.functions.utils import (
    elimina_tildes, removeNonAscii, format_moneda as format_money, normalize_str, language_client
)

from datetime import datetime, date, timedelta

import base64
from dateutil.parser import parse

register = template.Library()


@register.filter
def get_mes(cadena):
    try:
        meses = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre',
                 'Noviembre', 'Diciembre']
        numero = int(cadena)
        return meses[numero]
    except Exception as e:
        return '-'


@register.filter
def filter_is_step_configured(tenant, step):
    steps = eval(tenant.configcliente.steps_configured)
    if isinstance(steps, list):
        return step in steps


def clear_string(cadena):
    return removeNonAscii(elimina_tildes(cadena))


@register.filter
def in_group(user, groups):
    group_list = force_text(groups).split(',')
    return bool(user.groups.filter(name__in=group_list).values('name'))


@register.filter
def default_if_blank(string, default):
    return string == '' and _(default) or string


@register.filter
def convert_integer(numero):
    try:
        residuo = float(numero) % 1
        if residuo > 0:
            return numero
        else:
            return int(numero)

    except Exception as e:
        return '--'


@register.filter
def convert_integer2(numero):
    try:
        residuo = float(numero) % 1
        if residuo > 0:
            return str(round(numero, 2)).replace(",", ".")
        else:
            return int(numero)

    except Exception as e:
        return '--'


@register.filter
def convert_float(numero):
    try:
        return str(numero).replace(',', '.')

    except Exception as e:
        return '--'


@register.filter
def sum(numero1, numero2):
    try:
        return numero1 + numero2

    except Exception as e:
        return 0


@register.filter
def resta(numero1, numero2):
    return numero1 - numero2


@register.filter
def resta_decimals(numero1, numero2):
    try:
        resta = numero1 - numero2
    except Exception as e:
        print(e)

    return numero1 - numero2


@register.filter
def multiply(num1, num2):
    if num1:
        return num1 * num2
    else:
        return num2


@register.filter
def devolver_positivo(numero):
    return abs(numero)


@register.filter
def in_module(cliente, modulo_tag):
    module_list = force_text(modulo_tag).split(',')
    try:
        has_permiso = bool(cliente.configcliente.modulos.filter(tag__in=module_list).values('tag'))
    except Exception as e:
        has_permiso = False

    return has_permiso


@register.filter
def has_permission(user, permission):
    access = False
    try:
        permission_dict = permission.split('.')
        perm = Permission.objects.filter(
            codename=permission_dict[1],
            content_type__app_label=permission_dict[0]
        ).last()

        user_permission, groups = None, None
        if perm:
            user_permission = user.user_permissions.filter(pk=perm.id)
            groups = user.groups.filter(permissions=perm)

        access = bool(user_permission or groups)

    except Exception as e:
        print('ERROR HAS_PERMISSION: ', e)
        pass

    return access


@register.filter
def format_moneda(number, float_number=0):
    return format_money(number, float_number)


@register.filter
def format_ceil(number):
    diff = number - int(number)
    if diff == 0:
        valor = int(ceil(number))
    else:
        valor = number
    return valor


@register.filter
def in_mantenedor(cliente, mantenedor):
    mantenedor_dict = force_text(mantenedor).lower().split('@')
    try:
        has_permiso = bool(cliente.configcliente.mantenedores.filter(tag__in=mantenedor_dict).values('tag'))
    except Exception as e:
        has_permiso = False

    return has_permiso


@register.filter
def is_expirado(cliente):
    now = datetime.now()
    today = date(now.year, now.month, now.day)

    try:
        has_permiso = bool(cliente.configcliente.expiracion < today)
    except Exception as e:
        has_permiso = False

    return has_permiso


@register.filter
def get_selected(a, b):
    try:
        a = int(a)
    except Exception as e:
        print(e)

    try:
        b = int(b)
    except Exception as e:
        print(e)

    if a == b:
        return "selected"
    else:
        return ""


@register.filter
def verbose_name_filter(obj, field_name):
    return obj._meta.get_field(field_name).verbose_name


@register.filter
def base64encode(string):
    return base64.b64encode(string.encode()).decode()


@register.filter
def base64decode(string):
    lens = len(string)
    if lens % 4:
        return string
    else:
        return base64.b64decode(string).decode()


@register.filter
def concat(value_1, value_2):
    return str(value_1) + str(value_2)


@register.filter
def get_porcentaje(value, total):
    try:
        return round(float(value * 100) / total, 2)

    except Exception as e:
        return 0


@register.filter
def get_valor_by_porcentaje(porcentaje, total):
    try:
        return round((total * porcentaje) / 100)
    except Exception as e:
        return 0


@register.filter
def length(grilla):
    try:
        return len(grilla)
    except Exception as e:
        return 0


@register.filter
def hide_nonetype(value):
    if isinstance(value, None.__class__):
        return ''
    else:
        return value


@register.filter
def check_type(value):
    try:
        numero = int(value)
        return numero
    except:

        try:
            fecha = parse(value)
            return fecha.strftime('%Y-%m-%d %H:%M:%S')
        except:
            if '/media/' in value:
                return '<a href="%s"><i class="fa fa-download" aria-hidden="true"></i></a>' % value
            return value


@register.filter
def mi_strip(string):
    """
    funcion que reemplaza los espacios entre palabras por un guin bajo
    :param string (string): palabra o frase con un espacio entre palabras
    :return (string): string sin espacios al inicio y final con un guion bajo entre palabras
    """
    return string.lower().strip().replace(' ', '_')


@register.filter('has_group')
def has_group(user, group_name):
    groups = user.groups.all().values_list('name', flat=True)

    return True if group_name in groups else False


@register.filter
def get_iniciales(string):
    import re
    i = re.findall('([A-Z])[A-Za-z]* *', string)
    iniciales = "".join(i)
    return iniciales


@register.filter(name='range')
def filter_range(start, end):
    return range(start, end)


@register.filter
def format_date_slash(date):
    return date.strftime('%d/%m/%Y')


@register.filter
def replace_whitespace_by_underscore(value):
    return normalize_str(value).decode('utf-8').lower().replace(' ', '_').replace('%', '')


@register.simple_tag
def replace_str(str, old, new):
    return str.replace(old, new)


@register.filter
def inlist(value, custom_list):
    custom_list = list(map(int, custom_list.split(',')))
    return value in custom_list


@register.filter
def language_user(request):
    language = language_client()
    if language in ['es', 'mx', 'gt']:
        result = 'es'
    else:
        result = 'en'

    return result


@register.filter
def add_days_to_date(date, days):
    return date + timedelta(days=days)


@register.filter
def get_url_file(name):
    name_file = name.split('media')[1]
    return f'{settings.MEDIA_URL_SELF}{name_file}'


@register.filter
def get_file_name(item):
    return os.path.basename(item.file.name)


@register.filter
def translate_text(text):
    return str(_(text))


