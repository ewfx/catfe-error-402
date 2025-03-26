Feature: Fraud Detection API
Scenario: Get a Transaction by ID with Valid Data
Given a transaction with
| transaction_id | user_id    | amount  | currency | location  | merchant_id  | timestamp           | ip_address     |
| 555            | user123    | 60000   | INR      | Mumbai     | merchantABC  | 2025-03-23T10:00:00 | 192.168.1.10   |
When I send a GET request to "/api/fraud-detection/555"
Then the response status code should be 200
And the response body should contain "transaction_id" with value "555"
And the response body should contain "fraud_status" with value "Fraudulent"
And the response body should contain "fraud_score" with value greater than 50
And the response body should contain "alerts" with at least one alert