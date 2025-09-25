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
    items = body.get("items", [])

    if not order_id or not items:
        logger.error(f"Error: bad request - event = {json.dumps(body)}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "order_id and items are required"})
        }

    processing_time = round(random.uniform(0.5, 2.0), 2)
    time.sleep(processing_time)

    total = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)

    logger.info(f"Order {order_id} processed for customer {customer} with total {total:.2f} in {processing_time} seconds.")

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "message": f"Pedido {order_id} processado com sucesso!",
            "data": {
                "order_id": order_id,
                "customer": customer,
                "items": items,
                "total": round(total, 2),
                "processing_time": processing_time,
                "status": "processed"
            }
        })
    }
