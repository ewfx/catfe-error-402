Feature: Fraud Detection API
Scenario: Get Transaction by ID with Valid Input
Given a transaction exists with ID "555"
When I send a GET request to "/api/fraud-detection/555"
Then the response status should be 200
And the response should contain "transaction_id", "user_id", "amount", "currency", "location", "merchant_id", "timestamp", "ip_address", "fraud_status", "fraud_score", and "alerts"
And the fraud status should be "Fraudulent"
And the fraud score should be greater than 70