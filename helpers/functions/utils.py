# -*- encoding: utf-8 -*-
from datetime import datetime

from django.core.files.base import ContentFile
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.validators import validate_email
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.utils.encoding import force_text
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from itertools import cycle

from helpers.classes.console_print import ConsolePrint
from helpers.middleware.request_current import get_current_request
from config.settings import MEDIA_ROOT
from config.config import DEFAULT_LANGUAGE_CODE, ENVIRONMENT
from django.apps import apps
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.db.models.base import ModelBase
import unicodedata
import os
import uuid
import math
import base64
import threading

from helpers.functions.validators import check_in_memory_mime
from helpers.constants import CLIENTS_LANGUAGE_CHOICES

DAYS = ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá']


def is_array(data):
    return isinstance(data, (list, tuple, dict))


def set_filters(request, tipo, filtros={}):
    if is_array(filtros) and len(filtros):
        request.session[tipo] = filtros
    else:
        request.session[tipo] = {}

    return request.session[tipo]


def get_filters(request, tipo, key=None):
    if key is None:
        try:
            if not request.session[tipo]:
                return False
            else:
                return request.session[tipo]
        except Exception as e:
            return False
    else:
        return request.session[tipo][key]


def set_step_configured(tenant, step):
    steps = eval(tenant.configcliente.steps_configured)
    if not isinstance(steps, list):
        steps = []

    if not step in steps:
        steps.append(step)
        tenant.configcliente.steps_configured = str(steps)
        tenant.configcliente.save()

    return steps


def is_step_configured(tenant, step):
    steps = eval(tenant.configcliente.steps_configured)
    if isinstance(steps, list):
        return step in steps

    else:
        return False


def is_tenant_configured(tenant):
    steps = eval(tenant.configcliente.steps_configured)
    if isinstance(steps, list):
        return len(steps) == 8

    else:
        return False


def get_intervalos(intervalo=60, desde_cero=True, tope_minutos=60):
    intervalos = []
    iteraciones = tope_minutos / intervalo
    for i in range(0, iteraciones):
        if desde_cero:
            minuto = intervalo * i
        else:
            minuto = intervalo * (i + 1)

        if minuto == 0:
            minuto = '00'
        elif minuto < 10:
            minuto = '0%s' % minuto

        intervalos.append(minuto)

    return intervalos


def elimina_tildes(s):
    try:
        return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
    except Exception as e:
        return s


def removeNonAscii(s):
    try:
        return ''.join(i for i in s if ord(i) < 128)
    except Exception as e:
        return s


