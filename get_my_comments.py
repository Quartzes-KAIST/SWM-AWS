import json
import boto3
import decimal

from boto3.dynamodb.conditions import Key
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

def get_comments(userID):
    response = dynamodb.Table("comments").query(
        IndexName = "userID-Main",
        KeyConditionExpression = Key('userID').eq(userID)
    )

    return response["Items"]

def lambda_handler(event, context):
    # userID = event["requestContext"]["authorizer"]["jwt"]["claims"]["user_id"]
    userID = event["userID"]
    result = get_comments(userID)

    return {
        'statusCode': 200,
        'body': json.dumps(result, default = json_default)
    }

# test case

event = {
    "userID": "UMAjY9OfaAXUOKsmuGOUqxvXtbL2",
}

print(lambda_handler(event, None))