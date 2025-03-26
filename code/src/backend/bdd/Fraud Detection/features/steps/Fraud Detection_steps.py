from behave import when
import requests

@when('I send a DELETE request to "{endpoint}"')
def send_delete_request(context, endpoint):
    try:
        context.response = requests.delete(endpoint)
        context.response.raise_status()
    except requests.exceptions.RequestException as e:
        context.response = e