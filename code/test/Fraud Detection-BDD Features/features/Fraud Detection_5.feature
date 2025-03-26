Feature: Fraud Detection API
Scenario: Delete a Transaction with Valid ID
Given a transaction with
| transaction_id | user_id    | amount  | currency | location  | merchant_id  | timestamp           | ip_address     |
| 555            | user123    | 60000   | INR      | Mumbai     | merchantABC  | 2025-03-23T10:00:00 | 192.168.1.10   |
When I send a DELETE request to "/api/fraud-detection/555"
Then the response status code should be 200
And the response body should contain "message" with value "Transaction deleted successfully"