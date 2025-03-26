Feature: Fraud Detection API
Scenario: Get All Transactions
When I send a GET request to "/api/fraud-detection/"
Then the response status code should be 200
And the response body should be a list of transactions with at least one transaction