'''API to archive alerts from Threat Stack to AWS SNS'''

from app.errors import AppBaseError
import app.models.sns as sns_model
from flask import Blueprint, jsonify, request
import logging

_logger = logging.getLogger(__name__)

sns = Blueprint('sns', __name__)

class SNSViewBaseError(AppBaseError):
    '''Base SNS View error class.'''
    status_code = 400

class SNSViewWebhookDataError(SNSViewBaseError):
    '''Error with webhook data.'''

# Service routes.
@sns.route('/status', methods=['GET'])
def is_available():
    '''Test that AWS SNS is available.'''
    _logger.info('{}: {}'.format(request.method, request.path))


    sns_client = sns_model.SNSModel()
    sns_status = sns_client.is_available()
    sns_info = {'success': sns_status}

    status_code = 200
    if sns_status:
        success = True
    else:
        success = False

    return jsonify(success=success, sns=sns_info), status_code

@sns.route('/message', methods=['POST'])
def publish_message():
    '''Relay a webhook to AWS SNS.'''
    _logger.info('{}: {} - {}'.format(request.method,
                                      request.path,
                                      request.data))

    webhook_data = request.get_json()

    # Check webhook data to ensure correct format.
    if webhook_data == None:
        # Can be caused by incorrect Content-Type.
        msg ='No webhook data found in request: {}'.format(webhook_data)
        raise SNSViewWebhookDataError(msg)

    if not webhook_data.get('alerts'):
        msg = 'Webhook lacks alerts: {}'.format(webhook_data)
        raise SNSViewWebhookDataError(msg)

    for alert in webhook_data.get('alerts'):
        if not alert.get('id'):
            msg = "alert lacks 'id' field: {}".format(webhook_data)
            raise SNSViewWebhookDataError(msg)

        if not alert.get('created_at'):
            msg = "alert lacks 'created_at' field: {}".format(webhook_data)
            raise SNSViewWebhookDataError(msg)

    sns_client = sns_model.SNSModel()
    alerts = webhook_data.get('alerts')
    # this is to help us with the fact that Threat Stack batches alerts in
    # webhooks but when going through AWS API Gateway there's a 30s timeout.
    sns_responses = []
    for alert in alerts:
        single_alert = {'alerts': [alert]}
        resp = sns_client.publish_webhook(single_alert)
        sns_responses.append(resp)

    status_code = 200
    success = True
    response = {'success': success, 'sns': sns_responses}

    return jsonify(response), status_code

