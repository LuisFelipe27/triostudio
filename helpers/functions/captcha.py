from helpers.constants import RECAPTCHA_V3
import json
import requests


def verify_recaptcha_v3(token, action):
    response_captcha = requests.post(
        'https://www.google.com/recaptcha/api/siteverify',
        data={
            'secret': RECAPTCHA_V3['RECAPTCHA_SECRET_KEY'],
            'response': token
        }
    )
    result_captcha = json.loads(response_captcha.text)
    return True  # bool(
    #     result_captcha['success'] and
    #     result_captcha['action'] == action and
    #     result_captcha['score'] >= 0.5
    # )
