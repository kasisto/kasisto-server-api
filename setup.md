# Setting up an Enterprise API

# WARNING: This page is no longer maintained. Check <a href="https://docs.kasisto.com/">https://docs.kasisto.com/</a> for the latest version of the document. 

## What is the Enterprise API?

The Enterprise API is a specification that Kasisto uses to access bank services
in order to provide a conversational API over top of it. It is the contract
between Kasisto and the bank that says:

> If you provide “X” services in this particular way,
> we can provide “Y” intents over top of those services.


## Writing an API Server

Writing an Enterprise API requires following the provided [**Open API
Specification**](https://github.com/OAI/OpenAPI-Specification) (previously known
as Swagger Specification). Writing an API that matches the specification can be
done quickly through code generation tools like [**Swagger
Codegen**](https://github.com/swagger-api/swagger-codegen), or a bare HTTP
server that provides the endpoints that are needed for the intents desired. The
time it takes to create the server depends on the intents that you are
interested in having. You can have the first iteration of a server working by
creating simple stubs of the endpoints, which can take anywhere from a few hours
to a few days, depending on your language of choice and your experience level.

 > **NOTE:** *The Level of Effort is a rough estimation if implementation goes
 > smoothly with a bank, this can drastically change based on the difficulty of
 > implementation with the bank's services. The estimations are made with the
 > Scrum Process in mind using fibonnaci numbers (Small, Medium, Large, XLarge) as work days.*


## Intents and their Services

In order for Kasisto to react to certain user intentions, we need access to the
data to fulfill those intentions. Below you will find a rough mapping of what it
will take to ensure that we have the data we need to provide the features you
want.


---

### All Sessions

 * **Level of Effort:** *Small*

A chat session with a user starts with Kasisto fetching the user's info by
targetting the `/customer` endpoint. The request and response for the
`/customer` endpoint looks like:

 > [`/customer`](./api-overview.md#customer)

For most endpoint calls, there are several commonalities. The `secret` header is
given to you by Kasisto so you can verify that it is from us. The `token` header
is the access token stored in Kasisto's system that the Enterprise API may use
to access the endpoints for a given user. This could be an Oauth Access Token
(that is managed internally to Kasisto, including refreshing) or another token
that the bank assigns to the user. The `user_id` field is provided in case it is
needed by the bank for any requests.


---

### Account Information

 * **Level of Effort:** *Medium*

In order for Kasisto to present intents based on a User's account information
(like getting a balance), the Enterprise API must implement the `/accounts`
endpoint. Which can be found here:

 > [`/accounts`](./api-overview.md#accounts)

The key details to keep in mind here is that the `account_id` in the request
from Kasisto should be expected as either:

 - `null` - Kasisto's way of requesting account details for ALL accounts
 - `string` - Request a single account for the user
 - `array` - Request multiple accounts for a user

Keep an eye out for mapping the account types given by banks to match the
enumerations needed by Kasisto.

#### Gotchas

> - Ensure you have the ability to handle `null` for accounts which should
>   fetch ALL account details
> - Keep an eye on the enumerations for `account_type` and `currency_code`
>     - `account_type` **enumeration:** All lowercase with underscore word
>       separation. e.g. "cd", "checking", "credit_card", etc.
>     - `currency_code` **enumeration:** All uppercase, 3 letter codes from ISO
>       4217. e.g. "USD", "CAD", "INR", etc.


---

### Transaction Search

 * **Level of Effort:** *XLarge*

One of the most powerful features Kasisto has is giving the user the ability to
search for transactions with a variety of filters using natural language. These
transactions are fetched from the Enterprise API with the `/transactions`
endpoint. The documentation for transactions can be found here:

 > [`/transactions`](./api-overview.md#transactions)

##### Optional Enhancements

 > [`/merchants`](./api-overview.md#merchants)
 > [`/categories`](./api-overview.md#categories)
 > [`/payees`](./api-overview.md#payees)

The filters are mostly applied on the Kasisto side of things, but the key
detail to keep in mind is that we send a `limit` as well as a `start_date`, and
`end_date`. It should be noted that `limit` does not relate directly to the
user's request, but instead relates to our internally set limit that we use to
determine how much to grab from the Enterprise API for that implementation. The
reason for this is that we need to grab more than expected so we have at least
`X` transactions AFTER applying the user's desired filters. Something mentioned
later in the document is that it may be more optimal for the Enterprise API to
do that filtering of dates and limits on their side, rather than relying on
bank services to do it. This way a single request can be made for the max
number of transactions and that request can be cached, then re-used with
different filters. You may also have to merge in the `account_id` for the
transactions as well.

The additional endpoints for `/merchants`, `/categories`, and `/payees` enables
our system to optimize transaction searches, but giving us details on the
possibilities for the respective endpoint. Finding merchants, categories, and
payees becomes much more accuracte if these endpoints are implemented.

#### Gotchas

> - Handle a `null` limit properly (this should not limit the transactions
>   coming out)
> - Some data like `currency_code` or `account_id` doesn't come from the
>   transaction and comes from the account details, so merge that in when need
>   be
> - While `location` is optional, it enables a valuable search by location
>   feature
> - Sometimes the `merchant` comes from banks as a field known as `payee` or
>   similar nomenclature
> - For the Spending Overview features to work properly the `transaction_type`
>   field must be of type `credit` or `debit`
> - Keep an eye on the enumeration for `status`, `currency_code`, and
>   `transaction_type`
>     - `status` **enumeration:** All lowercase. e.g. "posted", "pending",
>       "cancelled", etc.
>     - `currency_code` **enumeration:** All uppercase, 3 letter codes from ISO
>       4217. e.g. "USD", "CAD", "INR", etc.
>     - `transaction_type` **enumeration:** All lowercase with underscore word
>       separation. e.g. "atm", "check_deposit", "credit", etc.


---

### Account Transfers

 * **Level of Effort:** *Medium*

A simple, but very useful feature of Kasisto is the ability to transfer money
from one account to another account. The request and response for this is fairly
straight forward, and probably the only thing to keep in mind is the enumeration
around the transfer status:

 > [`/transfer`](./api-overview.md#transfer)

#### Gotchas

> - Transfers implement an "Intent Level Security" system that enables the
>   Enterprise to require additional authorization.
>     - Throw a `[450] One-Time Password is required` http response to require
>       a OTP from the user
> - Keep an eye on the enumeration for `status`
>     - `status` **enumeration:** All lowercase. e.g. "posted", "pending",
>       "cancelled", etc.


---

### Person to Person Payments

 * **Level of Effort:** *XLarge*

The ability to pay another person is very valuable (aka P2P) and typically
requires two endpoint calls. The first being to `/payees` in order to get a
list of people that a user is able to send a payment to. After those payees are
presented and one is selected (with an amount to pay) a call to `/payment` will
be made. Again pay close attention to enumerations (like `status`):

 > [`/payees`](./api-overview.md#payees)
 > [`/payment`](./api-overview.md#payment)

#### Gotchas

> - P2P implement an "Intent Level Security" system that enables the
>   Enterprise to require additional authorization.
>     - Throw a `[450] One-Time Password is required` http response to require
>       a OTP from the user
> - Keep an eye on the enumeration for `currency_code` and `status`
>     - `currency_code` **enumeration:** All uppercase, 3 letter codes from ISO
>       4217. e.g. "USD", "CAD", "INR", etc.
>     - `status` **enumeration:** All lowercase. e.g. "posted", "pending",
>       "cancelled", etc.


## Handling Common Complications

Implementing an API spec is fairly trivial if you have experience with APIs. The
real meat of the Enterprise API comes from integration with the given bank's
services and handling change quickly to address problems. Every bank and
scenario is different, but there are some common considerations that should be
taken into account that will add time to your implementation.


### Making Multiple Calls for Aggregation

 * **Additional Level of Effort:** *XLarge*

One of the most common patterns that will be run into is having to take a single
batch of information (like a list of account IDs) and convert them into a batch
of things for each piece of information from a different location (details for
each account). If this is done in a serial manner (one after another) the it
takes to gather all of the data needed to fulfill a request can take a lot of
time. It is recommended that each of these calls are made concurrently. This can
be done in a variety of ways based on your language of choice. In Node.js, it is
as simple as making normal request asynchronous calls and batching the results
in the end. In Java, this may involve spinning up multiple threads and combining
them into a single response. Either way, to ensure a smooth experience plan a
strategy to handle requests to banks in parallel.


### Server Load

 * **Additional Level of Effort:** *Large*

It is common for banking infrastructure to be fragile and it may not be able to
handle the load of many requests one after the other. The best way to approach
this is to integrate caching on your Enterprise API implementation. There are a
lot of caching solutions that exist, Redis being a very common one. Consider
using the request parameters and the endpoint as a composite key in your caching
solution. This ensures that every request that would have the same parameters
going to the same location can quickly be pulled from the cache. Keep in mind
that working with stale data can create a fragile user experience, so be mindful
of expiring these cached requests perhaps after 15 minutes of the initial
request so fresh data can be pulled.


### Response Time

 * **Additional Level of Effort:** *Large*

Sometimes frequency of calls isn't a problem, but instead the problem is the
length of calls. This problem can be partially alleviated by using caching as
recommended above. Another consideration is shifting the responsibility data
processing to the Enterprise API layer. For example, when searching transactions
the user will use a variable amount of filtering like "last month" or
"yesterday". When you are caching based on request parameters to the bank that
include filtering or sorting, this can result in cache misses for almost exactly
the same data. Instead a pattern that includes fetching the maximum amount of
data possible (like 180 days worth of transactions) and caching that, then doing
the sorting and filtering on the API server will result in much higher
performance and put less strain on the bank's infrastructure.


### Error Handling

 * **Additional Level of Effort:** *Medium*

Expect failures when working with any infrastructure and have a strategy to
tackle them. A common one may be that an API key or authorization may fail and
may have to be refreshed. The Enterprise API needs to be able to respond to
these scenarios gracefully without hiccup.


### Parameter Management

 * **Additional Level of Effort:** *+Small*

Always protect your instance against the parallels of request parameters. As
common to all programming is ensuring that your system is able to handle
parameters when they are missing, when they come in malformed, or when you get
extra parameters that you don't know what to do with. Always ensure that you are
able to handle every scenario where "X" parameter is missing from a request. For
example, expect that `account_id` might come in as `null`. A clean default for
that would be fetching data for ALL account IDs. Request parameters may come in
as their primitive data type... or an array of that data type. Expect to handle
both.


### Data Mapping

 * **Additional Level of Effort:** *+Small*

Obviously not every bank will have every piece of data that we are looking for.
Do your best to create a transformation function that will convert what the bank
has to what Kasisto needs. This may be difficult and require data manipulation
like string parsing, enumeration mapping, or deriving based on other data that
exists. It may even require additional calls to endpoints to collect all of the
data. This may be one of the more difficult task as this requires a bit of
domain knowledge in the financial space as well as communication with the bank
services to get a feel for what should be what.
