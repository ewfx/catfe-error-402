Feature: Fraud Detection API
Scenario: Get All Transactions
When I send a GET request to "/api/fraud-detection/"
Then the response status should be 200
And the response should contain a list of transactions with "transaction_id", "user_id", "amount", "currency", "location", "merchant_id", "timestamp", "ip_address", "fraud_status", "fraud_score", and "alerts"