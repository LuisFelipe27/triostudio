# -*- encoding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from secretary import Renderer
from PyPDF2 import PdfFileMerger
from icalendar import Calendar, Event, vCalAddress, vText
from config.settings import MEDIA_ROOT
from helpers.classes.console_print import ConsolePrint
from helpers.functions.utils import (
    elimina_tildes, format_date_strftime, format_time_strftime, convert_integer,
    removeNonAscii, format_moneda, format_date_calendar,
    str_upper, str_lower, get_full_path, format_time_duration,
    tenant_current)
import logging
import os
import subprocess
import shutil
import uuid
import sys
import io
import pytz
import xlsxwriter


def convert_doc_to_pdf(path_home, outdir, path_file):
    try:
        # FOR CONVERT TO PDF IN WINDOWS
        # EXAMPLE URL '"C:/Program Files/LibreOffice/program/swriter.exe"'
        from config.config import LIBREOFFICE_WINDOWS_URL
        command = "{} --headless --convert-to pdf --outdir {} {}".format(
                LIBREOFFICE_WINDOWS_URL, outdir, path_file
            )
    except Exception as e:
        command = "export HOME='{}' && libreoffice --convert-to pdf --outdir '{}' '{}'".format(
            path_home, outdir, path_file
        )

    p = subprocess.Popen(command, stdout=subprocess.PIPE,
                         shell=True, stderr=subprocess.STDOUT)
    out, err = p.communicate()

    filename = path_file.split('/')[-1]

    return {
        'filename': filename[0:len(filename)-3]+'pdf',
        'path_file': path_file[0:len(path_file)-3]+'pdf'
    }


