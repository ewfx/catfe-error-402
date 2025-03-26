Feature: Fraud Detection API
Scenario: Create a Transaction with Invalid Data
Given a transaction with
| transaction_id | user_id    | amount  | currency | location  | merchant_id  | timestamp           | ip_address     |
| 555            | user123    | abc     | INR      | Mumbai     | merchantABC  | 2025-03-23T10:00:00 | 192.168.1.10   |
When I send a POST request to "/api/fraud-detection/"
Then the response status code should be 400
And the response body should contain "message" with value "Invalid request"