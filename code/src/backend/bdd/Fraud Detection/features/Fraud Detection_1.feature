Feature: Fraud Detection API
Scenario: Create a Transaction with Invalid Input - Missing Field
Given a transaction with
| transaction_id | user_id    | amount  | location  | merchant_id  | timestamp           | ip_address     |
| 555            | user123    | 60000   | Mumbai     | merchantABC  | 2025-03-23T10:00:00 | 192.168.1.10   |
When I send a POST request to "/api/fraud-detection/"
Then the response status should be 400
And the response should contain "message"
And the message should contain "missing required field"