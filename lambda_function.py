from urlparse import parse_qs
import logging
import json
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#our files
from oauth_secret import oauth_token
from wrt_lists import *
from wrt_bay_command import handle_bay_command
from wrt_agenda_command import handle_agenda_command, post_the_agenda, clear_all_items
from wrt_todo_command import handle_todo_command
from wrt_respond import *

def lambda_handler(event, context):
    try:
        if type(event) == str:
            params = parse_qs(json.loads(event)['body'])
        else:
            params = parse_qs(event['body'])
    except:
        logger.error('couldn\'t parse event{}'.format(event))
        logger.error('error when parsing event["body"]')
        return respond(None, "couldn't parse input")
    try:
        user = params['user_id'][0]
    except:
        logger.error('couldn\'t parse event{}'.format(event))
        logger.error('error when parsing user_id')
        return respond(None, "couldn't parse input")
    try:
        user_name = params['user_name'][0]
    except:
        logger.error('couldn\'t parse event{}'.format(event))
        logger.error('error when parsing user_name')
        return respond(None, "couldn't parse input")
    try:
        command = params['command'][0]
    except:
        logger.error('couldn\'t parse event{}'.format(event))
        logger.error('error when parsing command')
        return respond(None, "couldn't parse input")
    try:
        team_domain = params['team_domain'][0]
    except:
        logger.error('couldn\'t parse event{}'.format(event))
        logger.error('error when parsing team_domain')
        return respond(None, "couldn't parse input")
    try:
        text = ""
        if "text" in params:
            text = params['text'][0]
        logger.info('%s (id %s) sent command %s to domain %s with text %s' % (user_name, user, command, team_domain, text))
    except:
        logger.error('couldn\'t parse event{}'.format(event))
        logger.error('error when parsing text')
        return respond(None, "couldn't parse input")
    
    if command == '/bay':
        return handle_bay_command(user, text, team_domain)
    elif command == '/agenda':
        return handle_agenda_command(user, user_name, text, team_domain)
    elif command == '/todo':
        return handle_todo_command(user, text, team_domain)
    elif command == 'postit':
        return post_the_agenda()
    elif command == 'cron_clearit':
        return clear_all_items()
    else:
        return respond(None, "unknown command")
