import boto3

def delete_items_by_key(items, table_name, primary_key, text_key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    items_deleted = len(items)
    for i in items:
        primary = sorted(items.iterkeys())[0]
        text = items[i]
        if text.startswith('[deleted]'):
            items_deleted -= 1
            continue
        table.update_item(
            Key = {
                primary_key : i
            },
            AttributeUpdates = {
                text_key : {
                    'Value' : str('[deleted] ' + text),
                    'Action' : 'PUT'
                }
            }
        )
    return items_deleted

def put_item_in_table(item, table_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    table.put_item(Item = item)

def get_items_from_table(table_name, filter_object, text_key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    response = table.scan(Select = 'ALL_ATTRIBUTES')
    count = response['Count']
    retval = []
    for i in range(count):
        if filter_object(response['Items'][i]) and not \
        response['Items'][i][text_key].startswith('[deleted]'):
            retval.append(response['Items'][i])
    return retval
