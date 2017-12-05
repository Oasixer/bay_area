import time
import decimal

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
        return add_todo_item(user, text)

def get_all_todo_items_pretty(user):
    response = get_all_todo_items(user)

    items = {}
    for i in response:
        items[str(float(i['time_added']))] = i['todo_item'].strip('"')
    
    sorted_items = []
    for i in sorted(items.iterkeys()):
        if items[i].startswith('[deleted]'):
            continue
        sorted_items.append(items[i])
    if len(sorted_items) == 0:
        return respond(None, "You currently have no issues assigned to you. Enjoy your day!")
    return_string = "Here are your todo items:"
    for i in range(len(sorted_items)):
        return_string += "\n%i. %s" % (i + 1, sorted_items[i])
    
    return respond(None, return_string)

def get_all_todo_items(user):
    return get_items_from_table('WRT_todo', lambda x: x['User_ID'] == user, 'todo_item')

def clear_todo_items(user):
    items = get_all_todo_items(user)
    items_to_delete = {}
    for i in items:
        items_to_delete[i['time_added']] = i['todo_item']
    if len(items_to_delete) > 0:
        deleted = delete_items_by_key(items_to_delete, "WRT_todo", "time_added", "todo_item")
        return respond(None, "deleted %s items" % deleted)
    return respond(None, "no todo items to delete")

def delete_todo_by_index(user, index):
    items = get_all_todo_items(user)
    items_map = {}
    for i in items:
        items_map[i['time_added']] = i['todo_item']
        
    if index < 0 or index >= len(sorted(items_map.iterkeys())):
        return respond(None, "index out of range")
    key = sorted(items_map.iterkeys())[index]
    deleted = delete_items_by_key({key: items_map[key]}, "WRT_todo", "time_added", "todo_item")
    return respond(None, "deleted %s items" % deleted)

def add_todo_item(user, text):
    item = text
    time_added = decimal.Decimal(time.time())
    Item = { 
        'time_added': time_added,
        'todo_item' : item,
        'User_ID' : user
    }
    put_item_in_table(Item, "WRT_todo")
    
    return respond(None, "added: " + item)
