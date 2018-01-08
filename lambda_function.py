from urlparse import parse_qs
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#our files
from oauth_secret import oauth_token
from wrt_lists import *
from wrt_bay_command import handle_bay_command
from wrt_agenda_command import handle_agenda_command, post_the_agenda
from wrt_todo_command import handle_todo_command
from wrt_respond import *

def lambda_handler(event, context):
    try:
        params = parse_qs(event['body'])
        user = params['user_id'][0]
        user_name = params['user_name'][0]
        command = params['command'][0]
        team_domain = params['team_domain'][0]
        text = ""
        if "text" in params:
            text = params['text'][0]
        logger.info('%s (id %s) sent command %s to domain %s with text %s' % (user_name, user, command, team_domain, text))
    except:
        logger.error('couldn\'t parse event{}'.format(event))
        return respond(None, "couldn't parse input")
    
    if command == '/bay':
        return handle_bay_command(user, text, team_domain)
    elif command == '/agenda':
        return handle_agenda_command(user, user_name, text, team_domain)
    elif command == '/todo':
        return handle_todo_command(user, text, team_domain)
    elif command == 'postit':
        return post_the_agenda()
    else:
        return respond(None, "unknown command")
