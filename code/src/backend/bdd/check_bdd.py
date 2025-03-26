import os
import requests
from dotenv import load_dotenv

load_dotenv()

CHATGROQ_API_KEY = os.getenv("CHATGROQ_API_KEY_2")
CHATGROQ_API_URL = os.getenv("CHATGROQ_API_URL")
MODEL_NAME = "deepseek-r1-distill-llama-70b"


RANDOM_STRING = "ahdG2kLdXydsauih"

SYSTEM_MESSAGE = f"""You are an advanced and highly efficient language model designed to validate and correct BDD (Behavior-Driven Development) syntax written in Gherkin. Your primary goal is to analyze BDD feature files, identify any syntax errors, and either confirm the correctness or provide clear and concise corrections.


The validation process should include:
1. Make sure each line of the test case starts with either of "Feature", "Scenario", "Given", "Then", "When" or "And" nothing else.

Your response should follow these rules:
1. If the BDD syntax is correct, respond only with a fixed random string: {RANDOM_STRING}.
2. If the BDD syntax is incorrect:
   - Clearly explain what is wrong.
   - Provide the corrected syntax enclosed within three backticks (```gherkin...```).
   - Ensure the corrected syntax follows standard BDD conventions.

Your output should be easy to understand, professional, and structured. Never respond with conversational text or irrelevant information.

"""

def check_gherkin_syntax(bdd: str, system_message: str = SYSTEM_MESSAGE) -> str:
    try:
        prompt = f"""
                Check the Gherkin BDD syntax for the following input. 
If the syntax is correct, respond with {RANDOM_STRING}. 
If the syntax is incorrect, provide the corrected syntax inside ```gherkin...``` 3 backticks along with a brief explanation of what was wrong.

BDD Syntax:
{bdd}


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
            "temperature": 0.4

        }

        response = requests.post(CHATGROQ_API_URL, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()

        print(result)

        # Extract and return the generated text
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return "No response generated."

    except Exception as e:
        print(f"Error during checking syntax: {str(e)}")
        return "Error: Could not check syntax."

        

# print(check_gherkin_syntax("""
# Here is the scenario considering the information you ahve shared with me

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



