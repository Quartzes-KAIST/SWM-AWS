import json
import boto3
import decimal

from config.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

dynamodb = boto3.resource(
    'dynamodb',
    region_name = "us-east-1",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

def json_default(value): 
    if isinstance(value, decimal.Decimal):
        return int(value)
    raise TypeError('not JSON serializable')

def update_data(userID, gameID, region, playTime):
    dynamodb.Table("comments").update_item(
        Key = {
            'gameID#region': gameID + "#" + region,
            'userID': userID
        },
        UpdateExpression = "set playTime=:p",
        ExpressionAttributeValues = {
            ':p': playTime
        },
        ReturnValues = "ALL_NEW"
    )

    return

def lambda_handler(event, context):
    body = json.loads(event['body'])
    
    region = body["region"]
    userID = body["userID"]
    # userID = event["requestContext"]["authorizer"]["jwt"]["claims"]["user_id"]

    result = {}

    for gameID, playTime in body["gameList"].items():
        update_data(userID, gameID, region, playTime)

    return {
        'statusCode': 200,
        'body': json.dumps({"body": "updated"})
    }

# test case

event = {
    'body': json.dumps(
        {
            'region': "KR",
            "userID": "quartzes",
            "gameList": 
            {
                "new": 1092843,
                "test": 1029349,
                "sample": 2934859,
            }
        }
    )
}

print(lambda_handler(event, None))