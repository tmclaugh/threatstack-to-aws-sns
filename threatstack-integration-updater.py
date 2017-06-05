#!env python
import boto3
import json
import logging
from logging.config import fileConfig
import os

dirname = os.path.dirname(__file__)
logging_conf = os.path.join(dirname, 'logging.conf')
fileConfig(logging_conf, disable_existing_loggers=False)
if os.environ.get('TS_DEBUG'):
    logging.root.setLevel(level=logging.DEBUG)
_logger = logging.getLogger(__name__)

def handler(event, context):
    '''
    Update a lambda function.
    '''

    function_name = os.environ.get('FUNCTION_NAME') or event.get('FunctionName')
    function_s3_bucket = os.environ.get('FUNCTION_S3_BUCKET') or event.get('FunctionS3Bucket')
    function_s3_key = os.environ.get('FUNCTION_S3_KEY') or event.get('FunctionS3Key')

    _logger.info(event)

    lambda_client = boto3.client('lambda')
    resp = lambda_client.update_function_code(
        FunctionName=function_name,
        S3Bucket=function_s3_bucket,
        S3Key=function_s3_key,
        Publish=True
    )

    _logger.info(json.dumps(resp))

    exit(0)
