def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'text': err.message if err else res,
        'headers': {
            'Content-Type': 'application/json',
        },
    }
