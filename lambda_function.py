from urlparse import parse_qs

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
        command = params['command'][0]
        team_domain = params['team_domain'][0]
        text = ""
        if "text" in params:
            text = params['text'][0]
    except:
        return None
        #return post_the_agenda()
    
    if command == '/bay':
        return handle_bay_command(user, text, team_domain)
    elif command == '/agenda':
        return handle_agenda_command(user, text, team_domain)
    elif command == '/todo':
        return handle_todo_command(user, text, team_domain)
    elif command == 'postit':
        return post_the_agenda()
    else:
        return respond(None, "unknown command")
