import json
import boto3
import decimal

from boto3.dynamodb.conditions import Key
from config.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

dynamodb = boto3.resource(
    'dynamodb',
    region_name="us-east-1",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


def json_default(value):
    if isinstance(value, decimal.Decimal):
        return int(value)
    raise TypeError('not JSON serializable')


def get_app_meta(gameID: str):
    response = dynamodb.Table("meta_data").query(
        KeyConditionExpression=Key('gameID').eq(gameID)
    )

    return response['Items'][0]


def lambda_handler(event, context):
    gameID = event['pathParameters']["gameID"]

    result = get_app_meta(gameID)

    print(result)

    return {
        'statusCode': 200,
        'body': json.dumps(result, default=json_default)
    }
