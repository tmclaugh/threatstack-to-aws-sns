#!env python
import boto3
import cfn_resource
import io
import json
import logging
from logging.config import fileConfig
import os
import sys
import zipfile

try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen

dirname = os.path.dirname(__file__)
logging_conf = os.path.join(dirname, 'logging.conf')
fileConfig(logging_conf, disable_existing_loggers=False)
if os.environ.get('TS_DEBUG'):
    logging.root.setLevel(level=logging.DEBUG)
_logger = logging.getLogger(__name__)

handler = cfn_resource.Resource()

def _fetch_zip_file(url):
    '''
    Fetch a file from a URL and return a file-like object.
    '''
    u = urlopen(url)
    zip_file = io.BytesIO(u.read())

    if zipfile.is_zipfile(zip_file):
        zip_file.seek(0)
    else:
        raise Exception('Not valid zipfile.')

    return zip_file

@handler.update
def update_lambda(event, context):
    '''
    Update a lambda function.
    '''
    properties = event.get('ResourceProperties')
    function_name = properties.get('FunctionName')
    function_zip_file_url = properties.get('FunctionZipFileUrl')
    function_s3_bucket = properties.get('FunctionS3Bucket')
    function_s3_key = properties.get('FunctionS3Key')

    _logger.info(json.dumps(event))

    # S3{Bucket,Key} require S3 permissions/IAM policy for access. If using a
    # URL then we must fetch and get bytes.
    lambda_update_kwargs = {
        'FunctionName': function_name,
        'Publish': True
    }

    if function_zip_file_url:
        function_zip_file_bytes = _fetch_zip_file(function_zip_file_url)
        additional_args = {
            'ZipFile': function_zip_file_bytes.read()
        }
        lambda_update_kwargs.update(additional_args)
    else:
        additional_args = {
            'S3Bucket': function_s3_bucket,
            'S3Key': function_s3_key,
        }
        lambda_update_kwargs.update(additional_args)

    lambda_client = boto3.client('lambda')
    lambda_update_resp = lambda_client.update_function_code(**lambda_update_kwargs)

    cfn_resp = {
        'Status': 'SUCCESS',
        'Data': lambda_update_resp,
        'PhysicalResourceId': lambda_update_resp.get('FunctionArn')
    }
    _logger.info(json.dumps(cfn_resp))

    return cfn_resp

if __name__ == '__main__':
    '''
    Make this runable locally via command line.
    '''
    event = {
        'ResourceProperties': {}
    }
    event['ResourceProperties']['FunctionName'] = os.environ.get('FUNCTION_NAME')
    event['ResourceProperties']['FunctionZipFileUrl'] = os.environ.get('FUNCTION_ZIP_FILE_URL')
    event['ResourceProperties']['FunctionS3Bucket'] = os.environ.get('FUNCTION_S3_BUCKET')
    event['ResourceProperties']['FunctionS3Key'] = os.environ.get('FUNCTION_S3_KEY')

    update_lambda({}, None)
