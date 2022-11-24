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

def get_leaderboard(gameID, region):
    response = dynamodb.Table("comments").query(
        IndexName = "playTime-index",
        Limit = 20,
        ScanIndexForward = False,
        KeyConditionExpression = 
        Key('gameID#region').eq(gameID + "#" + region)
    )

    return response['Items']

def lambda_handler(event, context):
    region = event['pathParameters']['region']
    gameID = event['pathParameters']["gameID"]

    result = get_leaderboard(gameID, region)
    
    return {
        'statusCode': 200,
        'body': json.dumps(result, default = json_default)
    }

event = {
    'pathParameters':
    {
        "region": "KR",
        "gameID": "com.blizzard.wtcg.hearthstone"
    }
}

print(lambda_handler(event, None))