def export_documento(request, template, context, name='documento', format_=1,
                     return_path_file=False, return_non_full_path_file=False):
    """Export document to PDF / Word

    Keyword arguments:
    request -- the django request
    template -- the template format .odt
    context -- the context for use in template
    name -- the file name returned
    format_ -- the output format of the document
    return_path_file -- indicates if is required return the full path
                        of the file (optional)
    return_non_full_path_file -- indicates if is required return the file path
                                 from '/media/' onwards (optional)

    """

    now = datetime.now()

    # Se controla parametro request, ya que funcion se esta utilizando tambien
    # desde un management command y desde ahi no es posible utilizar request

    tenant = tenant_current()
    tenant_info = dict()
    tenant_info['tenant'] = tenant
    tenant_info['domain_url'] = tenant.domain_url
    try:
        tenant_info['request'] = request
        tenant_info['path'] = request.path
    except Exception:
        pass

    try:
        name_document = str(removeNonAscii(
            elimina_tildes(name))).replace(' ', '_').replace('/', '-')

        # Render docs template with library 'Secretary'
        engine = Renderer()

        # Add custom filters to render document
        # django filters doesn't work with {%load filters%}, is necessary add manually
        engine.environment.filters['date'] = format_date_strftime
        engine.environment.filters['time'] = format_time_strftime
        engine.environment.filters['time_duration'] = format_time_duration
        engine.environment.filters['lower'] = str_lower
        engine.environment.filters['upper'] = str_upper
        engine.environment.filters['format_date_calendar'] = format_date_calendar
        engine.environment.filters['format_moneda'] = format_moneda
        engine.environment.filters['convert_integer'] = convert_integer
        engine.environment.filters['url_archivo'] = get_full_path

        ruta_archivos = MEDIA_ROOT + '/' + tenant_info['domain_url']
        firma_blank = 'static/images/firma_blank.png'
        firma_ficha = None

        if 'imprimir_firma' in context:
            # Cuando se imprime con firma se recive la variable imprimir_firma en el context

            try:
                firma_solicita = None
                firma_autoriza = None
                solicita = context['oc'].seguimiento_set.filter(estado_id=1
                    ).order_by('created')

                firma_solicita_file = None

                if solicita:
                    firma_solicita_file = str(solicita[0].usuario.perfil.firma)
                    firma_solicita = MEDIA_ROOT + '/' + tenant_info['domain_url'] + '/' + firma_solicita_file

                context['firma_solicita'] = firma_blank

                try:
                    if os.path.exists(firma_solicita) and firma_solicita_file:
                        context['firma_solicita'] = firma_solicita
                except Exception as e:
                    pass

                autoriza = context['oc'].seguimiento_set.filter(estado_id=6
                    ).order_by('created')

                firma_autoriza_file = None

                if autoriza:
                    firma_autoriza_file = str(autoriza[0].usuario.perfil.firma)
                    firma_autoriza = MEDIA_ROOT + '/' + tenant_info['domain_url'
                        ] + '/' + firma_autoriza_file

                context['firma_autoriza'] = firma_blank
                try:
                    if os.path.exists(firma_autoriza) and firma_autoriza_file:
                        context['firma_autoriza'] = firma_autoriza
                except Exception as e:
                    pass

            except Exception as e:
                pass

        if 'firma_ficha' in context:
            tenant = tenant_current()
            domain_url = tenant.domain_url
            path_to_digital_rubric =  str(context['firma_ficha'])

            if domain_url in path_to_digital_rubric:
                # if domain_url exists, we should remove the first position in path (ruta_archivo already has the domain_url)
                path_to_digital_rubric = path_to_digital_rubric.split("/")
                path_to_digital_rubric = f"{path_to_digital_rubric[1]}/{path_to_digital_rubric[2]}"

            firma_ficha = ruta_archivos + '/' + path_to_digital_rubric

        try:
            if os.path.exists(firma_ficha) and context['firma_ficha']:
                context['firma_ficha'] = firma_ficha
            else:
                context['firma_ficha'] = firma_blank

        except Exception as e:
            context['firma_ficha'] = firma_blank

        context['print_date'] = now.strftime('%d/%m/%Y')
        context['print_time'] = now.strftime('%H:%M')

        if MEDIA_ROOT in template:
            document = engine.render(template, **context)
        else:
            document = engine.render(MEDIA_ROOT + '/' + template, **context)

        if 'documento_path' in context:
            path_pdf = ruta_archivos + '/' + context['documento_path']
        else:
            path_pdf = ruta_archivos

        uuid_doc = uuid.uuid4()
        nombre_doc = name_document + str(uuid_doc)

        # Prepares and saves the document in .doc for be convert in pdf.
        #
        # The .doc is used for return the full path of file if is required.
        filename = '%s.doc' % nombre_doc
        path_file = '%s/%s' % (ruta_archivos, filename)
        doc = open(path_file, 'wb')
        doc.write(document)  # Accept bytes
        doc.close()

        if format_ == 2:  # Format PDF
            path_file_doc = '{}/{}.doc'.format(ruta_archivos, nombre_doc)
            convert = convert_doc_to_pdf(ruta_archivos, path_pdf, path_file_doc)

            filename = convert['filename']
            path_file = convert['path_file']

            url_pdf = '/media/{}/{}'.format(tenant_info['domain_url'], filename)
            response = HttpResponseRedirect(url_pdf)

            # If is required the full path file, not is delete the temp.
            #
            # For delete temporarys must uses function 'remove_file_temp()'.
            if not return_path_file and not return_non_full_path_file:
                try:
                    os.remove(ruta_archivos + "/" + nombre_doc + ".doc")
                except Exception as e:
                    pass

        else:  # Format DOC
            response = HttpResponse(document,
                                    content_type='application/ms-word')
            response['Content-Disposition'] = "inline; filename={}_{}.doc"\
                .format(name_document, now.strftime('%d-%m-%Y'))

        try:
            # Closes document rendered only if is necessary
            document.close()

        except Exception as e:
            pass

        if return_path_file:
            if 'documento_path' in context:
                return context['documento_path'] + "/" + filename

            else:
                return path_file

        elif return_non_full_path_file:
            path_file = '/media/' + tenant_info['domain_url'] + "/" + filename
            return path_file

        else:
            return response

    except Exception as e:
        ConsolePrint().error('Template Docs Error', e)
        if 'path' in tenant_info:
            logger = logging.getLogger('django.request')
            logger.exception('Template Docs Error: %s', tenant_info['domain_url'], extra={
                             'status_code': 500, 'request': tenant_info['request']})
        raise e


def remove_file_temp(path_file):
    """Remove a file """
    os.remove(path_file)


def remove_directory_temp(path_directory):
    """Removes a directory with her files"""
    shutil.rmtree(path_directory, ignore_errors=True)


def copy_file_temp(path_file, new_path_file):
    """Copies a file to another directory"""
    shutil.copyfile(path_file, new_path_file)


def zip_file_temp(source, destination):
    """ Returnes a file comprimed (zip) that include one or plus files

    Keyword arguments:
    source -- the directory that have the files to comprimed
    destination -- the directory where will be the file comprimed

    """

    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))

    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s' % (name, format), destination)


