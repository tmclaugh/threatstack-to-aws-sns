'''AWS SNS Communication'''
from app.errors import AppBaseError
import boto3
from botocore.exceptions import ClientError
import config
import json
import logging
import six
import sys

_logger = logging.getLogger(__name__)

AWS_SNS_TOPIC = config.AWS_SNS_TOPIC

class SNSModelBaseError(AppBaseError):
    '''Base SNS error class.'''

class SNSClientError(SNSModelBaseError):
    '''SNS client error class.'''

class SNSModel:
    '''Communicate with AWS SNS'''

    def __init__(self, sns_topic_name=AWS_SNS_TOPIC):
        '''Initialize'''
        self.sns_client = boto3.client('sns')
        self.sns_topic_name = sns_topic_name
        self.sns_topic_arn = self._get_topic_arn_by_name(self.sns_topic_name)

    def _get_topic_arn_by_name(self, sns_topic_name):
        '''Return the topic ARN for the given name.'''
        # FIXME: Need to handle paginated results.
        topic_arn = None

        try:
            topics = self.sns_client.list_topics()
        except ClientError as e:
            exc_info = sys.exc_info()
            if sys.version_info >= (3,0,0):
                raise SNSClientError(e).with_traceback(exc_info[2])
            else:
                six.reraise(SNSClientError, SNSClientError(e), exc_info[2])

        for topic in topics['Topics']:
            arn = topic['TopicArn']
            if arn.split(':')[-1] == sns_topic_name:
                topic_arn = arn
                break

        return topic_arn


    def is_available(self):
        '''Check ability to access SNS topic.'''
        try:
            # FIXME: We should check that we can write to topic if possible.
            topic_attributes = self.sns_client.get_topic_attributes(
                TopicArn=self.sns_topic_arn
            )
            _logger.debug('topic_atributes: %s' % topic_attributes)
        except ClientError as e:
            exc_info = sys.exc_info()
            if sys.version_info >= (3,0,0):
                raise SNSClientError(e).with_traceback(exc_info[2])
            else:
                six.reraise(SNSClientError, SNSClientError(e), exc_info[2])

        # We should throw an error if there's an issue.
        return topic_attributes

    def publish_webhook(self, webhook):
        '''Publish webhook to SNS topic.'''
        try:
            # We don't do retry failure handling because because the topic
            # should handle that for us.
            sns_resp = self.sns_client.publish(TopicArn=self.sns_topic_arn,
                                               Message=json.dumps(webhook))
            _logger.debug('sns_resp: %s' % sns_resp)
        except ClientError as e:
            exc_info = sys.exc_info()
            if sys.version_info >= (3,0,0):
                raise SNSClientError(e).with_traceback(exc_info[2])
            else:
                six.reraise(SNSClientError, SNSClientError(e), exc_info[2])

        if sns_resp['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise SNSClientError('SNS failure: %s' % sns_resp)

        return sns_resp

