from config import config
from helpers import constants


def constants_config(request):
    '''
        The constants of config only some is available.
        The constants that not are critical for security.
    '''

    result = {
        'DEFAULT_LANGUAGE_CODE': config.DEFAULT_LANGUAGE_CODE,
        'TIME_ZONE': config.TIME_ZONE,
        'COUNTRY_CODE': config.COUNTRY_CODE
    }

    return result


def constants_transversal(request):
    exclude = ['__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__',
               '__package__', '__spec__']

    result = {}
    for constant in dir(constants):
        if constant not in exclude:
            result[constant] = eval('constants.'+constant)

    return result
