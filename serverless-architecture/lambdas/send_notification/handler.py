import json
import time
import random
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        body = json.loads(event.get("body", "{}"))
    except Exception as e:
        logger.error(f"Error parsing body: {str(e)}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON body"})
        }

    order_id = body.get("order_id", None)
    customer = body.get("customer", "Unknown")
    notification_type = body.get("type", "email")

    if not order_id:
        logger.error(f"Error: bad request - event = {json.dumps(body)}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "order_id is required"})
        }

    time.sleep(random.uniform(0.2, 0.8))

    logger.info(f"Notification sent for order {order_id} to customer {customer} via {notification_type}.")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Notificação enviada via {notification_type} para {customer}",
            "data": {
                "order_id": order_id,
                "customer": customer,
                "type": notification_type,
                "status": "sent"
            }
        })
    }
