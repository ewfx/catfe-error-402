import os
import requests


CHATGROQ_API_KEY = "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"
CHATGROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "deepseek-r1-distill-qwen-32b"

SYSTEM_MESSAGE = """You are an advanced language model specialized in generating BDD (Behavior-Driven Development) step definitions using Python and the Behave library.

Your task is to:
    1. Analyze the given BDD feature file line by line.
    2. Identify each step (Given, When, Then, And) and generate a corresponding step definition.
    3. Generate a complete and functional Python script containing all necessary imports and structured functions.
    4. Use simple Python language, for input handling and assertions to validate expected outcomes.
    5. Avoid using global variables and ensure the code is well-structured and ready for execution with the Behave framework.
    6. Make sure the data used is according to the api schema
    7. Make sure all endpoints are according to the endpoints provided.
    8. Make sure all the import statements are valid

Output Format:
    1. Enclose the entire code inside three backticks ```python...```.
    2. The output should be a single, complete script containing all the generated step definitions.
    3. Do not include any explanations or comments—only the step definitions.

    Sample Step Definition file:
    from behave import when, then
import requests
import json

@when('I send a GET request to "/api/fraud-detection/"')
def step_impl(context):
    base_url = "http://192.168.1.5:8000"
    endpoint = "/api/fraud-detection/"
    url = f"{base_url}{endpoint}"
    response = requests.get(url)
    context.response = response

@then('the response status code should be 200')
def step_impl(context):
    assert context.response.status_code == 200, f"Expected status code 200, but got {context.response.status_code}"

@then('the response body should contain at least one transaction')
def step_impl(context):
    response_json = context.response.json()
    assert isinstance(response_json, list), "Response body should be a list of transactions"
    assert len(response_json) >= 1, "Response should contain at least one transaction"
    
Your primary objective is to produce a fully functional Behave step definition file based on the given BDD feature file.
"""


def generate_bdd(prompt: str, system_message: str = SYSTEM_MESSAGE) -> str:
    """
    Calls the ChatGroq API to generate a summary using the LLama model.

    Args:
        prompt (str): The input text to be summarized.
        system_message (str): The system instruction message for LLama.

    Returns:
        str: The summarized output from LLama.
    """
    try:
        headers = {
            "Authorization": f"Bearer {CHATGROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_completion_tokens": 4096

        }

        response = requests.post(CHATGROQ_API_URL, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()

        # Extract and return the generated text
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return "No response generated."

    except Exception as e:
        print(f"Error during Code Generation: {str(e)}")
        return "Error: Could not generate Step definition."

# print(generate_bdd("""Generate Python Behave step definitions for the following Gherkin BDD feature:

# Feature: Transaction Deletion
#   As a user
#   I want to be able to delete transactions
#   So that I can manage my transaction history

#   Scenario: Unsuccessful deletion of a transaction with invalid transaction_id
#     Given a transaction with invalid transaction_id "abc"
#     When I send a DELETE request to "/api/fraud-detection/abc"
#     Then the response status code should be 400
#     And the response body should contain "message": "Invalid transaction_id"

# API URL: http://192.168.1.5:9000/
# The output should be a complete Python script with appropriate Behave step definitions, including necessary imports and structured functions. Each function should be decorated with the corresponding Gherkin keyword (e.g., @given, @when, @then). Write the script inside triple ` backticks.

#     """))
