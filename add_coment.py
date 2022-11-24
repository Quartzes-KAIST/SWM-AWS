import json
import boto3
import decimal
import datetime

from config.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

dynamodb = boto3.resource(
    'dynamodb',
    region_name = "us-east-1",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

def get_now():
    return datetime.datetime.now()

def json_default(value): 
    if isinstance(value, decimal.Decimal):
        return int(value)
    raise TypeError('not JSON serializable')

def get_playtime(userID, gameID, region):
    response = dynamodb.Table("comments").get_item(
        Key = {
            'gameID#region': gameID + "#" + region,
            'userID': userID
        }
    )

    return int(response["Item"]["playTime"])

def write_comment(userID, gameID, region, body):
    # create time
    createDate = int(get_now().timestamp())

    # update data
    dynamodb.Table("comments").update_item(
        Key = {
            'gameID#region': gameID + "#" + region,
            'userID': userID
        },
        UpdateExpression = "set createDate=:c, rating=:r, shortText=:s, longText=:l, photoURL=:p, userName=:n",
        ExpressionAttributeValues = {
            ':c': createDate,
            ':r': body["rating"],
            ':s': body["shortText"],
            ':l': body["longText"],
            ':p': body["photoURL"],
            ':n': body["userName"]
        },
        ReturnValues = "ALL_NEW"
    )

    return

def lambda_handler(event, context):
    body = json.loads(event['body'])
    
    # base info
    region = body["region"]
    gameID = body["gameID"]
    userID = body["userID"]
    # userID = event["requestContext"]["authorizer"]["jwt"]["claims"]["user_id"]

    if get_playtime(userID, gameID, region) < 3600: # required play time to write
        return {
            'statusCode': 403,
            'body': json.dumps({'body': 'failed by playtime'})
        }

    write_comment(userID, gameID, region, body)

    return {
        'statusCode': 200,
        'body': json.dumps({'body': 'success'})
    }

# test case

event = {
    'body': json.dumps(
        {
            'region': "KR",
            "gameID": "sample",
            "userID": "quartzes",
            "rating": 5,
            "shortText": "개쩌네요",
            "longText": "안한사람 두뇌 삽니다.",
            "photoURL": "www.google.com"
        }
    )
}

print(lambda_handler(event, None))