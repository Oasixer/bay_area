from oauth_secret import oauth_token
import pycurl
import urllib
import StringIO

def send_dm(user_id, message):
    c = pycurl.Curl()
    url = 'https://waterloorocketry.slack.com/api/chat.postMessage?token=' + oauth_token + '&channel=' + user_id + '&text=' + urllib.quote_plus(message)
    url = url.decode('utf-8').encode('ascii')
    c.setopt(c.URL, url)
    buffer = StringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    c.close()
