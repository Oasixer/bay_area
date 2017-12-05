import boto3
import time
import decimal

from wrt_respond import *

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

    count = response['Count']
    
    items = {}
    for i in range(count):
        items[str(float(response['Items'][i]['time_added']))] = response['Items'][i]['todo_item'].strip('"')
    
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
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('WRT_todo')

    return table.scan(
        Select = 'ALL_ATTRIBUTES',
        FilterExpression = boto3.dynamodb.conditions.Attr('User_ID').eq(user))

def clear_todo_items(user):
    items = get_all_todo_items(user)
    items_to_delete = {}
    for i in range(items['Count']):
        items_to_delete[items['Items'][i]['time_added']] = items['Items'][i]['todo_item']
    if len(items_to_delete) > 0:
        return delete_todo_by_key(items_to_delete)
    return respond(None, "no todo items to delete")

def delete_todo_by_key(items):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('WRT_todo')
    items_deleted = len(items)
    for i in items:
        primary = sorted(items.iterkeys())[0]
        text = items[i]
        if text.startswith('[deleted]'):
            items_deleted -= 1
            continue
        response = table.update_item(
            Key = {
                'time_added' : i
            },
            UpdateExpression = 'SET todo_item = :t',
            ExpressionAttributeValues = {
                ':t' : '[deleted] ' + text
            }
        )
    return respond(None, "deleted %s items" % items_deleted)

def delete_todo_by_index(user, index):
    items = get_all_todo_items(user)
    items_map = {}
    for i in range(items['Count']):
        if items['Items'][i]['todo_item'].startswith('[deleted]'):
            continue
        items_map[items['Items'][i]['time_added']] = items['Items'][i]['todo_item']
        
    if index < 0 or index >= len(sorted(items_map.iterkeys())):
        return respond(None, "index out of range")
    key = sorted(items_map.iterkeys())[index]
    return delete_todo_by_key({key: items_map[key]})

def add_todo_item(user, text):
    item = text
    time_added = decimal.Decimal(time.time())
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('WRT_todo')
    table.put_item(
        Item = { 
            'time_added': time_added,
            'todo_item' : item,
            'User_ID' : user
        })
    
    return respond(None, "added: " + item)
