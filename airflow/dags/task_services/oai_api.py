import requests

class OaiApi:
    def __init__(self):
        """initialize api for datahub.vlaamsekunstcollectie.be"""
        self.API_URL = 'http://datahub.vlaamsekunstcollectie.be'
        self.AUTH_URL = '/oauth/v2/auth'
        self.TOKEN_URL = '/oauth/v2/token'

        print("OaiApi initialized")

    def get_data(self, limit=20, offset=0, sort=None):
        # requests.get ...
        return []
