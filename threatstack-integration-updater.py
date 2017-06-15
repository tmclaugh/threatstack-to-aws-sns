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
    from urllib import urlopen

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

    function_name = os.environ.get('FUNCTION_NAME') or event.get('FunctionName')
    function_zip_file_url = os.environ.get('FUNCTION_ZIP_FILE_URL') or event.get('FunctionZipFileUrl')
    function_s3_bucket = os.environ.get('FUNCTION_S3_BUCKET') or event.get('FunctionS3Bucket')
    function_s3_key = os.environ.get('FUNCTION_S3_KEY') or event.get('FunctionS3Key')

    _logger.info(json.dumps(event))

    # S3{Bucket,Key} require S3 permissions/IAM policy for access. If using a
    # URL then we must fetch and get bytes.
    kwargs = {
        'FunctionName': function_name,
        'Publish': True
    }

    if function_zip_file_url:
        function_zip_file_bytes = _fetch_zip_file(function_zip_file_url)
        additional_args = {
            'ZipFile': function_zip_file_bytes.read()
        }
        kwargs.update(additional_args)
    else:
        additional_args = {
            'S3Bucket': function_s3_bucket,
            'S3Key': function_s3_key,
        }
        kwargs.update(additional_args)

    lambda_client = boto3.client('lambda')
    resp = lambda_client.update_function_code(**kwargs)

    _logger.info(json.dumps(resp))

    return resp