def export_excel(name, sheet_name, data, file_path=None):
    """ Funcionalidad para exportar a excel genérica, recibe
        name: nombre que va a tener el documento excel
        sheet_name: nombre que va a tener la hoja del documento excel
        has_other_sheet: indica si las variables "sheet_name" y "data" son para hojas distintas
        data: datos que se le pasan al método para exportarlos
            formato data:
                data = {
                    'properties':['properties, to, set, in, sheets']
                    'columns': ['Nombres', 'de', 'las', 'columnas']
                    'rows': [['datos', 'que', 'se'], ['quieren', 'exportar']]
                }
    """
    output = io.BytesIO()
    if file_path:
        wb = xlsxwriter.Workbook(file_path)
    else:
        wb = xlsxwriter.Workbook(output)

    ws = wb.add_worksheet(sheet_name)

    font_style = wb.add_format({'size': 9})
    font_style_bold = wb.add_format({'bold': True, 'size': 9})
    font_currency = wb.add_format({'num_format': '$#,##0'})
    font_number = wb.add_format({'num_format': '#,##0'})
    font_code = wb.add_format({'num_format': '@'})
    font_date = wb.add_format({'num_format': 'dd/mm/yy', 'size': 9})
    font_time = wb.add_format({'num_format': 'hh:mm', 'size': 9})
    text_wrap = wb.add_format({'text_wrap': True})

    row_num = 0
    col_num = 0

    if 'properties' in data and data['properties']:
        for property in data['properties']:
            if property['function'] == 'set_column':
                ws.set_column(property['column_range'], property['width'])

    for name_columns in data['columns']:
        ws.write(row_num, col_num, name_columns, font_style_bold)
        col_num += 1

    row_num += 1

    for rows in data['rows']:
        for col_num, row in enumerate(rows):
            if isinstance(row, dict):
                if row['format'] == int:
                    ws.write(row_num, col_num, row['value'], font_number)
                elif row['format'] == 'code' and row['value']:
                    ws.write(row_num, col_num, row['value'], font_code)

                elif row['format'] == 'currency':
                    ws.write(row_num, col_num, row['value'], font_currency)

                elif row['format'] == 'wrap' and row['value']:
                    ws.write(row_num, col_num, row['value'], text_wrap)

                elif row['format'] == 'date' and row['value']:
                    _value = row['value']
                    if len(_value.split(' ')) > 1:
                        _value = _value.split(' ')[0]
                    date_value = datetime.strptime(_value, '%d/%m/%Y')
                    ws.write_datetime(row_num, col_num, date_value, font_date)

                elif row['format'] == 'time' and row['value']:
                    time_value = datetime.strptime(row['value'], "%H:%M").time()
                    ws.write_datetime(row_num, col_num, time_value, font_time)

                else:
                    ws.write(row_num, col_num, row['value'], font_style)
            else:
                ws.write(row_num, col_num, str(row), font_style)
        row_num += 1
    wb.close()
    output.seek(0)

    if file_path:
        return file_path
    else:
        response = HttpResponse(output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s.xlsx' % name
        return response

def merge_files_in_pdf(files, filename='documento', return_path_file=False):
    merger = PdfFileMerger()
    tenant = tenant_current()

    name_document = str(removeNonAscii(
        elimina_tildes(filename))).replace(' ', '_')

    uuid_doc = uuid.uuid4()
    name_doc = name_document + str(uuid_doc)
    file = MEDIA_ROOT + '/' + tenant.domain_url + '/' + '%s.pdf' % name_doc

    for pdf in files:
        merger.append(pdf)

    merger.write(file)
    merger.close()

    if return_path_file:
        return file
    else:
        url_pdf = '/media/{}/{}.pdf'.format(tenant.domain_url, name_doc)
        response = HttpResponseRedirect(url_pdf)
        return response


def generate_ics_file(data, domain_url):
    uuid_doc = uuid.uuid4()
    name_doc = str(_('detalle_cita')) + '_' + str(uuid_doc)
    file = MEDIA_ROOT + '/' + domain_url + '/' + f"{name_doc}.ics"

    calendar = Calendar()
    event = Event()
    calendar.add('attendee', f"MAILTO:{data['patient']['email']}")

    event.add('summary', data['summary'])

    event.add('dtstart', data['date_start'])
    event.add('dtend', data['date_end'])

    organizer = vCalAddress(f"MAILTO:{data['patient']['email']}")
    organizer.params['cn'] = vText(f"{data['patient']['fullname']}")
    event['organizer'] = organizer
    event['location'] = vText(f"{data['branch']['address']}")

    calendar.add_component(event)

    ics_file = open(file, 'wb')
    ics_file.write(calendar.to_ical())
    ics_file.close()

    return file


def make_template_relative_path(template):
    """Make relative path of template """
    template = str(template)
    try:
        tenant = tenant_current()
        domain_url = tenant.domain_url
        if not domain_url in template:
            return '{}/{}'.format(domain_url, template)
    except Exception:
        pass
    return template
