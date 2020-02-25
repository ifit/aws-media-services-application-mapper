# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
This file contains the REST API and CloudWatch entry-points for the MSAM backend.
"""

import os

import boto3
from chalice import Chalice, Rate

from chalicelib import cache
import chalicelib.channels as channel_tiles
import chalicelib.cloudwatch as cloudwatch_data
import chalicelib.layout as node_layout
import chalicelib.periodic as periodic_handlers
import chalicelib.settings as msam_settings

app = Chalice(app_name='msam')

# update one region at this interval
NODE_UPDATE_RATE_MINUTES = 5

# update connections at this interval
CONNECTION_UPDATE_RATE_MINUTES = 5

# update subscribed alarm states at this interval
ALARM_UPDATE_RATE_MINUTES = 1

# update MSAM visuals from tags at this interval
TAG_UPDATE_RATE_MINUTES = 5

# table names generated by CloudFormation
ALARMS_TABLE_NAME = os.environ["ALARMS_TABLE_NAME"]
CHANNELS_TABLE_NAME = os.environ["CHANNELS_TABLE_NAME"]
CONTENT_TABLE_NAME = os.environ["CONTENT_TABLE_NAME"]
EVENTS_TABLE_NAME = os.environ["EVENTS_TABLE_NAME"]
LAYOUT_TABLE_NAME = os.environ["LAYOUT_TABLE_NAME"]
SETTINGS_TABLE_NAME = os.environ["SETTINGS_TABLE_NAME"]

# TTL provided via CloudFormation
CACHE_ITEM_TTL = int(os.environ["CACHE_ITEM_TTL"])

# DynamoDB
DYNAMO_CLIENT = boto3.client("dynamodb")
DYNAMO_RESOURCE = boto3.resource("dynamodb")


@app.route('/layout/view/{view}', cors=True, api_key_required=True, methods=['GET'])
def get_view_layout(view):
    """
    API entry point for retrieving all item positions in a view.
    """
    return node_layout.get_view_layout(app.current_request, view)


@app.route('/layout/nodes/{view}/{node_id}', cors=True, api_key_required=True, methods=['DELETE'])
def delete_view_layout(view, node_id):
    """
    API entry point for removing nodes from a view.
    """
    return node_layout.delete_node_layout(view, node_id)


@app.route('/layout/nodes', cors=True, api_key_required=True, methods=['PUT', 'POST'], content_types=['application/json', 'application/x-www-form-urlencoded'])
def set_view_layout():
    """
    API entry point for setting nodes in a view. This adds new nodes and overwrites existing nodes. It does not replace the entire set.
    """
    return node_layout.set_node_layout(app.current_request.json_body)


@app.route('/channels', cors=True, api_key_required=True, methods=['GET'])
def get_channel_list():
    """
    API entry point to return all the current channel names.
    """
    return channel_tiles.get_channel_list()


@app.route('/channel/{name}', cors=True, api_key_required=True, methods=['PUT', 'POST'], content_types=['application/json', 'application/x-www-form-urlencoded'])
def set_channel_nodes(name):
    """
     API entry point to set the nodes for a given channel name.
    """
    return channel_tiles.set_channel_nodes(name, app.current_request.json_body)


@app.route('/channel/{name}', cors=True, api_key_required=True, methods=['GET'])
def get_channel_nodes(name):
    """
    API entry point to get the nodes for a given channel name.
    """
    return channel_tiles.get_channel_nodes(name)


@app.route('/channel/{name}', cors=True, api_key_required=True, methods=['DELETE'])
def delete_channel_nodes(name):
    """
    API entry point to delete a channel.
    """
    return channel_tiles.delete_channel_nodes(app.current_request, name)


@app.route('/settings/{item_key}', cors=True, api_key_required=True, methods=['GET', 'PUT', 'POST', "DELETE"], content_types=['application/json', 'application/x-www-form-urlencoded'])
def application_settings(item_key):
    """
    API entry point to get or set the object value for a setting.
    """
    return msam_settings.application_settings(app.current_request, item_key)


@app.route('/cached/{service}/{region}', cors=True, api_key_required=True, methods=['GET'])
def cached_by_service_region(service, region):
    """
    API entry point to retrieve items from the cache under the service and region name.
    """
    return cache.cached_by_service_region(service, region)


@app.route('/cached/arn/{arn}', cors=True, api_key_required=True, methods=['GET'])
def cached_by_arn(arn):
    """
    API entry point to retrieve items from the cache by arn.
    """
    return cache.cached_by_arn(arn)


@app.route('/cached', cors=True, api_key_required=True, methods=['PUT', 'POST'], content_types=['application/json', 'application/x-www-form-urlencoded'])
def put_cached_data():
    """
    API entry point to add items to the cache.
    """
    return cache.put_cached_data(app.current_request)


@app.route('/cached/arn/{arn}', cors=True, api_key_required=True, methods=['DELETE'])
def delete_cached_data(arn):
    """
    API entry point to delete items from the cache.
    """
    return cache.delete_cached_data(arn)


@app.route('/regions', cors=True, api_key_required=True, methods=['GET'])
def regions():
    """
    API entry point to retrieve all regions based on EC2.
    """
    return cache.regions()


@app.route('/cloudwatch/alarms/all/{region}', cors=True, api_key_required=True, methods=['GET'])
def get_cloudwatch_alarms_region(region):
    """
    API entry point to retrieve all CloudWatch alarms for a given region.
    """
    return cloudwatch_data.get_cloudwatch_alarms_region(region)


@app.lambda_function()
def incoming_cloudwatch_alarm(event, _):
    """
    Standard AWS Lambda entry point for receiving CloudWatch alarm notifications.
    """
    return cloudwatch_data.incoming_cloudwatch_alarm(event, _)


@app.route('/cloudwatch/alarm/{alarm_name}/region/{region}/subscribe', cors=True, api_key_required=True, methods=['PUT', 'POST'])
def subscribe_resource_to_alarm(alarm_name, region):
    """
    API entry point to subscribe one or more nodes to a CloudWatch alarm in a region.
    """
    return cloudwatch_data.subscribe_resource_to_alarm(app.current_request, alarm_name, region)


@app.route('/cloudwatch/alarm/{alarm_name}/region/{region}/unsubscribe', cors=True, api_key_required=True, methods=['PUT', 'POST'])
def unsubscribe_resource_from_alarm(alarm_name, region):
    """
    API entry point to unsubscribe one or more nodes to a CloudWatch alarm in a region.
    """
    return cloudwatch_data.unsubscribe_resource_from_alarm(app.current_request, alarm_name, region)


@app.route('/cloudwatch/alarm/{alarm_name}/region/{region}/subscribers', cors=True, api_key_required=True, methods=['GET'])
def subscribers_to_alarm(alarm_name, region):
    """
    API entry point to return subscribed nodes of a CloudWatch alarm in a region.
    """
    return cloudwatch_data.subscribers_to_alarm(alarm_name, region)


@app.route('/cloudwatch/alarms/{alarm_state}/subscribers', cors=True, api_key_required=True, methods=['GET'])
def subscribed_with_state(alarm_state):
    """
    API entry point to return nodes subscribed to alarms in a given alarm state (OK, ALARM, INSUFFICIENT_DATA).
    """
    return cloudwatch_data.subscribed_with_state(alarm_state)


@app.route('/cloudwatch/alarms/subscriber/{resource_arn}', cors=True, api_key_required=True, methods=['GET'])
def alarms_for_subscriber(resource_arn):
    """
    API entry point to return all alarms subscribed to by a node.
    """
    return cloudwatch_data.alarms_for_subscriber(resource_arn)


@app.route('/cloudwatch/alarms/subscribed', cors=True, api_key_required=True, methods=['GET'])
def all_subscribed_alarms():
    """
    API entry point to return a unique list of all subscribed alarms in the database.
    """
    return cloudwatch_data.all_subscribed_alarms()


@app.route('/cloudwatch/events/state/{state}', cors=True, api_key_required=True, methods=['GET'])
def get_cloudwatch_events_state(state):
    """
    API entry point to retrieve all pipeline events in a given state (set, clear).
    """
    return cloudwatch_data.get_cloudwatch_events_state(state)


@app.route('/cloudwatch/events/all/{resource_arn}', cors=True, api_key_required=True, methods=['GET'])
def get_cloudwatch_events_resource(resource_arn):
    """
    API entry point to return all CloudWatch events related to a node.
    """
    return cloudwatch_data.get_cloudwatch_events_resource(resource_arn)


@app.route('/cloudwatch/events/{resource_arn}/{start_time}', cors=True, api_key_required=True, methods=['GET'])
def get_cloudwatch_events_resource(resource_arn, start_time):
    """
    API entry point to return all CloudWatch events related to a node from start_time to now.
    """
    return cloudwatch_data.get_cloudwatch_events_resource(resource_arn, start_time)


@app.route('/cloudwatch/events/{resource_arn}/{start_time}/{end_time}', cors=True, api_key_required=True, methods=['GET'])
def get_cloudwatch_events_resource(resource_arn, start_time, end_time):
    """
    API entry point to return all CloudWatch events related to a node for a given time range.
    """
    return cloudwatch_data.get_cloudwatch_events_resource(resource_arn, start_time, end_time)


@app.route('/ping', cors=True, api_key_required=True, methods=['GET'])
def ping():
    """
    API entry point to test the API key authentication and retrieve the build timestamp.
    """
    return {"message": "pong", "buildstamp": os.environ["BUILD_STAMP"]}


@app.schedule(Rate(NODE_UPDATE_RATE_MINUTES, unit=Rate.MINUTES))
def update_nodes(event):
    """
    Entry point for the CloudWatch scheduled task to discover and cache services.
    """
    # get this lambda's timeout value
    lambda_client = boto3.client("lambda")
    this_lambda = lambda_client.get_function(FunctionName=event.context.invoked_function_arn)
    # calculate millis
    total_ms = int(this_lambda['Configuration']['Timeout']) * 1000
    # we need 25% of our total run time remaining to keep going
    min_remain_ms = int(total_ms * 0.25)
    # loop until the remaining time is less than the minimum
    while min_remain_ms < event.context.get_remaining_time_in_millis():
        periodic_handlers.update_nodes()
        # print the stats
        print("remaining time {}ms".format(event.context.get_remaining_time_in_millis()))
        print("required remaining time {}ms".format(min_remain_ms))


@app.schedule(Rate(CONNECTION_UPDATE_RATE_MINUTES, unit=Rate.MINUTES))
def update_connections(_):
    """
    Entry point for the CloudWatch scheduled task to discover and cache services.
    """
    return periodic_handlers.update_connections()


@app.schedule(Rate(ALARM_UPDATE_RATE_MINUTES, unit=Rate.MINUTES))
def update_alarms(_):
    """
    Entry point for the CloudWatch scheduled task to discover and cache services.
    """
    return periodic_handlers.update_alarms()


@app.schedule(Rate(TAG_UPDATE_RATE_MINUTES, unit=Rate.MINUTES))
def update_from_tags(_):
    """
    Entry point for the CloudWatch scheduled task to discover and cache services.
    """
    return periodic_handlers.update_from_tags()
