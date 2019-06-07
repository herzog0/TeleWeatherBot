import json
import flask

from tele_weather_bot.bot import receiver


def respond(err, res=None):
    response = {
        "statusCode": 400 if err else 200,
        "body": str(err) if err else json.dumps(res),
        "headers": {
            "Content-Type": "application/json",
        },
    }

    return response["body"], response["statusCode"], response["headers"]


def lambda_handler(event, context=None):

    """Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

    To scan a DynamoDB table, make a GET request with the TableName as a
    query string parameter. To put, update, or delete an item, make a POST,
    PUT, or DELETE request respectively, passing in the payload to the
    DynamoDB API as a JSON body.
    """
    # print("Received event: " + json.dumps(event, indent=2))

    operations = {
        'POST': receiver,
    }

    # Extrai o corpo da requisição

    if event.is_json:
        payload = event.get_json()
    else:
        payload = None

    if payload:
        return respond(None, operations['POST'](payload))
    else:
        return respond(ValueError("Didn't understand a thing!"))
