"""
公共接口
"""

import requests


class QuoinePublic:
    def __init__(self, baseurl):
        self.baseurl = baseurl

    def request(self, method, url, params=None, headers=None):
        try:
            if method == 'GET':
                resp = requests.get(url, params=params, headers=headers) if params is not None \
                    else resp = requests.get(url, headers=headers)
            elif method == 'POST':
                resp = requests.post(url, data=params, headers=headers)
            else:
                return False, 'check method, it is not exist'

            if resp.status_code == 200:
                return True, resp.json()
            else:
                error = {
                    'status_code': resp.status_code,
                    'method': method,
                    'url': url,
                    'params': params,
                    'resp': resp.text
                }
                return False, error
        except requests.exceptions.RequestException as e:
            print('----- Requests Exception -----')
            error = {
                'method': method,
                'url': url,
                'error_info': e
            }
            return False, error
        
    def output(self, function_name, content):
        return {
            'function_name': function_name,
            'content': content
        }