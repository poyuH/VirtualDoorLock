from boto3 import resource
import json


print('Loading function')
visitors_table = resource('dynamodb').Table('visitors')
photo_table = resource('dynamodb').Table('photo')

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Origin" : "*",
            "Access-Control-Allow-Credentials" : True
        },
    }


def lambda_handler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

    To scan a DynamoDB table, make a GET request with the TableName as a
    query string parameter. To put, update, or delete an item, make a POST,
    PUT, or DELETE request respectively, passing in the payload to the
    DynamoDB API as a JSON body.
    '''
    #print("Received event: " + json.dumps(event, indent=2))
    operations = {
        # 'DELETE': lambda dynamo, x: dynamo.delete_item(**x),
        'GET': lambda photo_table, faceId: photo_table.get_item(Key={'faceId':faceId}),
        'POST': lambda visitors_table, x: visitors_table.put_item(Item=x),
        # 'PUT': lambda dynamo, x: dynamo.update_item(**x),
    }
    operation = event['httpMethod']
    if operation == 'GET':
        payload = event['queryStringParameters']['faceId']
        result = operations[operation](photo_table, payload).get('Item')
        return respond(None, result)

    elif operation in operations:
        payload = json.loads(event['body'])
        if not payload.get('is_granted'):
            return respond(None, None)
        payload.pop('is_granted')
        return respond(None, operations[operation](visitors_table, payload))
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))

