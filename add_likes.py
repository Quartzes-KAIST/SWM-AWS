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

def get_like_list(userID, gameID, region):
    response = dynamodb.Table("comments").get_item(
        Key = {
            'gameID#region': gameID + "#" + region,
            'userID': userID
        }
    )

    if "likedUser" in response["Item"]:
        return response["Item"]["likedUser"]
    else:
        return []

def add_likes(userID, gameID, region, target):
    dynamodb.Table("comments").update_item(
        Key = {
            'gameID#region': gameID + "#" + region,
            'userID': target
        },
        UpdateExpression = "set likes = if_not_exists(likes, :zero) + :add_val, likedUser = list_append(if_not_exists(likedUser, :empty_list), :userID_list)",
        ExpressionAttributeValues = {
            ':zero': decimal.Decimal(0),
            ':add_val': decimal.Decimal(1),
            ':empty_list': [],
            ':userID_list': [userID]
        },
        ReturnValues = "ALL_NEW"
    )

    return

def lambda_handler(event, context):
    body = json.loads(event['body'])
    
    region = body["region"]
    gameID = body["gameID"]
    userID = body["userID"]
    # userID = event["requestContext"]["authorizer"]["jwt"]["claims"]["user_id"]
    target = body["target"]

    # get like list
    like_list = get_like_list(target, gameID, region)

    # add user's like
    if userID in like_list:
        return {
            'statusCode': 403,
            'body': json.dumps({'body': 'user already liked target comment'})
        }
    else:
        add_likes(userID, gameID, region, target)

    return {
        'statusCode': 200,
        'body': json.dumps({'body': 'success'})
    }

# test case

event = {
    'body': json.dumps(
        {
            'region': "KR",
            "gameID": "jp.goodsmile.touhoulostwordglobal_android",
            "userID": "UMAjY9OfaAXUOKsmuGOUqxvXtbL2",
            "target": "UMAjY9OfaAXUOKsmuGOUqxvXtbL2",
        }
    )
}

print(lambda_handler(event, None))