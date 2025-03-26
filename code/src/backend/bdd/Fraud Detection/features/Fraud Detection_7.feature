Feature: Fraud Detection API
Scenario: Delete Transaction with Invalid Input - Non-Existing ID
Given a transaction does not exist with ID "666"
When I send a DELETE request to "/api/fraud-detection/666"
Then the response status should be 404
And the response should contain "message"
And the message should contain "transaction not found"

Before