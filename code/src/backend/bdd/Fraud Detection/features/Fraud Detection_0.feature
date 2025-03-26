Feature: Fraud Detection API
Scenario: Create a Transaction with Valid Input
Given a transaction with
| transaction_id | user_id    | amount  | currency | location  | merchant_id  | timestamp           | ip_address     |
| 555            | user123    | 60000   | INR      | Mumbai     | merchantABC  | 2025-03-23T10:00:00 | 192.168.1.10   |
When I send a POST request to "/api/fraud-detection/"
Then the response status should be 200
And the response should contain "message", "transaction_id", "fraud_status", "fraud_score", and "alerts"
And the fraud status should be "Fraudulent"
And the fraud score should be greater than 70