def normalize_str(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')


def valid_run(run, es_admin=True):
    run = run.replace('.', '')
    run = run.replace('-', '')
    rut = run[:-1]
    dv = run[-1:]
    if dv == 'k' or dv == 'K':
        dv = 10

    reversed_digits = map(int, reversed(str(rut)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    result = (-s) % 11

    if str(result) != str(dv):
        if es_admin:
            raise ValidationError("El RUN es incorrecto.")
        else:
            return False
    else:
        return True


def format_run(run):
    run = run.replace('.', '')
    run = run.replace('-', '')
    for i, c in enumerate(reversed(run)):
        if i == 0:
            run = '-%s' % c
        elif i in (3, 6, 9):
            run = '.%s%s' % (c, run)
        else:
            run = '%s%s' % (c, run)

    return run


def mcd(nums):
    """ Funcion para hallar el Maximo Comun Divisor """
    a = max(nums)
    b = min(nums)
    while b != 0:
        mcd = b
        b = a % b
        a = mcd
    return mcd


def mcm(nums):
    """ Funcion para hallar el Minimo Comun Multiplo """
    a = max(nums)
    b = min(nums)
    mcm = (a / mcd(a, b)) * b
    return mcm


def format_moneda(number, float_number=0):
    try:
        if int(float_number) == 0:
            number = int(number)
            value = '{:0,.0f}'.format(number).replace(',', '.')
        else:
            number = float(number)
            value = eval('\'{:0,.' + str(float_number) + 'f}\'').format(number) \
                .replace('.', '-') \
                .replace(',', '.') \
                .replace('-', ',')
    except Exception as e:
        value = 0

    return value


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_tipos_de_documentos():
    from transversal.models import TemplateDocumentoFijo, TemplateDocumentoDinamico
    OPTION_TIPO_DOCUMENTO = TemplateDocumentoFijo.OPTION_TIPO_DOCUMENTO + TemplateDocumentoDinamico.OPTION_TIPO_DOCUMENTO
    return OPTION_TIPO_DOCUMENTO


def translate_date(string):
    aux = string
    weekday = (('Monday', 'lunes'), ('Tuesday', 'martes'), ('Wednesday', 'miercoles'), ('Thursday', 'jueves'),
               ('Friday', 'viernes'), ('Saturday', 'sabado'), ('Sunday', 'domingo'))
    for wd in weekday:
        aux = aux.replace(wd[0], wd[1])

    month = (('January', 'enero'), ('February', 'febrero'), ('March', 'marzo'), ('April', 'abril'), ('may', 'mayo'),
             ('June', 'junio'), ('July', 'julio'), ('August', 'agosto'), ('September', 'septiembre'),
             ('October', 'octubre'), ('November', 'noviembre'), ('December', 'diciembre'))
    for m in month:
        aux = aux.replace(m[0], m[1])

    return aux


def generate_hash(str_app=None, str_model=None, str_field=None):
    hash_id = str(uuid.uuid4())
    if not str_app or not str_model or str_field:
        return hash_id

    else:
        model = apps.get_model(str_app, str_model)
        if bool(model.objects.filter(**{str_field: hash_id})):
            generate_hash(str_app, str_model, str_field)
        else:
            return hash_id


def add_months(origin_date, months):
    import datetime, calendar

    month = origin_date.month - 1 + months
    year = origin_date.year + month // 12
    month = month % 12 + 1
    day = min(origin_date.day, calendar.monthrange(year, month)[1])

    return datetime.date(year, month, day)


def get_first_day_month(origin_date):
    from datetime import date

    return date(origin_date.year, origin_date.month, 1)


def get_last_day_month(origin_date):
    from datetime import timedelta

    date_in_first_day = get_first_day_month(origin_date)
    next_month = add_months(date_in_first_day, 1)

    return next_month - timedelta(days=1)


def get_deferred_fields(model, include=[]):
    import django

    fields = []
    for field in model._meta.get_fields():
        if not isinstance(field, django.db.models.fields.reverse_related.ManyToManyRel) and not isinstance(field,
                                                                                                           django.db.models.fields.reverse_related.ManyToOneRel):
            f = str(field).split('.')[2]
            fields.append(f)

    fields += include
    return tuple(fields)


def format_date(fecha):
    from datetime import datetime, date

    if isinstance(fecha, datetime) or isinstance(fecha, date):
        return fecha
    else:
        result = None
        fecha_dict = fecha.split('-')
        if len(fecha_dict) == 1:
            fecha_dict = fecha_dict[0].split('/')

        if len(fecha_dict) == 3:
            anio, mes, dia = '', '', ''
            if int(fecha_dict[0]) >= 1900:
                anio = fecha_dict[0]
                mes = fecha_dict[1]
                dia = fecha_dict[2]

            else:
                anio = fecha_dict[2]
                mes = fecha_dict[1]
                dia = fecha_dict[0]

            if int(fecha_dict[1]) > 12:
                if int(fecha_dict[0]) >= 1900:
                    anio = fecha_dict[0]
                    mes = fecha_dict[2]
                    dia = fecha_dict[1]

                else:
                    anio = fecha_dict[2]
                    mes = fecha_dict[0]
                    dia = fecha_dict[1]

            if int(anio) >= 1900:
                result = '%s-%s-%s' % (anio, mes, dia)

            else:
                result = None

        return result


def get_user_models(formato='tuple'):
    user_apps = get_user_apps(formato='array')
    models = ContentType.objects.filter(app_label__in=user_apps).order_by('app_label')
    if formato == 'tuple':
        options = ()
        for model in models:
            try:
                model_option = (model.model_class().__name__, model.name,)
                options = options + (model_option,)
            except Exception as e:
                pass
        return options
    if formato == 'array':
        options = []
        for model in models:
            options.append(model.model_class().__name__)
        return options


def find_model_on_module(module, doc, debug=False, model=ContentType):
    """
	Esta funcionalidad sirve para filtrar los Model existentes (normalmentes desde contenttype de django) en un determinado documento, con definiciones de ModelViewsets.
	Retornara solo los ContentType registrados en el documento determinado.
	Ej:
		find_model_on_module(module='coleccion', document="api")
	"""
    if not isinstance(model, (ModelBase)):
        raise TypeError('Object %s is not a Model.' % model)
    include = 'from ' + module + ' import ' + doc + ' as document'
    filterarray = []
    try:
        exec(include)
    except ImportError as e:
        if debug:
            message = e.message + '\nExceuted statemment: ' + include
            e.message = e.__class__.__name__ + ": " + message
            raise ImportError(message)
        return [0]
    except Exception as e:
        raise e
    for cls in document.__dict__:
        model_viewset = getattr(document, cls)
        try:
            if hasattr(model_viewset, 'queryset'):
                if isinstance(model_viewset.queryset, (models.query.QuerySet)):
                    contenttype_id = model.objects.get(app_label=model_viewset.queryset.model._meta.app_label,
                                                       model=model_viewset.queryset.model._meta.model_name).id
                    filterarray.append(contenttype_id)
        except Exception as e:
            pass
    return model.objects.filter(id__in=filterarray)


def user_has_permission(user, tag_permission, raise_exception=False):
    if not user.has_perm(tag_permission):
        if raise_exception:
            raise PermissionDenied
        else:
            return False
    else:
        return True


def get_parametro(key):
    parameter_model = apps.get_model('transversal', 'Parameter')
    try:
        return parameter_model.objects.get(key=key).value
    except Exception as e:
        return ''

def get_parameter(key):

    return get_parametro(key)


def convert_integer(numero):
    try:
        residuo = float(numero) % 1
        if residuo > 0:
            return numero
        else:
            return int(numero)

    except Exception as e:
        return '--'


def capitalize_first_letter(value):
    return value[0].upper() + value[1:]


def str_upper(value):
    return value.upper()


def str_lower(value):
    return value.lower()


def format_date_strftime(value):
    try:
        if value:
            return value.strftime('%d/%m/%Y')
        else:
            return "--"
    except:
        date = value.split('-')
        return f'{date[2]}-{date[1]}-{date[0]}'


def format_time_strftime(value):
    if value and not isinstance(value, str):
        return value.strftime('%H:%M')
    else:
        return "--"


def format_time_duration(value):
    if value:
        hours = value.strftime('%H')
        minutes = value.strftime('%M')
        duration_text = ''
        if hours != '0' and hours != '00':
            duration_text = f'{hours} hrs. '
        if minutes != '0' and minutes != '00':
            duration_text += f'{minutes} min.'
        return duration_text
    else:
        return "--"


def format_date_calendar(value):
    request = get_current_request()
    if request.user.perfil and request.user.perfil.language in ['es', 'mx', 'gt', 'oncovida', 'qa_oncovida']:
        return "{}. {}".format(DAYS[int(value.strftime('%w'))], value.strftime('%d/%m'))
    else:
        return "{}. {}".format(value.strftime('%a'), value.strftime('%d/%m'))


def tenant_current(is_principal=True, is_massiveload=False):
    from django.apps import apps
    from django.db import connection

    client_model = apps.get_model('multi_tenant', 'Tenant')

    if is_massiveload:
        clients = client_model.objects.filter(schema_name=connection.schema_name)
        if clients.count() == 1:
            return clients.first()
        else:
            return clients.filter(is_principal=False).first()
    else:
        return client_model.objects.get(
            schema_name=connection.schema_name,
            is_principal=is_principal
        )


def tenant_custom_language():
    request = get_current_request()
    result = {'language': '', 'client': ''}
    # Se extrae nombre de cliente mediante la url
    aux = request.tenant.domain_url.find(".ordenadito")
    client = request.tenant.domain_url[0:aux]
    client = client.replace('-', '_')
    # Se busca si cliente tiene una configuracion de lenguaje propia
    for item in CLIENTS_LANGUAGE_CHOICES:
        if item[0] == client:
            result['language'] = client
            result['client'] = item[1]

    return result


def unique_list(param_list):
    # insert the list to the set
    list_set = set(param_list)
    # convert the set to the list
    return list(list_set)


def client_has_module(module_tag):
    request = get_current_request()
    module_list = force_text(module_tag).split(',')

    return bool(request.tenant.configcliente.modulos.filter(tag__in=module_list).values('tag'))


def paginate_data(items, record_per_page, page):
    paginator = Paginator(items, record_per_page)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        items = paginator.page(paginator.num_pages)

    return items


def language_client():
    request = get_current_request()
    try:
        language = request.user.perfil.language
    except Exception as e:
        result = tenant_custom_language()
        if result['language']:
            language = result['language']
        else:
            language = DEFAULT_LANGUAGE_CODE

    return language


def round_well(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)


def get_full_path(file_url):
    from config.settings import MEDIA_ROOT

    if MEDIA_ROOT in file_url:
        return file_url

    elif '/media' in file_url:
        return '%s%s' % (MEDIA_ROOT.replace('/media', ''), file_url)

    else:
        return '%s%s' % (MEDIA_ROOT, file_url)


def http_response_print(request, message, message_type=None, redirect_url=None):
    from django.contrib import messages
    from django.http import HttpResponseRedirect, JsonResponse

    if message_type is None:
        message_type = messages.ERROR

    if redirect_url:
        messages.add_message(request, message_type, message)
        return HttpResponseRedirect(redirect_url)
    elif 'HTTP_REFERER' in request.META:
        messages.add_message(request, message_type, message)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return JsonResponse({'status': False, 'message': message})


def valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError as e:
        return False


def check_if_in_list_of_dict(array_dicts, value):
    """Check if given value exists in list of dictionaries """
    for elem in array_dicts:
        if value in elem.values():
            return True
    return False


def base64_to_file(data, filename):
    file = base64.b64decode(data)
    extension = check_in_memory_mime(file, read_file=False).split('/')[1]
    return ContentFile(file, name=f'{filename}.{extension}')


def in_dict_list(key, value, my_dictlist):
    for entry in my_dictlist:
        if entry[key] == value:
            return True
    return False


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def valid_date(date, format_to_valid='%Y-%m-%d'):
    try:
        import datetime
        datetime.datetime.strptime(date, format_to_valid)
        return True
    except Exception:
        return False


def send_mails_reports_to_admin_and_managers(errors, report_name, client_name, schema_name):
    from django.db import connection
    connection.schema_name = schema_name

    template = get_template('django/reports/reports_errors_log.txt')
    context = {'errors': errors}
    message = template.render(context)
    if errors and len(errors):
        mail.mail_admins(
            f'Error Informe {report_name}, Cliente: {client_name}',
            message,
        )
        mail.mail_managers(
            f'Error Informe {report_name}, Cliente: {client_name}',
            message,
        )


def send_mails_log_reports(client=None, errors=None, report_name=''):
    try:
        if not client:
            current_client = get_current_request().tenant
            client_name = current_client.nombre
            schema_name = current_client.schema_name
        else:
            client_name = client.nombre
            schema_name = client.schema_name
    except Exception:
        client_name, schema_name = None, None

    if client_name and schema_name:
        thread = threading.Thread(
            target=send_mails_reports_to_admin_and_managers,
            args=(errors, report_name, client_name, schema_name)
        )

        thread.start()


def remove_file_in_server(path_file):
    try:
        os.remove(path_file)
    except Exception as e:
        ConsolePrint().error(title='ERROR REMOVE FILE FROM SERVER', message=e)
        pass


def get_subdomain(domain):
    if ENVIRONMENT['name']:
        subdomain = '%s-%s' % (domain, ENVIRONMENT['name'])
        if ENVIRONMENT['name'] in ['qa', 'rc']:
            subdomain = '%s-%s' % (domain, ENVIRONMENT['rc_name'])
    else:
        subdomain = domain
    return subdomain
