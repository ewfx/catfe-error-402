import os
import requests
from dotenv import load_dotenv

load_dotenv()

CHATGROQ_API_KEY = os.getenv("CHATGROQ_API_KEY_2")
CHATGROQ_API_URL = os.getenv("CHATGROQ_API_URL")
MODEL_NAME = "deepseek-r1-distill-llama-70b"

SYSTEM_MESSAGE = """You are an advanced assistant specialized in analyzing and validating BDD (Behavior-Driven Development) feature files and step definitions written in Gherkin syntax and Python Behave. 

The generation and validation process should include the following:
1. Make sure all the import statements are valid
2. Make sure all endpoints are according to the endpoints provided.
3. Go through each line of the BDD feature file one by one.
4. For each line that represents a step (Given, When, Then, And), make sure a valid step definition is defined with matched title name.
5. If a step definition is missing or incorrect, generate the appropriate step definition.
6. If all step definitions are correct and present, respond with a fixed random string: "ahdG2kLdXydsauih".

The generated code should:
1. Follow Pythonic conventions and use the Behave library.
2. Handle input data efficiently.
3. Include necessary imports and structured functions.
4. Use assertions to validate expected outcomes.
5. Avoid using global variables.
6. Make sure the data used is according to the api schema
7. Include all the steps present in the bdd

Your primary goal is to:
1. Analyze the given BDD feature file and its corresponding step definitions.
2. Identify any python syntax inconsistencies, errors, or issues.
3. If everything is correct, respond only with the fixed random string: "ahdG2kLdXydsauih".
4. If there are issues or inconsistencies,:
   - Fix the errors directly in the step definitions.
   - Generate the corrected step definitions.
   - Enclose the corrected code inside three backticks (```python...```).

Your response should never contain explanations or comments, only the random string if everything is correct or the fixed code if there are issues.

The output should be:
1. If no issues are found, respond only with the fixed random string: "ahdG2kLdXydsauih".
2. If any issues are found, output the corrected step definitions inside triple backticks (```python...```), as a complete and functional Python script, ready to be used as a step definition file in a Behave BDD framework.

"""
RANDOM_STRING = "ahdG2kLdXydsauih"


# def read_step_def_from_file():
#     """
#     Reads the BDD syntax from the catfact.feature file.
#     """
#     try:
#         with open(os.path.join(STEP_DEFINITIONS_DIR, STEP_DEFINITIONS_FILE), "r") as file:
#             bdd_content = file.read()
#             print("Loaded BDD Syntax:")
#             print(bdd_content)
#             return bdd_content
#     except Exception as e:
#         print(f"Error reading BDD file: {str(e)}")
#         return ""

def check_step_def(bdd: str, step_definitions: str, api_schema: str, system_message: str = SYSTEM_MESSAGE) -> str:
    try:
        prompt = f"""
                Validate the following BDD feature file and its corresponding step definitions. 
If the syntax and mapping are correct, respond only with the random string: "ahdG2kLdXydsauih". 
If there are issues or inconsistencies, fix them directly and generate the corrected code inside three backticks (```...```).

API_SCHEMA: {api_schema}

Feature File (BDD):
{bdd}

Step Definitions:
{step_definitions}

Validation:

            """

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
            "temperature": 0.5,
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
        print(f"Error during checking syntax: {str(e)}")
        return "Error: Could not check syntax."


# print(check_step_def("""
#     Feature: Transaction Deletion
#   As a user
#   I want to be able to delete transactions
#   So that I can manage my transaction history

#   Scenario: Unsuccessful deletion of a transaction with invalid transaction_id
#     Given a transaction with invalid transaction_id "abc"
#     When I send a DELETE request to "/api/fraud-detection/abc"
#     Then the response status code should be 400
#     And the response body should contain "message": "Invalid transaction_id"
#     """))
        

# print(check_gherkin_syntax("""
#     Feature: Fraud Detection API

#   Scenario: Detect missing transaction data
#     Given a transaction with:
#       | transaction_id | Amount | Currency | Location | timestamp           |
#       | 7              | 0      | USD      | New York | 2025-03-20T14:00:00Z |
#     When I send a POST request to "/api/fraud-detection/"
#     Then the response status should be 400
#     And the response should contain an error message indicating missing data
# """))

# print(generate_bdd("""Generate Python Behave step definitions for the following Gherkin BDD feature:

#     Feature: Retrieve a random cat fact

#   Scenario: Successful retrieval of a random cat fact
#     Given the cat fact API is available at "https://catfact.ninja/fact"
#     When the user sends a GET request to fetch a random cat fact
#     Then the response status code should be 200
#     And the response should contain a random fact as a string
#     And the response should contain a "length" field indicating the fact length

# The output should be a complete Python script with appropriate Behave step definitions, including necessary imports and structured functions. Each function should be decorated with the corresponding Gherkin keyword (e.g., @given, @when, @then).

#     """))



