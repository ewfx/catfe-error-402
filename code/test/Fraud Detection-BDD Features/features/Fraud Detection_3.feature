Feature: Fraud Detection API
Scenario: Get a Transaction by ID with Invalid ID
When I send a GET request to "/api/fraud-detection/999"
Then the response status code should be 404
And the response body should contain "message" with value "Transaction not found"