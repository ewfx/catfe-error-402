Feature: Fraud Detection API
Scenario: Create a transaction and then delete it
Given a transaction with
| transaction_id | user_id    | amount  | currency | location  | merchant_id  | timestamp           | ip_address     |
| 555            | user123    | 60000.0 | INR      | Mumbai     | merchantABC  | 2025-03-23T10:00:00 | 192.168.1.10   |
When I send a POST request to "/api/fraud-detection/"
Then the response status code should be 200
And the response body should contain "message" with value "Transaction created successfully"
When I send a DELETE request to "/api/fraud-detection/555"
Then the response status code should be 200
And the response body should contain "message" with value "Transaction deleted successfully"
And the transaction with ID "555" should no longer exist