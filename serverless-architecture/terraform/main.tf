provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_requesting_account_id  = true

  endpoints {
    lambda       = "http://localhost:4566"
    apigateway   = "http://localhost:4566"
    iam          = "http://localhost:4566"
  }
}

########################
# Lambda Functions
########################
resource "aws_lambda_function" "process_order" {
  function_name    = "process_order"
  handler          = "handler.lambda_handler"
  runtime          = "python3.10"
  filename         = "../lambdas/process_order/lambda.zip"
  source_code_hash = filebase64sha256("../lambdas/process_order/lambda.zip")
  role             = "arn:aws:iam::000000000000:role/lambda_exec_role"
}

resource "aws_lambda_function" "send_notification" {
  function_name    = "send_notification"
  handler          = "handler.lambda_handler"
  runtime          = "python3.10"
  filename         = "../lambdas/send_notification/lambda.zip"
  source_code_hash = filebase64sha256("../lambdas/send_notification/lambda.zip")
  role             = "arn:aws:iam::000000000000:role/lambda_exec_role"
}

resource "aws_lambda_function" "charge_payment" {
  function_name    = "charge_payment"
  handler          = "handler.lambda_handler"
  runtime          = "python3.10"
  filename         = "../lambdas/charge_payment/lambda.zip"
  source_code_hash = filebase64sha256("../lambdas/charge_payment/lambda.zip")
  role             = "arn:aws:iam::000000000000:role/lambda_exec_role"
}

########################
# API Gateway
########################
resource "aws_api_gateway_rest_api" "api" {
  name        = "ServerlessAPI"
  description = "API Gateway para protótipo serverless"
}

# Orders
resource "aws_api_gateway_resource" "orders" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "orders"
}

resource "aws_api_gateway_method" "process_order_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.orders.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "process_order_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.orders.id
  http_method             = aws_api_gateway_method.process_order_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.process_order.invoke_arn
}

resource "aws_lambda_permission" "allow_apigw_process_order" {
  statement_id  = "AllowAPIGatewayInvokeProcessOrder"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.process_order.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

# Notifications
resource "aws_api_gateway_resource" "notifications" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "notifications"
}

resource "aws_api_gateway_method" "send_notification_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.notifications.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "send_notification_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.notifications.id
  http_method             = aws_api_gateway_method.send_notification_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.send_notification.invoke_arn
}

resource "aws_lambda_permission" "allow_apigw_send_notification" {
  statement_id  = "AllowAPIGatewayInvokeSendNotification"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.send_notification.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

# Payments
resource "aws_api_gateway_resource" "payments" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "payments"
}

resource "aws_api_gateway_method" "charge_payment_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.payments.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "charge_payment_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.payments.id
  http_method             = aws_api_gateway_method.charge_payment_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.charge_payment.invoke_arn
}

resource "aws_lambda_permission" "allow_apigw_charge_payment" {
  statement_id  = "AllowAPIGatewayInvokeChargePayment"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.charge_payment.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

########################
# Deployment & Stage
########################
resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id

  depends_on = [
    aws_api_gateway_integration.process_order_integration,
    aws_api_gateway_integration.send_notification_integration,
    aws_api_gateway_integration.charge_payment_integration
  ]
}

resource "aws_api_gateway_stage" "dev_stage" {
  stage_name    = "dev"
  rest_api_id   = aws_api_gateway_rest_api.api.id
  deployment_id = aws_api_gateway_deployment.deployment.id
}

########################
# Output
########################
output "api_url" {
  value = "${aws_api_gateway_rest_api.api.execution_arn}/${aws_api_gateway_stage.dev_stage.stage_name}"
}
