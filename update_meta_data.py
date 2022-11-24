import json
import boto3

from boto3.dynamodb.conditions import Key
from config.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

# https://pypi.org/project/google-play-scraper/
from google_play_scraper import app


AWS_BUCKET_NAME = "real-gamers-critics"
s3 = boto3.resource(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
dynamodb = boto3.resource(
    'dynamodb',
    region_name="us-east-1",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


def meta_update(gameID, title, iconURL, screenshotURLs, category, reviewCount, summary):
    dynamodb.Table("meta_data").update_item(
        Key={
            'gameID': gameID
        },
        UpdateExpression="set title=:t, iconURL=:i, screenshotURLs=:s, category=:c, reviewCount=:r, summary=:sum",
        ExpressionAttributeValues={
            ':t': title,
            ':i': iconURL,
            ':s': screenshotURLs,
            ':c': category,
            ':r': reviewCount,
            ':sum': summary
        }
    )

    return


def s3_save_json(json_object, filename):
    filename = "applist/" + filename + ".json"

    # upload file
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.put
    s3.Object(
        AWS_BUCKET_NAME,
        filename,
    ).put(
        Body=json.dumps(json_object, ensure_ascii=False),
        ACL='public-read'
    )

    result = filename + ' upload complete'
    return {'response': result}


def lambda_handler(event, context):
    comment_counts = {}
    scan_result = dynamodb.Table("comments").scan(
        FilterExpression=Key('shortText').gt("")
    )

    for comment in scan_result["Items"]:
        gameID = comment["gameID#region"].split("#")[0]

        if gameID not in comment_counts:
            comment_counts[gameID] = 0

        comment_counts[gameID] += 1

    err = []
    updated = []
    json_data = []
    for gameID, reviewCount in comment_counts.items():
        try:
            # https://pypi.org/project/google-play-scraper/
            result = app(gameID, lang='en', country='us')  # defaults to en-us

            title = result["title"]
            iconURL = result["icon"]
            screenshotURLs = result["screenshots"]
            category = result["genre"]
            summary = result["summary"]

            meta_update(gameID, title, iconURL, screenshotURLs,
                        category, reviewCount, summary)

            updated.append(gameID)
            json_data.append(
                (reviewCount, {"title": title, "gameId": gameID, "icon": iconURL, "category": category}))

        except Exception as e:
            err.append((gameID, e))

    # 임시 앱 랭킹 (검색용)
    s3_save_json([i[1] for i in sorted(
        json_data, key=lambda x: x[0], reverse=True)], "byReviews")

    return updated, err
