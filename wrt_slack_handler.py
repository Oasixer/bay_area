from oauth_secret import oauth_token
import pycurl
import urllib
import StringIO
import json

def post_to_general(message):
    general = 'C07MWEYPR'
    return api_handler('chat.postMessage', text = message, channel = general)

def send_dm(user_id, message):
    return api_handler('chat.postMessage', text = message, channel = user_id)

def get_status(user):
    return api_handler('users.profile.get', user = user)['profile']['status_text']

def set_status(user, text, emoji):
    return api_handler('users.profile.set', user = user, profile = urllib.quote_plus('{"status_emoji":"' + emoji + '","status_text":"' + text + '"}'))

def api_handler(method, text = None, channel = None, user = None, profile = None):
    c = pycurl.Curl()
    url = 'https://waterloorocketry.slack.com/api/' + method + '?token=' + oauth_token
    if channel:
        url += '&channel=' + channel
    if user:
        url += '&user=' + user
    if profile:
        url += '&profile=' + profile
    if text:
        url += '&text=' + urllib.quote_plus(text)
    url = url.decode('utf-8').encode('ascii')
    c.setopt(c.URL, url)
    buffer = StringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    c.close()
    return json.loads(buffer.getvalue())
