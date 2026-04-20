from imgurpython import ImgurClient
from helpers.functions.utils import get_parametro


class ImgUr:
    
    def __init__(self, client_id, client_secret, access_token, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token

    def imgur_client(self):
        client = ImgurClient(self.client_id, self.client_secret, self.access_token, self.refresh_token)
        return client


