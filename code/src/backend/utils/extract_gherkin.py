import re

def extract_gherkin_scenarios(text, feature_name="Fraud Detection API"):
    """
    Extract and clean all BDD scenarios enclosed in triple backticks (```gherkin ... ```).
    Adds a "Feature" line at the beginning of each scenario.
    
    Args:
        text (str): The input text containing BDD scenarios.
        feature_name (str): The feature name to be added to each scenario.
    
    Returns:
        list: A list of cleaned Gherkin scenarios with feature names.
    """
    # Unescape the string to handle escaped newlines and quotes
    text = text.encode().decode('unicode_escape')

    # Regular expression to find all scenarios enclosed within triple backticks and "gherkin"
    pattern = r"```(?:\w*)?\n(.*?)```"
    blocks = re.findall(pattern, text, re.DOTALL)
    # if not blocks:
    #     pattern = r"```(.*?)```"
    #     blocks = re.findall(pattern, text, re.DOTALL)


    print(blocks)

    scenarios = []
    for block in blocks:
        # Extract individual scenarios from the block
        scenario_pattern = r"(Scenario:.*?)(?=Scenario:|$)"
        raw_scenarios = re.findall(scenario_pattern, block, re.DOTALL)

        print(raw_scenarios)
        
        # Clean and format each extracted scenario
        for scenario in raw_scenarios:
            cleaned_scenario = clean_scenario(scenario, feature_name)
            scenarios.append(cleaned_scenario)
    
    return scenarios

def clean_scenario(scenario, feature_name):
    """
    Clean the extracted BDD scenario by removing unnecessary escape characters and formatting properly.
    Adds a "Feature" line at the beginning of each scenario.
    
    Args:
        scenario (str): The raw BDD scenario.
        feature_name (str): The feature name to be added.
    
    Returns:
        str: The cleaned BDD scenario with the feature name.
    """
    # Remove leading and trailing newlines and extra spaces
    cleaned_scenario = scenario.strip()
    # Replace escaped newlines with actual newlines
    cleaned_scenario = cleaned_scenario.replace("\\n", "\n")
    # Replace escaped double quotes with actual double quotes
    cleaned_scenario = cleaned_scenario.replace('\\"', '"')
    # Add the feature name at the beginninge
    feature_line = f"Feature: {feature_name}\n"
    # Remove any unnecessary leading or trailing whitespace on each line
    cleaned_scenario = "\n".join(line.strip() for line in cleaned_scenario.splitlines())
    # Combine the feature line with the cleaned scenario
    return feature_line + cleaned_scenario


text = """Here are the BDD test cases for the Fraud Detection API:

# ```
# Feature: Fraud Detection API
#   Scenario 1: Create a Transaction with Valid Inputs
#     Given a transaction with
#       | transaction_id | Amount  | Currency | Location       |  
#       | 139           | ₹60,000 | INR      | Mumbai         |  
#     When I send a POST request to "/api/fraud-detection/"
#     Then the response status should be 201
#     And the response should contain "message", "transaction_id", "fraud_status", "fraud_score", and "alerts"
#     And the "message" should be "Transaction created successfully"
#     And the "fraud_status" should be "Fraudulent"
#     And the "fraud_score" should be greater than 70
#     And the "alerts" should contain at least one valid alert

#   Scenario 2: Create a Transaction with Invalid Inputs
#     Given a transaction with
#       | transaction_id | Amount  | Currency | Location       |  
#       | 139           | ₹-50,000 | INR      | Mumbai         |  
#     When I send a POST request to "/api/fraud-detection/"
#     Then the response status should be 400
#     And the response should contain "message" and "error"
#     And the "message" should be "Invalid transaction request"

#   Scenario 3: Get a Transaction by ID with Valid Inputs
#     Given a transaction ID "5"
#     When I send a GET request to "/api/fraud-detection/{transaction_id}"
#     Then the response status should be 200
#     And the response should contain "_id", "transaction_id", "user_id", "amount", "currency", "location", "merchant_id", "timestamp", "fraud_status", and "fraud_score"
#     And the "fraud_status" should be "Fraudulent"
#     And the "fraud_score" should be greater than 70

#   Scenario 4: Get a Transaction by ID with Invalid Inputs
#     Given a transaction ID " invalidID"
#     When I send a GET request to "/api/fraud-detection/{transaction_id}"
#     Then the response status should be 404
#     And the response should contain "message" and "error"
#     And the "message" should be "Transaction not found"

#   Scenario 5: Get All Transactions
#     When I send a GET request to "/api/fraud-detection/"
#     Then the response status should be 200
#     And the response should contain an array of transactions
#     And each transaction should contain "_id", "transaction_id", "user_id", "amount", "currency", "location", "merchant_id", "timestamp", "fraud_status", and "fraud_score"
#     And the "fraud_status" should be either "Fraudulent" or "Non-Fraudulent"
#     And the "fraud_score" should be either greater than or less than or equal to 70

#   Scenario 6: Delete a Transaction with Valid Inputs
#     Given a transaction ID "7"
#     When I send a DELETE request to "/api/fraud-detection/{transaction_id}"
#     Then the response status should be 200
#     And the response should contain "message"
#     And the "message" should be "Transaction deleted successfully"

#   Scenario 7: Delete a Transaction with Invalid Inputs
#     Given a transaction ID " invalidID"
#     When I send a DELETE request to "/api/fraud-detection/{transaction_id}"
#     Then the response status should be 404
#     And the response should contain "message" and "error"
#     And the "message" should be "Transaction not found"
# ```

# Note: The above test cases cover both success and failure cases comprehensively and are structured as a complete BDD feature file, ready for use."""

# # Print each cleaned scenario
# scenarios = extract_gherkin_scenarios(text)

# print(scenarios)