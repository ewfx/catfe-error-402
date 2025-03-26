Feature: Fraud Detection API
Scenario: Delete Transaction with Valid Input
Given a transaction exists with ID "555"
When I send a DELETE request to "/api/fraud-detection/555"
Then the response status should be 200
And the response should contain "message"
And the message should be "Transaction deleted successfully"