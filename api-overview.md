# Kasisto Enterprise API Overview
Version 1.3 Beta 7

- [Authentication](#authentication)
- [Authorization](#authorization)
- [Schema](#schema)
- [Customer Methods](#customer-methods)
  * [/token](#token)
  * [/validate_otp](#validate-otp)
  * [/customer](#customer)
- [Accounts Methods](#accounts-methods)
  * [/accounts](#accounts)
- [Transactions Methods](#transactions-methods)
  * [/transactions](#transactions)
  * [/categories](#categories)
  * [/merchants](#merchants)
- [Transfers Methods](#transfers-methods)
  * [/transfer](#transfer)
- [Payments Methods](#payments-methods)
  * [/payment](#payment)
  * [/payees](#payees)
- [Bank Locations Methods](#bank-locations-methods)
  * [/bank_locations](#bank-locations)
- [Offers Methods](#offers-methods)
  * [/offers](#offers) 
- [Customer Action Methods](#customer-action-methods)
  * [/customer_action](#customer-action)
- [Interaction Methods](#interaction-methods)
  * [/interaction](#interaction)


## Authentication
The Kasisto API requires all requests to include a secret key header value used for request authentication.  Kasisto will include the secret key header in each request from our servers. API implementations must validate the secret is correct.
Server implementations should return a 401 HTTP status code response if authentication fails.

## Authorization
The Kasisto API allows requests to include a user authorization token header value.  This token should be validated on the server implementation to match the provided user_id value and that is has the necessary privileges to access the requested information.
Server implementations should return a 403 HTTP status code response if authorization fails.

## Tracking
The Kasisto API requests include a unique request identifier. This identifier is provided as a request_id field in the HTTP Request header. This request_id can be used to track the requests when investigating execution logs.

## Schema
All API access must be over HTTPS.  All data is sent and received as JSON.
Schema definitions are described [here](#schema-definitions).

## Exception handling
All the service in the Kasisto API should follow the same exception handling mechanism.

1) When the customer is authenticated, KAI receives a token from the Bank. (Please check the KAI Conversational API specs for details on the available login flows)
<br>Once KAI has a token for a customer, it will provide it in the HTTP headers fields of the request.<br>The Bank's services are in charge of verifying the access rights before returning the data.

2) When a service executes successfully, it should return a HTTP status 200.

3) When an error occurs, the server should return a different HTTP status code depending on the type of the error and the response should follow the [error_response](#error_response) format.

| Status | Description | Trigger | 
| ------ | ----------- | ----------- | 
| 401 | Authentication Failed | The backend service failed to authenticate the user.<br>This error can occur:<br>- when the token provided by KAI is invalid or missing.<br>- (Only for [/token](#token)) when the parameter sent by KAI to create the session are wrong. | 
| 403 | Access Denied |  The token provided by KAI is invalid or it expired.<br>KAI should obtain another token before retrying the call. |
| 450 | One-Time Password is required | The user session security needs to be elevated to proceed with the request.<br>KAI should ask for an OTP from the user and validate it before retying the call.  |
| 451 | Invalid One-Time Password<br>(Only for [/validate_otp](#validate-otp)) | The OTP provided by the customer is invalid.<br>KAI should ask him to enter the OTP again then retry. |
| 452 | Expired One-Time Password<br>Only for [/validate_otp](#validate-otp)) | The OTP provided by the customer expired.<br>KAI will terminate the intent flow and inform the customer that the request has been cancelled. |
| 453 | Too Many One-Time Password Failures<br>(Only for [/validate_otp](#validate-otp)) | The customer failed to send the correct OTP multiple times in a row.<br>KAI will terminate the intent flow and inform the customer that the request has been cancelled.  |
| 500 | Server Error | A server error occurred when processing the request. <br>For functional errors, the server can return a "display_message_id" in the [error_response](#error_response).<br>KAI will use this "display_message_id" to lookup the message to display to the customer in its message library.<br>If no "display_message_id" is returned KAI will use a default error message. |
| 501 | Not Implemented | This operation is not implemented. |

4) When a One-Time Password is required, additional details on the OTP can be provided in the field "otp_details" of the [error_response](#error_response).

### Customer Methods

#### Token

```
POST /token
```

Obtains authentication tokens for the customer.

This service is used for the Authentication pass-through mechanism. (Please check the KAI Conversational API specs for details on this login flow)

##### Request Parameters

| Parameter | Location |
| --------- | -------- |
| secret | header |
| locale | header |
| Date | header |
| request_id | header |
| [token_credentials](#token_credentials) | body |

##### Responses

| Status | Description | Schema |
| ------ | ----------- | ------ |
| 200 | token response | [token_response](#token_response) |
| 401 | Authentication Failed | [error_response](#error_response) |
| 403 | Access Denied | [error_response](#error_response) |
| 500 | Server Error | [error_response](#error_response) |
| 501 | Not Implemented | [error_response](#error_response) |

##### Sample Request / Response

```http
POST /token HTTP/1.1
Content-Type: application/json
Accept: application/json
secret: string
locale: string
Date: "Tue, 01 Jan 2017 00:00:00 GMT"
request_id: string
```
```json
{
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
token: string (optional)
```
```json
{
    "user_id": "string", 
    "token": "string",
    "refresh_token" : "string",
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ]
}
```

##### Notes:

The ```/token``` operation should return at least 1 token. I.e. ```token``` and ```refresh_token``` cannot both be blank.

#### Validate OTP

```
POST /validate_otp
```

This service validates a One-Time Password and returns a new user token

##### Request Parameters

| Parameter | Location |
| --------- | -------- |
| secret | header |
| token | header |
| locale | header |
| Date | header |
| request_id | header |
| [validate_otp_request](#validate_otp_request) | body |

##### Responses

| Status | Description | Schema |
| ------ | ----------- | ------ |
| 200 | token response | [token_response](#token_response) |
| 401 | Authentication Failed | [error_response](#error_response) |
| 403 | Access Denied | [error_response](#error_response) |
| 451 | Invalid One-Time Password | [error_response](#error_response) |
| 452 | Expired One-Time Password | [error_response](#error_response) |
| 453 | Too Many One-Time Password Failures | [error_response](#error_response) |
| 500 | Server Error | [error_response](#error_response) |
| 501 | Not Implemented | [error_response](#error_response) |

##### Sample Request / Response

```http
POST /validate_otp HTTP/1.1
Content-Type: application/json
Accept: application/json
secret: string
token: string
locale: string
Date: "Tue, 01 Jan 2017 00:00:00 GMT"
request_id: string
```
```json
{
    "user_id": "string", 
    "otp": "string",
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ]
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
token: string (optional)
```
```json
{
    "user_id": "string", 
    "token": "string",
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ]
}
```

##### Notes:

If the OTP provided by the customer is invalid, the server can return the following errors:
1) HTTP Status 451 - The OTP provided by the customer is invalid.<br>KAI should ask him to enter the OTP again then retry.
2) HTTP Status 452 - The OTP provided by the customer expired.<br>KAI will terminate the intent flow and inform the customer that the request has been cancelled.
3) HTTP Status 453 - The customer failed to send the correct OTP multiple times in a row.<br>KAI will terminate the intent flow and inform the customer that the request has been cancelled.

#### Customer

```
POST /customer
```

Gets the customer details. 

##### Request Parameters

| Parameter | Location |
| --------- | -------- |
| secret | header |
| token | header |
| locale | header |
| Date | header |
| request_id | header |
| [customer_request](#customer_request) | body |

##### Responses

| Status | Description | Schema |
| ------ | ----------- | ------ |
| 200 | customer response | [customer](#customer) |
| 401 | Authentication Failed | [error_response](#error_response) |
| 403 | Access Denied | [error_response](#error_response) |
| 450 | One-Time Password is required | [error_response](#error_response) |
| 500 | Server Error | [error_response](#error_response) |
| 501 | Not Implemented | [error_response](#error_response) |

##### Sample Request / Response

```http
POST /customer HTTP/1.1
Content-Type: application/json
Accept: application/json
secret: string
token: string
locale: string
Date: "Tue, 01 Jan 2017 00:00:00 GMT"
request_id: string
```
```json
{
    "user_id": "string", 
    "otp": "string", 
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ]
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
token: string (optional)
```
```json
{
    "user_id": "string",
    "full_name": "string", 
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "mobile_number": "string", 
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

##### Notes:

1) This service is called to retrieve the user_id of the customer and other useful customer information.

2) The user_id is mandatory in the service response as this field is used by KAI to identify unique customers.



### Accounts Methods

#### Accounts

```
POST /accounts
```

Gets the list of all the customer's accounts.

##### Request Parameters

| Parameter | Location |
| --------- | -------- |
| secret | header |
| token | header |
| locale | header |
| Date | header |
| request_id | header |
| [accounts_request](#accounts_request) | body |

##### Responses

| Status | Description | Schema |
| ------ | ----------- | ------ |
| 200 | accounts response | Array of [account](#account) |
| 401 | Authentication Failed | [error_response](#error_response) |
| 403 | Access Denied | [error_response](#error_response) |
| 450 | One-Time Password is required | [error_response](#error_response) |
| 500 | Server Error | [error_response](#error_response) |
| 501 | Not Implemented | [error_response](#error_response) |

##### Sample Request / Response

```http
POST /accounts HTTP/1.1
Content-Type: application/json
Accept: application/json
secret: string
token: string
locale: string
Date: "Tue, 01 Jan 2017 00:00:00 GMT"
request_id: string
```
```json
{
    "user_id": "string", 
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ]
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
token: string (optional)
```
```json
[{
    "account_id": "string",
    "account_type": [
        "cd", 
        "checking", 
        "credit_card", 
        "heloc", 
        "ira", 
        "investment", 
        "loc", 
        "loan", 
        "money_market", 
        "mortgage", 
        "overdraft_protection", 
        "sloc", 
        "savings", 
        "wire", 
        "p2p_payment"
    ], 
    "account_number": "string",
    "account_name": "string",
    "account_nickname": "string",
    "account_status": [
        "active", 
        "inactive"
    ], 
    "account_image": "string",
    "current_balance": 0.0, 
    "available_balance": 0.0, 
    "fcy_currency_code": "string",
    "fcy_current_balance": 0.0, 
    "fcy_available_balance": 0.0, 
    "credit_limit": 0.0, 
    "interest_rate": 0.0, 
    "available_credit": 0.0, 
    "statement_date": "2016-01-30", 
    "payment_due_amount": 0.0, 
    "payment_due_date": "2016-01-30",
    "minimum_payment_due_amount": 0.0, 
    "reward_points": 0,
    "reward_miles": 0,
    "reward_cashback": 0.0, 
    "can_transfer_to": true, 
    "can_transfer_from": true, 
    "can_pay_payee": true, 
    "can_waive_fee": true, 
    "expiration_date": "2016-01-30",
    "available_cash_advance_limit": 0.0, 
    "original_tenor": 0,
    "original_tenor_unit": [
        "year", 
        "month", 
        "day"
    ], 
    "maturity_date": "2016-01-30", 
    "annual_fee": 0.0, 
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}]
```

##### Notes:
1) The field "account_type" in response should be one of the following:
    "cd","checking","credit_card","heloc","ira","investment","loc","loan","money_market","mortgage","overdraft_protection”,
    "sloc","savings","wire".


2) The "account_number" of the account may optionally be masked. However, the last unique N digits in the account numbers must be provided. E.g. A credit card account number of "4515874554548888" can be returned as "8888" or "xxxxxxxxxxxx8888"    

3) The field "account_status" in response should be one of the following: "active","inactive".
Only the Credit Cards with an "inactive" status are eligible for the Credit Card Activation intent.

4) The field "account_image" in response should contain the full http url to the account image.
All images should be hosted on a webserver. KAI doesn't provide any image hosting service.
```json
"account_image": "https://www.my_bank_images_server.com/image/product_type_a.png"
```

5) The field "payment_due_date" and "statement_date" in the response should be in "yyyy-MM-dd” Date format.

6) If there is no meta then pass empty array.

7) As a guidance, we show the supported features per account type in the table below.
The mapping can change from Bank to Bank and is to be agreed with Kasisto prior to implementation : 

| Feature | Certificate of deposit | Checking | Credit Card | Loan | Mortgage | Savings |
| --------- | :-------------: | :-------------: | :-------------: | :-------------: | :-------------: | :-------------: |
| account_id | x | x | x | x | x | x |
| account_type | cd |checking | credit_card | loan | mortgage |savings |
| account_number | x | x | x | x | x | x |
| account_name | x | x | x | x | x | x |
| account_nickname | x | x | x | x | x | x |
| account_status | x | x | x | x | x | x |   
| current_balance  | x | x | x | x | x | x |
| available_balance  | x | x | x | x | x | x |
| fcy_currency_code  |  | x |  |  |  | x |
| fcy_current_balance |  | x |  |  |  | x |
| fcy_available_balance |  | x |  |  |  | x |
| credit_limit |  | x | x |  |  | x |
| interest_rate | x | x | x | x | x | x |
| available_credit |  |  | x |  |  |  |
| statement_date | x | x | x | x | x | x |
| payment_due_amount |  |  | x | x | x |  |
| payment_due_date |  |  | x | x | x |  |
| minimum_payment_due_amount |  |  | x | x | x |  |
| reward_points |  |  | x |  |  |  |
| reward_miles |  |  | x |  |  |  |
| reward_cashback |  |  | x |  |  |  |
| can_transfer_to | x | x | x | x | x | x |
| can_transfer_from |  | x | x |  |  | x |
| can_pay_payee |  | x | x |  |  | x |
| can_waive_fee | x | x | x | x | x | x |
| annual_fee |  |  | x |  |  |  |
| expiration_date |  |  | x |  |  |  |
| available_cash_advance_limit |  |  | x |  |  |  |
| original_tenor | x |  |  | x | x |  |
| original_tenor_unit | x |  |  | x | x |  |
| maturity_date | x |  |  | x | x |  |

8) For Accounts in foreign currency:

    a) The fields "current_balance" and "available_balance" should be sent as amount equivalent in the default currency.

    b) The field "fcy_currency_code" should contain the currency code of the Account (JPY, EUR, etc.)

    c) The fields "fcy_current_balance" and "fcy_available_balance" should hold the foreign currency amounts

9) For Accounts with multiple foreign currencies, KAI expects multiple Account objects in the response: One account per foreign currency.

10) Intent enabling fields:

| Field | Intent | Description |
| --------- | -------- | -------- |
| can_transfer_to | Transfer | Indicates that this Account can be used as destination for the transfer. If the acconut is a credit card, the flow triggered is a pay credit card bill |
| can_transfer_from | Transfer | Indicates that this Account can be used as source for transfer |
| can_pay_payee | Pay2Person | Indicates that this Account can be used for a payment to Payee |
| can_waive_fee | FeeWaiver | Indicates that this Account is eligible to fee waiver |

11) The original tenor of an account is controlled by 2 attributes. The "original_tenor", which is an integer and the "original_tenor_unit" which is a string from the enum of ["year", "month", "day"]. E.g. a tenor of 3 months is represented as:

```json
{
    "original_tenor" : 3,
    "original_tenor_unit" : "month"
}
```

### Transactions Methods

#### Transactions

```
POST /transactions
```

Searches the customer's transactions.

##### Request Parameters

| Parameter | Location |
| --------- | -------- |
| secret | header |
| token | header |
| locale | header |
| Date | header |
| request_id | header |
| [transaction_criteria](#transaction_criteria) | body |

##### Responses

| Status | Description | Schema |
| ------ | ----------- | ------ |
| 200 | transactions | Array of [transaction](#transaction) |
| 401 | Authentication Failed | [error_response](#error_response) |
| 403 | Access Denied | [error_response](#error_response) |
| 450 | One-Time Password is required | [error_response](#error_response) |
| 500 | Server Error | [error_response](#error_response) |
| 501 | Not Implemented | [error_response](#error_response) |

##### Sample Request / Response

```http
POST /transactions HTTP/1.1
Content-Type: application/json
Accept: application/json
secret: string
token: string
locale: string
Date: "Tue, 01 Jan 2017 00:00:00 GMT"
request_id: string
```
```json
{
    "user_id": "string",
    "account_ids": [
        "string"
    ],
    "limit": 0, 
    "start_date": "2016-01-30T00:00:00.000+0000", 
    "end_date": "2016-01-30T00:00:00.000+0000"
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
token: string (optional)
```
```json
[{
    "account_id": "string",
    "transaction_id": "string", 
    "title": "string",
    "description": "string", 
    "transaction_type": [
        "credit", 
        "debit"
    ], 
    "amount": 0.0, 
    "currency_code": "string", 
    "categories": [
        "string"
    ],
    "merchant": "string",
    "payee": "string",
    "location": {
        "address": "string",
        "city": "string",
        "state": "string", 
        "zip": "string",
        "country": "string",
        "coordinates": {
          "lat": 0.0,
          "long": 0.0
        }
    },
    "status": [
        "posted", 
        "pending", 
        "cancelled"
    ], 
    "check_number": 0, 
    "transaction_date": "2016-01-30T00:00:00.000+0000", 
    "post_date": "2016-01-30T00:00:00.000+0000", 
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}]
```

##### Notes:

1) The API doesn't filter by category, payee or merchant. Instead, we rely on KAI for the filtering.

2) The field "limit" in the request can be used to limit the maximum number of transactions returned by the service.

    a) When the limit is not set or equals 0, the service should return all the transactions that match the search filter

    b) When the limit is set to N above 0, the service should return only N most recent transactions. 

3) The field "transaction_type" in response should be one of the following:
   "credit", "debit”.

4) The field "amount" should always have a positive value. 

5) The field "status" in response should be one of the following:
   "posted", "pending", "cancelled".

6) The fields "transaction_date" and "post_date" in response should be in ISO-8601 format "yyyy-MM-dd’T’HH:mm:ssZ” Date format.

7) If there is no meta or categories then pass empty array.

#### Categories

```
POST /categories
```

Get transaction categories

##### Request Parameters

| Parameter | Location |
| --------- | -------- |
| secret | header |
| token | header |
| locale | header |
| Date | header |
| request_id | header |
| [categories_request](#categories_request) | body |

##### Responses

| Status | Description | Schema |
| ------ | ----------- | ------ |
| 200 | categories response | Array of [category](#category) |
| 401 | Authentication Failed | [error_response](#error_response) |
| 403 | Access Denied | [error_response](#error_response) |
| 500 | Server Error | [error_response](#error_response) |
| 501 | Not Implemented | [error_response](#error_response) |

##### Sample Request / Response

```http
POST /categories HTTP/1.1
Content-Type: application/json
Accept: application/json
secret: string
token: string
locale: string
Date: "Tue, 01 Jan 2017 00:00:00 GMT"
request_id: string
```
```json
{
    "user_id": "string", 
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ]
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
token: string (optional)
```
```json
[{
    "category_id": "string",
    "name": "string",
    "alias": [
        "string"
    ],
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}]
```

#### Merchants

```
POST /merchants
```

Gets the list of merchants for this user.

##### Request Parameters

| Parameter | Location |
| --------- | -------- |
| secret | header |
| token | header |
| locale | header |
| Date | header |
| request_id | header |
| [merchants_request](#merchants_request) | body |

##### Responses

| Status | Description | Schema |
| ------ | ----------- | ------ |
| 200 | merchants response | Array of [merchant](#merchant) |
| 401 | Authentication Failed | [error_response](#error_response) |
| 403 | Access Denied | [error_response](#error_response) |
| 500 | Server Error | [error_response](#error_response) |
| 501 | Not Implemented | [error_response](#error_response) |

##### Sample Request / Response

```http
POST /merchants HTTP/1.1
Content-Type: application/json
Accept: application/json
secret: string
token: string
locale: string
Date: "Tue, 01 Jan 2017 00:00:00 GMT"
request_id: string
```
```json
{
    "user_id": "string", 
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ]
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
token: string (optional)
```
```json
[{
    "merchant_id": "string",
    "name": "string",
    "alias": [
        "string"
    ],
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}]
```


### Transfers Methods

#### Transfer

```
POST /transfer
```

Transfers funds between two accounts of a customer. 

This service can be used to transfer money from one account to another or to execute a payment to a credit card.

##### Request Parameters

| Parameter | Location |
| --------- | -------- |
| secret | header |
| token | header |
| locale | header |
| Date | header |
| request_id | header |
| [transfer_request](#transfer_request) | body |

##### Responses

| Status | Description | Schema |
| ------ | ----------- | ------ |
| 200 | transfer response | [transfer](#transfer) |
| 401 | Authentication Failed | [error_response](#error_response) |
| 403 | Access Denied | [error_response](#error_response) |
| 450 | One-Time Password is required | [error_response](#error_response) |
| 500 | Server Error | [error_response](#error_response) |
| 501 | Not Implemented | [error_response](#error_response) |

##### Sample Request / Response

```http
POST /transfer HTTP/1.1
Content-Type: application/json
Accept: application/json
secret: string
token: string
locale: string
Date: "Tue, 01 Jan 2017 00:00:00 GMT"
request_id: string
```
```json
{
    "user_id": "string", 
    "source_account_id": "string",
    "dest_account_id": "string", 
    "amount": 0.0, 
    "currency_code": "string", 
    "date": "2016-01-30T00:00:00.000+0000", 
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
token: string (optional)
```
```json
{
    "transfer_id": "string",
    "reference_number": "string",
    "status": [
        "processed", 
        "pending", 
        "cancelled", 
        "failed"
    ], 
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

##### Notes:

1) Only the customer's Accounts returned by [/accounts](#accounts) can be eligible.

    a) Accounts with the flag "can_transfer_from" set to true can be selected as a source.

    b) Accounts with the flag "can_transfer_to" set to true can be selected as a destination.

2) The field "transfer_id" in the response is the internal Bank id of the request for internal tracking purpose.

3) The field "reference_number" in the response is the reference number to communicate to the customer for tracking purpose.

4) The field "status" in the response can be used to inform KAI on the status of the action. The possible values are:
    "processed", "pending", "cancelled", "failed".


### Payments Methods

#### Payment

```
POST /payment
```

Pays funds to a payee.

##### Request Parameters

| Parameter | Location |
| --------- | -------- |
| secret | header |
| token | header |
| locale | header |
| Date | header |
| request_id | header |
| [payment_request](#payment_request) | body |

##### Responses

| Status | Description | Schema |
| ------ | ----------- | ------ |
| 200 | payment response | [payment](#payment) |
| 401 | Authentication Failed | [error_response](#error_response) |
| 403 | Access Denied | [error_response](#error_response) |
| 450 | One-Time Password is required | [error_response](#error_response) |
| 500 | Server Error | [error_response](#error_response) |
| 501 | Not Implemented | [error_response](#error_response) |

##### Sample Request / Response

```http
POST /payment HTTP/1.1
Content-Type: application/json
Accept: application/json
secret: string
token: string
locale: string
Date: "Tue, 01 Jan 2017 00:00:00 GMT"
request_id: string
```
```json
{
    "user_id": "string", 
    "source_account_id": "string",
    "payee_id": "string", 
    "amount": 0.0, 
    "currency_code": "string", 
    "date": "2016-01-30T00:00:00.000+0000", 
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
token: string (optional)
```
```json
{
    "payment_id": "string",
    "reference_number": "string",
    "status": [
        "processed", 
        "pending", 
        "cancelled", 
        "failed"
    ], 
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

##### Notes:

1) Only the Accounts with the flag "can_pay_payee" set to true can be selected as a source.

2) Only payees returned by [/payees](#payees) are eligible. 

3) The field "payment_id" in the response is the internal Bank id of the request for internal tracking purpose.

4) The field "reference_number" in the response is the reference number to communicate to the customer for tracking purpose.

5) The field "status" in the response can be used to inform KAI on the status of the action. The possible values are:
    "processed", "pending", "cancelled", "failed".

#### Payees

```
POST /payees
```

Gets the list of payees for a user.

##### Request Parameters

| Parameter | Location |
| --------- | -------- |
| secret | header |
| token | header |
| locale | header |
| Date | header |
| request_id | header |
| [payees_request](#payees_request) | body |

##### Responses

| Status | Description | Schema |
| ------ | ----------- | ------ |
| 200 | payees response | Array of [payee](#payee) |
| 401 | Authentication Failed | [error_response](#error_response) |
| 403 | Access Denied | [error_response](#error_response) |
| 500 | Server Error | [error_response](#error_response) |
| 501 | Not Implemented | [error_response](#error_response) |

##### Sample Request / Response

```http
POST /payees HTTP/1.1
Content-Type: application/json
Accept: application/json
secret: string
token: string
locale: string
Date: "Tue, 01 Jan 2017 00:00:00 GMT"
request_id: string
```
```json
{
    "user_id": "string", 
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ]
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
token: string (optional)
```
```json
[{
    "payee_id": "string",
    "name": "string",
    "alias": [
        "string"
    ],
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ], 
    "category": [
        "payee", 
        "biller"
    ]
}]
```

##### Notes:

1) The "category" field is a string enum with expected values ```["payee","biller"]```.

### Bank Locations Methods

#### Bank Locations

```
POST /bank_locations
```

Searches for bank locations.

##### Request Parameters

| Parameter | Location |
| --------- | -------- |
| secret | header |
| token | header |
| locale | header |
| Date | header |
| request_id | header |
| [bank_locations_criteria](#bank_locations_criteria) | body |

##### Responses

| Status | Description | Schema |
| ------ | ----------- | ------ |
| 200 | bank_locations | Array of [bank_location](#bank_location) |
| 401 | Authentication Failed | [error_response](#error_response) |
| 403 | Access Denied | [error_response](#error_response) |
| 450 | One-Time Password is required | [error_response](#error_response) |
| 500 | Server Error | [error_response](#error_response) |
| 501 | Not Implemented | [error_response](#error_response) |

##### Sample Request / Response

```http
POST /bank_locations HTTP/1.1
Content-Type: application/json
Accept: application/json
secret: string
token: string (optional)
locale: string
Date: "Tue, 01 Jan 2017 00:00:00 GMT"
request_id: string
```
```json
{
    "user_id": "string",
    "location": {
        "address": "string",
        "city": "string",
        "state": "string", 
        "zip": "string",
        "country": "string", 
        "country": "string",
        "coordinates": {
          "lat": 0.0,
          "long": 0.0
        }
    }
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
token: string (optional)
```
```json
[{
    "location_id": "string",
    "location_type": [
        "atm", 
        "bank"
    ], 
    "location_name": "string",
    "location_url": "string",
    "location": {
        "address": "string",
        "city": "string",
        "state": "string",
        "zip": "string",
        "country": "string",
        "coordinates": {
            "lat": 0.0,
            "long": 0.0
        }
    },
    "phone_number": "string",
    "services": [
        "string"
    ],
    "opening_hours": [
        "string"
    ],
    "opening_days": "string", 
    "languages": [
        "string"
    ]
}]
```

##### Notes:
1) The field "location" can be omitted in the request when KAI searches for all locations.

2) The field "opening_days" in the response should be one of the following: "monday", "tuesday", "wednesday", "thursday, "friday", "saturday", "sunday". It specifies the days of the week where the POI is open. The values should always be in English.

3) The field "opening_hours" contains a text description of the opening hours. The description should be returned in the language matching the request "locale" parameter.

    a) If locale is set to en_XX (en_US, en_HK, en_SG, etc..), the opening hours should be returned in English.

    b) If locale is set to zh_HK, the opening hours should be returned in Cantonese.

```json
"opening_hours": [ 
    "Mon – Fri: 9am to 5pm",
    "Sat 9am to 1pm",
    "public holidays: closed"
]
```

```json
"opening_hours": [ 
    "星期一至星期五: 上午九時至下午五時",
    "星期六上午九時至下午一時"
]
```
### Offers Methods

#### Offers

```
POST /offers
```

Obtain a list of offers that can be redeemed by the user.

##### Request Parameters

| Parameter | Location |
| --------- | -------- |
| secret | header |
| token | header |
| locale | header |
| request_id | header |
| Date | header |
| [offers_request](#offers_request) | body |

##### Responses

| Status | Description | Schema |
| ------ | ----------- | ------ |
| 200 | offers response | Array of [offer](#offer) |
| 401 | Authentication Failed | [error_response](#error_response) |
| 403 | Access Denied | [error_response](#error_response) |
| 500 | Server Error | [error_response](#error_response) |
| 501 | Not Implemented | [error_response](#error_response) |


##### Sample Request / Response

```http
POST /offers HTTP/1.1
Content-Type: application/json
Accept: application/json
secret: string
token: string
locale: string
request_id: string
Date: Tue, 01 Jan 2017 00:00:00 GMT
```
```json
{
    "user_id": "string",
    "location": {
        "address": "string",
        "city": "string",
        "state": "string", 
        "zip": "string",
        "country": "string",
        "coordinates": {
          "lat": 0.0,
          "long": 0.0
        }
    }
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
token: string (optional)
```
```json
[
    {
        "offer_id" : "string",
        "summary" : "string",
        "image_url" : "string",
        "merchant" : "string",
        "location_name" : "string",
        "location_contact_number" : "string",
        "location_email" : "string",
        "offer_url" : "string",
        "location" : {
            "address" : "string",
            "city" : "string",
            "state" : "string",
            "country" :"string",
            "coordinates" : {
                "lat" : 0.0,
                "long" : 0.0
            }
        },
        "categories" : ["string"],
        "start_date" : "2018-01-01",
        "end_date" : "2018-01-01",
        "details" : [
            "string"
        ]
    }
]
```

##### Notes:

1) The `merchant` refers to the name of the company providing the offer. For example, "ABC Restaurant" 

2) The `location_name` is a description of the merchant location. For example, "ABC Restaurant @ Full Win Commercial Center"

3) The `offer_url` is an external webpage identified by the bank to provide detailed information about that particular offer.

4) The text in  `details` should be kept concise to avoid clutter and information overload.

### Customer Action Methods

#### Customer Action

```
POST /customer_action
```

This service is a generic service that allows the customer to submit different type of requests.

##### Request Parameters

| Parameter | Location |
| --------- | -------- |
| secret | header |
| token | header |
| locale | header |
| Date | header |
| request_id | header |
| [customer_action_request](#customer_action_request) | body |

##### Responses

| Status | Description | Schema |
| ------ | ----------- | ------ |
| 200 | Customer action response | [customer_action_response](#customer_action_response) |
| 401 | Authentication Failed | [error_response](#error_response) |
| 403 | Access Denied | [error_response](#error_response) |
| 450 | One-Time Password is required | [error_response](#error_response) |
| 500 | Server Error | [error_response](#error_response) |
| 501 | Not Implemented | [error_response](#error_response) |

##### Sample Request / Response

```http
POST /customer_action HTTP/1.1
Content-Type: application/json
Accept: application/json
secret: string
token: string
locale: string
Date: "Tue, 01 Jan 2017 00:00:00 GMT"
request_id: string
```
```json
{
    "user_id": "string",
    "action": "string",
    "parameters": [
        { 
            "name": "string", 
            "value": "string"
        }
    ]
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
token: string (optional)
```
```json
{
    "reference_id": "string",
    "reference_number": "string",
    "status": [
        "processed", 
        "pending", 
        "cancelled", 
        "failed"
    ], 
    "display_message_id": "string",
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

##### Notes:

1) The list below details the customer action that can be submitted by KAI as part of the Banking Intents.

| Intent | Action name | Parameter name | Parameter description | 
| --------- | -------- | -------- | -------- |
| Credit Card Activation | credit_card_activate | account_id | Id of the credit card to activate |
| Credit Card Fee Waiver | credit_card_waive_fee | account_id | Id of the credit card to waive fees |

2) Depending on the actions, the customer request can be synchronously or asynchronously processed.
The field "status" in the response can be used to inform KAI on the status of the action. The possible values are:
    "processed", "pending", "cancelled", "failed".

3) The field "reference_id" in the response is the internal Bank id of the request for internal tracking purpose.

4) The field "reference_number" in the response is the reference number to communicate to the customer for tracking purpose.

5) The field "display_message_id" in the response can be used to inform KAI to display a specific message to the customer.
KAI will use this "display_message_id" to lookup the message to display to the customer in its message library.
If no "display_message_id" is returned KAI will use a default message.
The list of possible messages should be defined prior to implementation.



### Interaction Methods

#### Interaction

```
POST /interaction
```

This service receives the user interaction transcripts as they occur. (Only available from 2.0.1 onward.)

##### Request Parameters

| Parameter | Location |
| --------- | -------- |
| secret | header |
| locale | header |
| Date | header |
| request_id | header |
| [interaction_request](#interaction_request) | body |

##### Responses

| Status | Description | Schema |
| ------ | ----------- | ------ |
| 200 | The request has succeeded |  |
| 401 | Authentication Failed | [error_response](#error_response) |
| 403 | Access Denied | [error_response](#error_response) |
| 500 | Server Error | [error_response](#error_response) |
| 501 | Not Implemented | [error_response](#error_response) |

##### Sample Request / Response

```http
POST /interaction HTTP/1.1
Content-Type: application/json
Accept: application/json
secret: string
locale: string
Date: "Tue, 01 Jan 2017 00:00:00 GMT"
request_id: string
```
```json
{
    "interaction_type": [
        "USER_INPUT", 
        "PUSH_MESSAGE", 
        "LIVE_CHAT_OPTION_DISPLAYED", 
        "LOGOUT", 
        "ENTER_TOKEN"
    ], 
    "application": {
        "application_id": "string", 
        "locale": "string", 
        "environment": "string", 
        "build_id": "string", 
        "package_id": "string"
    }, 
    "user": {
        "user_id": "string", 
        "session_id": "string"
    }, 
    "platform": {
        "name": "string", 
        "conversation_id": "string", 
        "user_id": "string"
    }, 
    "device": {
        "type": "string", 
        "os": "string", 
        "model": "string", 
        "id": "string"
    }, 
    "segment_names": [
        "string"
    ], 
    "request_text": "string", 
    "response": {
        "message_contents": [
            {
                "type": [
                    "TEXT", 
                    "BUTTON", 
                    "MEDIUM", 
                    "CONTAINER", 
                    "EVENT", 
                    "CARD"
                ], 
                "payload": {}, 
                "segment_name": "string"
            }
        ], 
        "quick_replies": [
            {
                "type": [
                    "TEXT", 
                    "LOCATION"
                ], 
                "payload": "string", 
                "display_text": "string"
            }
        ], 
        "alternative_questions": [
            {
                "question_id": "string", 
                "question": "string"
            }
        ]
    }, 
    "intent": "string", 
    "sub_intent": "string", 
    "elapsed_time": 0, 
    "date": "2016-01-30T00:00:00.000+0000", 
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ] 
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
token: string (optional)
```
```json

```


### Schema Definitions

#### account

```json
{
    "account_id": "string",
    "account_type": [
        "cd", 
        "checking", 
        "credit_card", 
        "heloc", 
        "ira", 
        "investment", 
        "loc", 
        "loan", 
        "money_market", 
        "mortgage", 
        "overdraft_protection", 
        "sloc", 
        "savings", 
        "wire", 
        "p2p_payment"
    ], 
    "account_number": "string",
    "account_name": "string",
    "account_nickname": "string",
    "account_status": [
        "active", 
        "inactive"
    ], 
    "account_image": "string",
    "current_balance": 0.0, 
    "available_balance": 0.0, 
    "fcy_currency_code": "string",
    "fcy_current_balance": 0.0, 
    "fcy_available_balance": 0.0, 
    "credit_limit": 0.0, 
    "interest_rate": 0.0, 
    "available_credit": 0.0, 
    "statement_date": "2016-01-30", 
    "payment_due_amount": 0.0, 
    "payment_due_date": "2016-01-30",
    "minimum_payment_due_amount": 0.0, 
    "reward_points": 0,
    "reward_miles": 0,
    "reward_cashback": 0.0, 
    "can_transfer_to": true, 
    "can_transfer_from": true, 
    "can_pay_payee": true, 
    "can_waive_fee": true, 
    "expiration_date": "2016-01-30", 
    "available_cash_advance_limit": 0.0, 
    "original_tenor": 0, 
    "original_tenor_unit": [
        "year", 
        "month", 
        "day"
    ], 
    "maturity_date": "2016-01-30", 
    "annual_fee": 0.0, 
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

#### accounts_request

```json
{
    "user_id": "string",
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

#### alternative_question

```json
{
    "question_id": "string", 
    "question": "string"
}
```

#### application

```json
{
    "application_id": "string", 
    "locale": "string", 
    "environment": "string", 
    "build_id": "string", 
    "package_id": "string"
}
```

#### bank_location

```json
{
    "location_id": "string",
    "location_type": [
        "atm", 
        "bank"
    ], 
    "location_name": "string",
    "location_url": "string",
    "location": {
        "address": "string",
        "city": "string",
        "state": "string",
        "zip": "string",
        "country": "string",
        "coordinates": {
            "lat": 0.0,
            "long": 0.0
        }
    },
    "phone_number": "string",
    "services": [
        "string"
    ],
    "opening_hours": [
        "string"
    ],
    "opening_days": [
        "string"
    ],
    "languages": [
        "string"
    ]
}
```

#### bank_locations_criteria

```json
{
    "user_id": "string",
    "location": {
        "address": "string",
        "city": "string",
        "state": "string", 
        "zip": "string",
        "country": "string",
        "coordinates": {
          "lat": 0.0,
          "long": 0.0
        }
    }
}
```

#### categories_request

```json
{
    "user_id": "string", 
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ]
}
```

#### category

```json
{
    "category_id": "string",
    "name": "string",
    "alias": [
        "string"
    ],
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

#### coordinates

```json
{
    "lat": 0.0, 
    "long": 0.0
}
```

#### customer

```json
{
    "user_id": "string", 
    "full_name": "string", 
    "first_name": "string",
    "last_name": "string",
    "email": "string", 
    "mobile_number": "string", 
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

#### customer_action_request

```json
{
    "user_id": "string",
    "action": "string",
    "parameters": [
        { 
            "name": "string", 
            "value": "string"
        }
    ]
}
```

#### customer_action_response

```json
{
    "reference_id": "string",
    "reference_number": "string",
    "status": [
        "processed", 
        "pending", 
        "cancelled", 
        "failed"
    ], 
    "display_message_id": "string",
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

#### customer_request

```json
{
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ]
}
```

#### device

```json
{
    "type": "string", 
    "os": "string", 
    "model": "string", 
    "id": "string"
}
```

#### error_response

```json
{
    "message": "string",
    "code": "string",
    "otp_details": "string", 
    "display_message_id": "string", 
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

#### interaction_request

```json
{
    "interaction_type": [
        "USER_INPUT", 
        "PUSH_MESSAGE", 
        "LIVE_CHAT_OPTION_DISPLAYED", 
        "LOGOUT", 
        "ENTER_TOKEN"
    ], 
    "application": {
        "application_id": "string", 
        "locale": "string", 
        "environment": "string", 
        "build_id": "string", 
        "package_id": "string"
    }, 
    "user": {
        "user_id": "string", 
        "session_id": "string"
    }, 
    "platform": {
        "name": "string", 
        "conversation_id": "string", 
        "user_id": "string"
    }, 
    "device": {
        "type": "string", 
        "os": "string", 
        "model": "string", 
        "id": "string"
    }, 
    "segment_names": [
        "string"
    ], 
    "request_text": "string", 
    "response": {
        "message_contents": [
            {
                "type": [
                    "TEXT", 
                    "BUTTON", 
                    "MEDIUM", 
                    "CONTAINER", 
                    "EVENT", 
                    "CARD"
                ], 
                "payload": {}, 
                "segment_name": "string"
            }
        ], 
        "quick_replies": [
            {
                "type": [
                    "TEXT", 
                    "LOCATION"
                ], 
                "payload": "string", 
                "display_text": "string"
            }
        ], 
        "alternative_questions": [
            {
                "question_id": "string", 
                "question": "string"
            }
        ]
    }, 
    "intent": "string", 
    "sub_intent": "string", 
    "elapsed_time": 0, 
    "date": "2016-01-30T00:00:00.000+0000", 
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ]
}
```

#### interaction_request_response

```json
{
    "message_contents": [
        {
            "type": [
                "TEXT", 
                "BUTTON", 
                "MEDIUM", 
                "CONTAINER", 
                "EVENT", 
                "CARD"
            ], 
            "payload": {}, 
            "segment_name": "string"
        }
    ], 
    "quick_replies": [
        {
            "type": [
                "TEXT", 
                "LOCATION"
            ], 
            "payload": "string", 
            "display_text": "string"
        }
    ], 
    "alternative_questions": [
        {
            "question_id": "string", 
            "question": "string"
        }
    ]
}
```

#### location

```json
{
    "address": "string", 
    "city": "string", 
    "state": "string", 
    "zip": "string", 
    "country": "string", 
    "coordinates": {
        "lat": 0.0, 
        "long": 0.0
    }
}
```

#### merchant

```json
{
    "merchant_id": "string",
    "name": "string",
    "alias": [
        "string"
    ],
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

#### merchants_request

```json
{
    "user_id": "string", 
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ]
}
```

#### message_content

```json
{
    "type": [
        "TEXT", 
        "BUTTON", 
        "MEDIUM", 
        "CONTAINER", 
        "EVENT", 
        "CARD"
    ], 
    "payload": {}, 
    "segment_name": "string"
}
```

#### name_value_pair

```json
{
    "name": "string", 
    "value": "string"
}
```

#### payee

```json
{
    "payee_id": "string",
    "name": "string",
    "alias": [
        "string"
    ],
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ], 
    "category": [
        "payee", 
        "biller"
    ]
}
```

#### payees_request

```json
{
    "user_id": "string", 
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ]
}
```

#### payment

```json
{
    "payment_id": "string",
    "reference_number": "string",
    "status": [
        "processed", 
        "pending", 
        "cancelled", 
        "failed"
    ], 
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

#### payment_request

```json
{
    "user_id": "string", 
    "source_account_id": "string",
    "payee_id": "string", 
    "amount": 0.0, 
    "currency_code": "string", 
    "date": "2016-01-30T00:00:00.000+0000", 
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

#### platform

```json
{
    "name": "string", 
    "conversation_id": "string", 
    "user_id": "string"
}
```

#### quick_reply

```json
{
    "type": [
        "TEXT", 
        "LOCATION"
    ], 
    "payload": "string", 
    "display_text": "string"
}
```

#### token_credentials

```json
{
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ]
}
```

#### token_response

```json
{
    "user_id": "string", 
    "token": "string",
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ]
}
```

#### transaction

```json
{
    "account_id": "string",
    "transaction_id": "string", 
    "title": "string",
    "description": "string", 
    "transaction_type": [
        "credit", 
        "debit"
    ], 
    "amount": 0.0, 
    "currency_code": "string", 
    "categories": [
        "string"
    ],
    "merchant": "string",
    "payee": "string",
    "location": {
        "address": "string",
        "city": "string",
        "state": "string", 
        "zip": "string",
        "country": "string",
        "coordinates": {
          "lat": 0.0,
          "long": 0.0
        }
    }, 
    "status": [
        "posted", 
        "pending", 
        "cancelled"
    ], 
    "check_number": 0, 
    "transaction_date": "2016-01-30T00:00:00.000+0000", 
    "post_date": "2016-01-30T00:00:00.000+0000", 
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

#### transaction_criteria

```json
{
    "user_id": "string",
    "account_ids": [
        "string"
    ],
    "limit": 0, 
    "start_date": "2016-01-30T00:00:00.000+0000", 
    "end_date": "2016-01-30T00:00:00.000+0000"
}
```

#### transfer

```json
{
    "transfer_id": "string",
    "reference_number": "string",
    "status": [
        "processed", 
        "pending", 
        "cancelled", 
        "failed"
    ], 
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

#### transfer_request

```json
{
    "user_id": "string", 
    "source_account_id": "string",
    "dest_account_id": "string", 
    "amount": 0.0, 
    "currency_code": "string", 
    "date": "2016-01-30T00:00:00.000+0000", 
    "meta": [
        {
            "name": "string",
            "value": "string"
        }
    ]
}
```

#### user

```json
{
    "user_id": "string", 
    "session_id": "string"
}
```

#### validate_otp_request

```json
{
    "user_id": "string", 
    "otp": "string",
    "meta": [
        {
            "name": "string", 
            "value": "string"
        }
    ]
}
```

#### offers_request

```json
{
    "user_id": "string",
    "location": {
        "address": "string",
        "city": "string",
        "state": "string", 
        "zip": "string",
        "country": "string",
        "coordinates": {
          "lat": 0.0,
          "long": 0.0
        }
    }
}
```

#### offer

```json
{
    "offer_id" : "string",
    "summary" : "string",
    "image_url" : "string",
    "merchant" : "string",
    "location_name" : "string",
    "location_contact_number" : "string",
    "location_email" : "string",
    "offer_url" : "string",
    "location" : {
        "address" : "string",
        "city" : "string",
        "state" : "string",
        "country" :"string",
        "coordinates" : {
            "lat" : 0.0,
            "long" : 0.0
        }
    },
    "categories" : ["string"],
    "start_date" : "2018-01-01",
    "end_date" : "2018-01-01",
    "details" : [
        "string"
    ]
}
```