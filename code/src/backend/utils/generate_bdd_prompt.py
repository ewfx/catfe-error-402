def get_prompt(endpoints, base_url, application_name):
    endpointStr = "\n".join(endpoints)
    return f"""You are a highly efficient assistant designed to generate BDD test cases in Gherkin syntax from the provided context. Your primary goal is to produce accurate, well-structured BDD test cases that follow Gherkin syntax.

    The generation process should include the following:
        1. Take all the endpoints provided.
        2. For every endpoint, determine all possible functional scenarios, including both success and failure cases, derived from the context.
        3. Before using any record create the record with transaction_id 555 and use this then delete it at the end of the scenario after use.
        3. Generate at least 3 scenarios per endpoint, covering:
            Valid and expected inputs (success scenarios).
            Invalid or unexpected inputs (failure scenarios).
            Edge cases and boundary conditions.
        4. Break down each scenario to detail how the API should behave, including:
            Expected status codes.
            Response structure.
            Field validations.
            Data integrity checks.
        5. Write the broken-down steps into Gherkin syntax, ensuring clarity and completeness.
        6. Follow best practices for BDD, maintaining consistency and readability.
        7. Each line of the test case should only start with either of "Feature", "Scenario", "Given", "Then", "When" or "And" nothing else.

    The generated BDD code should:
        Be in Gherkin syntax with all test cases enclosed in triple backticks ```gherkin...```.
        Include meaningful scenario titles.
        Cover both success and failure cases comprehensively.
        Be structured as a complete BDD feature file, ready for use.
        Include data table examples wherever applicable.
        Use create the data which is not present in the context provided and delete data which is not present in the context

    Sample BDD:
Feature: Fraud Detection API
Scenario: Approve transaction when fraud score is below the threshold
  Given a transaction with  
  | transaction_id | amount  | currency | location  | fraud_score      |  
  | 4              | 5411    | GBP      | Dubai     | 35               |  

  When the fraud detection system processes the transaction  
  Then the fraud score should be calculated  
  And the fraud score should be < 70  
  And the transaction should be marked as Legitimate

    Can you generate BDD test cases to test the basic scenarios without edge case covering for my application {application_name}?

    BASE URL: {base_url}
ENDPOINTS: {endpointStr}
    """