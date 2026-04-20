from helpers.constants import RECAPTCHA_V3


def recaptcha_site_key(request):
    return {'RECAPTCHA_SITE_KEY': RECAPTCHA_V3['RECAPTCHA_SITE_KEY']}