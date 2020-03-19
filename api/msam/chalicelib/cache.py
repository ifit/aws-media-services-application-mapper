# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
This file contains helper functions for updating and querying the cache.
"""

import os
from urllib.parse import unquote

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from botocore.config import Config

# table names generated by CloudFormation
CONTENT_TABLE_NAME = os.environ["CONTENT_TABLE_NAME"]

# user-agent config
STAMP = os.environ["BUILD_STAMP"]
MSAM_BOTO3_CONFIG = Config(user_agent="aws-media-services-applications-mapper/{stamp}/cache.py".format(stamp=STAMP))


def cached_by_service(service):
    """
    Retrieve items from the cache for the given service name.
    """
    try:
        ddb_table_name = CONTENT_TABLE_NAME
        # ddb_index_name = "service-index"
        ddb_index_name = "ServiceRegionIndex"
        ddb_resource = boto3.resource('dynamodb', config=MSAM_BOTO3_CONFIG)
        ddb_table = ddb_resource.Table(ddb_table_name)
        response = ddb_table.query(IndexName=ddb_index_name, KeyConditionExpression=Key('service').eq(service))
        items = response["Items"]
        # check for paging
        while "LastEvaluatedKey" in response:
            # query again with start key
            response = ddb_table.query(IndexName=ddb_index_name, KeyConditionExpression=Key('service').eq(service), ExclusiveStartKey=response['LastEvaluatedKey'])
            items = items + response["Items"]
        # return when done paging
        return items
    except ClientError as error:
        print(error)
        return {"message": str(error)}


def cached_by_service_region(service, region):
    """
    API entry point to retrieve items from the cache under the service and region name.
    """
    try:
        service = unquote(service)
        region = unquote(region)
        ddb_table_name = CONTENT_TABLE_NAME
        ddb_index_name = "ServiceRegionIndex"
        ddb_resource = boto3.resource('dynamodb', config=MSAM_BOTO3_CONFIG)
        ddb_table = ddb_resource.Table(ddb_table_name)
        response = ddb_table.query(IndexName=ddb_index_name, KeyConditionExpression=Key('service').eq(service) & Key('region').eq(region))
        items = response["Items"]
        while "LastEvaluatedKey" in response:
            response = ddb_table.query(IndexName=ddb_index_name, KeyConditionExpression=Key('service').eq(service) & Key('region').eq(region), ExclusiveStartKey=response['LastEvaluatedKey'])
            items = items + response["Items"]
        return items
    except ClientError as error:
        print(error)
        return {"message": str(error)}


def cached_by_arn(arn):
    """
    API entry point to retrieve an item from the cache under the ARN.
    """
    try:
        arn = unquote(arn)
        ddb_table_name = CONTENT_TABLE_NAME
        ddb_resource = boto3.resource('dynamodb', config=MSAM_BOTO3_CONFIG)
        ddb_table = ddb_resource.Table(ddb_table_name)
        response = ddb_table.query(KeyConditionExpression=Key('arn').eq(arn))
        items = response["Items"]
        while "LastEvaluatedKey" in response:
            response = ddb_table.query(KeyConditionExpression=Key('arn').eq(arn), ExclusiveStartKey=response['LastEvaluatedKey'])
            items = items + response["Items"]
        return items
    except ClientError as error:
        print(error)
        return {"message": str(error)}


def put_cached_data(request):
    """
    API entry point to add items to the cache.
    """
    try:
        ddb_table_name = CONTENT_TABLE_NAME
        ddb_resource = boto3.resource('dynamodb', config=MSAM_BOTO3_CONFIG)
        ddb_table = ddb_resource.Table(ddb_table_name)
        cache_entries = request.json_body
        print(cache_entries)
        # write the channel nodes to the database
        for entry in cache_entries:
            # workaround for dynamodb numeric types
            entry["expires"] = int(entry["expires"])
            entry["updated"] = int(entry["updated"])
            ddb_table.put_item(Item=entry)
        return {"message": "saved"}
    except ClientError as error:
        print(error)
        return {"message": str(error)}


def delete_cached_data(arn):
    """
    API entry point to delete items from the cache.
    """
    try:
        arn = unquote(arn)
        ddb_table_name = CONTENT_TABLE_NAME
        ddb_resource = boto3.resource('dynamodb', config=MSAM_BOTO3_CONFIG)
        ddb_table = ddb_resource.Table(ddb_table_name)
        # cache_entries = request.json_body
        # print(cache_entries)
        # write the channel nodes to the database
        # for entry in cache_entries:
        ddb_table.delete_item(Key={"arn": arn})
        return {"message": "deleted"}
    except ClientError as error:
        print(error)
        return {"message": str(error)}


def regions():
    """
    API entry point to retrieve all regions based on EC2.
    """
    service = boto3.client("ec2", config=MSAM_BOTO3_CONFIG)
    response = service.describe_regions()
    return response["Regions"]
