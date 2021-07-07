'''Template for a Python3 project on AWS.'''
import json
import boto3
import sys

from libs import aws
from libs.helpers import safe_dumps


def default(event, context):
    """Default handler for websocket messages"""
    message = event.get('body', '')

    if not message.strip():
        return {
            'statusCode': 200,
        }

    if message.startswith('/'):
        return _handle_slash(message, event)

    connection_id, request_time = _get_conn_id_and_time(event)

    user = aws.get_user(connection_id)
    channel_name = user.get('channel_name', 'general')
    username = user.get('username', 'anonymous')

    # Save the message to dynamodb
    aws.save_message(connection_id, request_time, message, channel_name)

    # broadcast the message to all connected users
    _broadcast(
        message,
        _get_endpoint(event),
        connection_id,
        channel_name,
        username,
    )

    return {
        'statusCode': 200,
        'body': safe_dumps(message),
    }


def handle_cmd(event, context):
    payload = json.loads(event['body'])
    command = payload['data']

    handlers = {
        'fetchChannels': fetch_channels,
    }

    handlers[command](event)

    return {
        'statusCode': 200,
    }


def fetch_channels(event):
    channels = aws.get_channels_list()
    _send_message_to_client(event, safe_dumps({'channelsList': sorted(channels)}))


def _broadcast(message, endpoint, sender, channel, username):
    client = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint)

    # need to look up what channel the user is connected to
    for connection_id in aws.get_connected_connection_ids(channel):
        if connection_id == sender:
            continue

        client.post_to_connection(
            ConnectionId=connection_id,
            Data='#{} {}: {}'.format(channel, username, message),
        )


def connect(event, context):
    connection_id = _get_connection_id(event)
    aws.set_connection_id(connection_id)

    return {
        'statusCode': 200,
        'body': 'connect',
    }


def disconnect(event, context):
    connection_id = _get_connection_id(event)

    user = aws.get_user(connection_id)
    channel_name = user.get('channel_name', 'general')
    aws.delete_connection_id(connection_id, channel_name)

    return {
        'statusCode': 200,
        'body': 'disconnect',
    }


def _handle_slash(message, event):
    if message.startswith('/name '):
        return _set_name(message, event)

    if message.startswith('/channel '):
        return _set_channel(message, event)

    return _help(event)


def _help(event):
    message = "Valid commands: /help, /name [NAME], /channel [CHAN_NAME]"
    _send_message_to_client(event, message)
    return {
        'statusCode': 200,
        'body': 'help',
    }


def _set_name(message, event):
    name = message.split('/name')[-1]
    connection_id = _get_connection_id(event)
    aws.save_username(connection_id, name.strip())

    _send_message_to_client(event, 'Set username to {}'.format(name.strip()))

    return {
        'statusCode': 200,
        'body': 'name',
    }


def _set_channel(message, event):
    channel_name = message.split('/channel')[-1]
    channel_name = channel_name.strip('# ')

    connection_id = _get_connection_id(event)

    aws.update_channel_name(connection_id, channel_name)
    aws.set_connection_id(connection_id, channel=channel_name)

    _send_message_to_client(event, 'Changed to #{}'.format(channel_name))

    return {
        'statusCode': 200,
        'body': 'name',
    }


def _send_message_to_client(event, message):
    client = boto3.client('apigatewaymanagementapi', endpoint_url=_get_endpoint(event))
    client.post_to_connection(
        ConnectionId=_get_connection_id(event),
        Data=message,
    )


def _get_connection_id(event):
    ctx = event['requestContext']
    return ctx['connectionId']


def _get_request_time(event):
    ctx = event['requestContext']
    return ctx['requestTimeEpoch']


def _get_conn_id_and_time(event):
    ctx = event['requestContext']
    return (ctx['connectionId'], ctx['requestTimeEpoch'])


def _get_endpoint(event):
    ctx = event['requestContext']
    domain = ctx['domainName']
    stage = ctx['stage']
    return 'https://{}/{}'.format(domain, stage)
