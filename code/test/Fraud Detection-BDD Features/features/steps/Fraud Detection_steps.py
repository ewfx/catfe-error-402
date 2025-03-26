from behave import when, then
import requests
import json

@when('I send a DELETE request to "/api/fraud-detection/999"')
def step_impl(context):
    base_url = "http://192.168.1.5:9001"
    endpoint = "/api/fraud-detection/999"
    url = f"{base_url}{endpoint}"
    response = requests.delete(url)
    context.response = response

@then('the response status code should be 404')
def step_impl(context):
    assert context.response.status_code == 404, f"Expected status code 404, but got {context.response.status_code}"

@then('the response body should contain "message" with value "Transaction not found"')
def step_impl(context):
    response_json = context.response.json()
    assert "message" in response_json, "Response body does not contain 'message' field"
    assert response_json["message"] == "Transaction not found", f"Expected message 'Transaction not found', but got {response_json['message']} instead"
