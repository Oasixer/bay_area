import time
import decimal
import re

from wrt_respond import *
from wrt_dynamodb_handler import *

def handle_todo_command(user, text, team_domain):
    if text == "":
        return get_all_todo_items_pretty(user)
    elif text == "clear":
        return clear_todo_items(user)
    elif text.startswith("remove") and len(text.split(' ')) == 2 and text.split(' ')[1].isdigit():
        return delete_todo_by_index(user, int(text.split(' ')[1]) - 1)
    else:
        m = re.search(r"^\[([^\]]*)\](.*)$", text);
        if m and len(m.group(1).strip()) > 0 and len(m.group(2).strip()) > 0:
            return add_todo_item(user, m.group(2).strip(), m.group(1).strip());
        return add_todo_item(user, text)

def get_all_todo_items_pretty(user):
    response = get_all_todo_items(user)

    items = {}
    for i in response:
        items[str(float(i['time_added']))] = (i['todo_item'].strip('"'), i['tag'] if 'tag' in i else 'personal')
    
    sorted_items = {}
    for i in sorted(items.iterkeys()):
        if items[i][0].startswith('[deleted]'):
            continue
        if items[i][1] in sorted_items:
            sorted_items[items[i][1]].append(items[i][0])
        else:
            sorted_items[items[i][1]] = [items[i][0]]
    if len(sorted_items) == 0:
        return respond(None, "You currently have no issues assigned to you. Enjoy your day!")
    return_string = "Here are your todo items:"
    counter = 1
    if 'personal' in sorted_items:
        for i in sorted_items['personal']:
            return_string += "\n%i. %s" % (counter, i)
            counter += 1
        sorted_items.pop('personal')
    if sorted_items == {}:
        return respond(None, return_string)

    for i in sorted(sorted_items.iterkeys()):
        return_string += "\n\n[%s]:" % i
        for j in sorted_items[i]:
            return_string += "\n%i. %s" % (counter, j)
            counter += 1
    
    return respond(None, return_string)

def get_all_todo_items(user):
    return get_items_from_table('WRT_todo', lambda x: ('tag' in x and (x['tag'] != 'personal' or x['User_ID'] == user)) or ('tag' not in x and x['User_ID'] == user), 'todo_item')

def clear_todo_items(user):
    items = get_all_todo_items(user)
    items_to_delete = {}
    for i in items:
        if 'tag' in i and i['tag'] != 'personal':
            continue
        items_to_delete[i['time_added']] = i['todo_item']
    if len(items_to_delete) > 0:
        deleted = delete_items_by_key(items_to_delete, "WRT_todo", "time_added", "todo_item")
        return respond(None, "deleted %s items" % deleted)
    return respond(None, "no todo items to delete")

def delete_todo_by_index(user, index):
    response = get_all_todo_items(user)

    items = {}
    for i in response:
        items[str(float(i['time_added']))] = (i['todo_item'], i['tag'] if 'tag' in i else 'personal', i['time_added'])

    sorted_response = []
    for i in sorted(items.iterkeys()):
        if items[i][0].strip().startswith('[deleted]'):
            continue
        sorted_response.append({'todo_item':items[i][0],'tag':items[i][1], 'time_added':items[i][2]})

    items_map = {}
    for i in sorted_response:
        if not 'tag' in i:
            i['tag'] = 'personal'
        if i['tag'] in items_map:
            items_map[i['tag']].append( ( i['time_added'] , i['todo_item'] ) )
        else:
            items_map[i['tag']] = [ ( i['time_added'], i['todo_item']) ]
        
    if index < 0:
        return respond(None, "positive indices only")

    #first check personal
    if 'personal' in items_map:
        if index < len(items_map['personal']):
            to_delete = items_map['personal'][index]
            deleted = delete_items_by_key({to_delete[0]: to_delete[1]}, 'WRT_todo', 'time_added', 'todo_item')
            return respond(None, "deleted item: %s" % to_delete[1])
        index -= len(items_map['personal'])
        items_map.pop('personal')

    #then check alphabetically
    for i in sorted(items_map.iterkeys()):
        if index < len(items_map[i]):
            to_delete = items_map[i][index]
            deleted = delete_items_by_key({to_delete[0]: to_delete[1]}, 'WRT_todo', 'time_added', 'todo_item')
            return respond(None, "deleted item: %s" % to_delete[1])
        index -= len(items_map[i])
        items_map.pop(i)

    return respond(None, "index out of range")

def add_todo_item(user, text, tag = None):
    item = text
    time_added = decimal.Decimal(time.time())
    Item = { 
        'time_added': time_added,
        'todo_item' : item,
        'User_ID'   : user,
        'tag'       : tag if tag else 'personal'
    }
    put_item_in_table(Item, "WRT_todo")
    
    if tag:
        return respond(None, "added: " + item + " to [" + tag + "]")
    else:
        return respond(None, "added: " + item)
