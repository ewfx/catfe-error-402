Feature: Fraud Detection API
Scenario: Create a transaction with ID 555
Given a transaction with
| transaction_id | user_id    | amount  | currency | location  | merchant_id  | timestamp           | ip_address     |
| 555            | user123    | 60000   | INR      | Mumbai     | merchantABC  | 2025-03-23T10:00:00 | 192.168.1.10   |

After