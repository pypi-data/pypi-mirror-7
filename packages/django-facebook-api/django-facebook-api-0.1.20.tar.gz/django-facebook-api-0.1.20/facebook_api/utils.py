from django.conf import settings
from oauth_tokens.models import AccessToken
from facegraph import Graph, GraphException
from datetime import datetime
import time
import logging

__all__ = ['graph']

log = logging.getLogger('facebook_api')

ACCESS_TOKEN = getattr(settings, 'FACEBOOK_API_ACCESS_TOKEN', None)

def get_tokens():
    '''
    Get all vkontakte tokens list
    '''
    return AccessToken.objects.filter(provider='facebook').order_by('-granted')

def update_token():
    '''
    Update token from provider and return it
    '''
    return AccessToken.objects.fetch('facebook')

def get_api():
    '''
    Return API instance with latest token from database
    '''
    if ACCESS_TOKEN:
        token = ACCESS_TOKEN
    else:
        tokens = get_tokens()
        if not tokens:
            update_token()
            tokens = get_tokens()
        token = tokens[0].access_token
    return Graph(token)

def graph(method, **kwargs):
    '''
    Call API using access_token
    '''
    api = get_api()
    try:
        response = api[method](**kwargs)
    except GraphException, e:
        if e.code == 190:
            update_token()
            return graph(method, **kwargs)
        elif 'An unexpected error has occurred. Please retry your request later' in str(e):
            time.sleep(1)
            return graph(method, **kwargs)
        else:
            raise e
    except ValueError, e:
        log.warning("ValueError: %s registered while executing method %s with params %s" % (e, method, kwargs))
        # sometimes returns this dictionary, sometimes empty response, covered by test "test_empty_result"
        data = {"error_code":1,"error_msg":"An unknown error occurred"}
        return None
    except Exception, e:
        log.error("Unhandled error: %s registered while executing method %s with params %s" % (e, method, kwargs))
        raise e

    if getattr(response, 'error_code', None):
        log.error("Error %s: %s returned while executing method %s with params %s" % (response.error_code, response.error_msg, method, kwargs))
        time.sleep(1)
        return graph(method, **kwargs)

    return response