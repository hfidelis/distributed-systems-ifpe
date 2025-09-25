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
    amount = body.get("amount", 0)
    card_number = body.get("card_number", "")

    if not order_id or not amount or not card_number:
        logger.error(f"Error: bad request - event = {json.dumps(body)}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "order_id, amount and card_number are required"})
        }

    if len(card_number) != 16 or not card_number.isdigit():
        logger.error(f"Error: invalid card number - event = {json.dumps(body)}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid card number"})
        }

    time.sleep(random.uniform(0.5, 1.5))

    approved = random.choice([True, True, True, False])

    logger.info(f"Payment for order {order_id} {'approved' if approved else 'declined'}.")

    return {
        "statusCode": 200 if approved else 402,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "message": "Payment approved" if approved else "Payment declined",
            "data": {
                "order_id": order_id,
                "amount": amount,
                "card_number": f"**** **** **** {card_number[-4:]}",
                "status": "approved" if approved else "declined"
            }
        })
    }
