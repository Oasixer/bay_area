from wrt_respond import *
from oauth_secret import oauth_token
from wrt_lists import *
import json
import pycurl
import urllib
import StringIO
import random

def handle_bay_command(user, text, team_domain):
    if text == "":
        current_status = get_current_status(user,team_domain)
        if current_status in BAY_LEAVE_STATUS_LIST or current_status == "":
            current_status = random.choice(BAY_STATUS_LIST)
        return respond(None, "%s" % set_current_status(user,team_domain,current_status,':rocket:'))
    elif text == "who":
        list_bay = list_of_people_in_bay(team_domain, True)
        if(len(list_bay) == 0):
            return respond(None, "there's no one in the bay right now")
        elif(len(list_bay) == 1):
            return respond(None, "%s is in the bay" % list_bay[0])
        elif(len(list_bay) == 2):
            return respond(None, "%s and %s are in the bay" % (list_bay[0], list_bay[1]))
        else:
            res_str = ", ".join(list_bay[:-1])
            res_str += ", and " + list_bay[-1] + " are all in the bay"
        return respond(None, res_str)
    elif text == "bay_area_iot":
        list_bay = list_of_people_in_bay(team_domain, False)
        return respond(None, json.dumps(list_bay))
    elif text == "leave":
        status_emoji = random.choice(BAY_LEAVE_EMOJI_LIST);
        status_text = random.choice(BAY_LEAVE_STATUS_LIST)
        return respond(None, "%s" % set_current_status(user,team_domain,status_text,status_emoji))
    else:
        return respond(None, "%s" % set_current_status(user,team_domain,text,':rocket:'))


def get_current_status(user, team_domain):
    c = pycurl.Curl()
    url = 'https://' + team_domain + '.slack.com/api/users.profile.get?token=' + oauth_token + '&user=' + user
    url = url.decode('utf-8').encode('ascii')
    c.setopt(c.URL, url)
    buffer = StringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    c.close()
    return json.loads(buffer.getvalue())['profile']['status_text']
    
def set_current_status(user, team_domain, status_text, status_emoji):
    c = pycurl.Curl()
    url = 'https://' + team_domain + '.slack.com/api/users.profile.set?token=' + oauth_token + '&user=' + user +\
            '&profile=' + urllib.quote_plus('{"status_emoji":"' + status_emoji + '","status_text":"' + status_text + '"}')
    url = url.decode('utf-8').encode('ascii')
    c.setopt(c.URL, url)
    buffer = StringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    c.close()
    json_data = json.loads(buffer.getvalue())
    if user in DEBUG_LIST:
        return json.dumps(json_data)
    if (not "ok" in json_data) or (not json_data["ok"]):
        return "something went wrong, error message: " + json.dumps(json_data["error"])
    return "changed your status to " + status_emoji + " " + status_text

def list_of_people_in_bay(team_domain, human_readable):
    c = pycurl.Curl()
    url = 'https://' + team_domain + '.slack.com/api/users.list?token=' + oauth_token
    url = url.decode('utf-8').encode('ascii')
    c.setopt(c.URL, url)
    buffer = StringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    c.close()
    members = json.loads(buffer.getvalue())['members']
    list_bay = []
    for i in members:
        if (not (i['id'] in ignore_list)) and "profile" in i and "status_emoji" in i['profile'] and i['profile']['status_emoji'] == ':rocket:':
            if(human_readable):
                list_bay.append(i['profile']['real_name'])
            else:
                list_bay.append(i['id'])
    return list_bay
