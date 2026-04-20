from datetime import datetime

from helpers.classes.console_print import ConsolePrint
from helpers.constants import TEMPLATE_DOCUMENTO_FIJO
from helpers.functions.export_document import export_documento
from helpers.middleware.request_current import get_current_request
from app.transversal.models import TemplateDocumentoFijo


class FileToPrint:
    def liquidation(self, record, full_path):
        try:
            now = datetime.now()
            tdf = TemplateDocumentoFijo.objects.get(
                documento=TEMPLATE_DOCUMENTO_FIJO['LIQUIDATION']
            )
            request = get_current_request()
            context = dict()
            context['print_date'] = now.strftime('%d/%m/%Y')
            context['liquidation'] = record

            return_full_path = False
            return_non_full_path = True
            if full_path:
                return_full_path = True
                return_non_full_path = False

            return export_documento(
                request, str(tdf.template), context, tdf.nombre, tdf.formato,
                return_path_file=return_full_path,
                return_non_full_path_file=return_non_full_path
            )

        except Exception as e:
            ConsolePrint().error('ERROR FILE TO PRINT (LIQUIDATION)', e)
            return None

    def liquidation_item(self, record, full_path):
        try:
            now = datetime.now()
            tdf = TemplateDocumentoFijo.objects.get(
                documento=TEMPLATE_DOCUMENTO_FIJO['LIQUIDATION_ITEM']
            )
            request = get_current_request()
            context = dict()
            context['print_date'] = now.strftime('%d/%m/%Y')
            context['item'] = record

            return_full_path = False
            return_non_full_path = True
            if full_path:
                return_full_path = True
                return_non_full_path = False

            return export_documento(
                request, str(tdf.template), context, tdf.nombre, tdf.formato,
                return_path_file=return_full_path,
                return_non_full_path_file=return_non_full_path
            )

        except Exception as e:
            ConsolePrint().error('ERROR FILE TO PRINT (LIQUIDATION ITEM)', e)
            return None
