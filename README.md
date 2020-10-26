# Ticket Overlord
Ticket management system which utilizes DRF, Redis and Celery

## Requirements
 Docker and docker-compose

## How to launch
 1. Copy `.env.template` to `.env` and customize it to your liking
 2. `docker-compose up -d`
 3. You can access the app on `localhost:8080`

## Main concepts
### Program flow
- `event/events/` will return a generic list with only ids of available ticket types
- `event/events/<pk>` will return a detailed view about the event with full ticket types
- Frontend can evaluate if it is possible to reserve a ticket by 'available' field to avoid unnecessary requests,
- In case user needs to login or create an account `/api-auth/login/` and `/register/` endpoints are available,
- If user is logged in, they can access `/event/reservations/` to view their reservations. If `validated` field is set to `False`, frontend should countdown to 15 minutes past `created` field to indicate how much time is left before reservation expires,
- If a user wishes to reserve a ticket, FE should call **POST** on `/event/reservations/` with a structure containing `ticket_type` and `amount` of tickets,
- FE shouldn't allow the user to make multiple reservations, as they will be bounced back by the backend,
- If a user wants to start the payment, FE should call **POST** on `/payment/payments` with a self-documenting `reservation_id`,
- To start payment procedure, FE should call **POST** on `/payment/payments/<int:id>/pay/` with a `token` for transaction, which is passed to payment gateway,
- State of the procedure is available under `payment_status`, and any errors on `error` fields when using **GET** on `/payment/payments/<int:id>/`,
- While payment process is not `FAILURE` or `SUCCESS` the reservation will not be removed.


### Caching
- all computed fields that will have to be accessed frequently (eg. ticket availability) are cached for 15 minutes,
- creation and deletion of reservations trigger cache reload for associated tickets

### Threading
- creating a reservation spawns a delayed destructor thread, that will attempt to delete the reservation
- if `validated` field on the object hasn't been set by the time of deletion, it will follow through, otherwise worker will be dismissed
- payment is processed on a separate thread as well
- result of the payment will be stored in payment model -- if there will be any errors, amount and currency will be null and error details will be available in error field
- if the payment is successful, reservation destruction worker will be dismissed and `validated` field on reservation will be set
- if during reservation deletion the payment is being processed, purge will be halted until payment completion. If it results in success, deletion will be canceled. If it results in an error, reservation will be removed.

### General optimizations
- Database operations are done using queryset and Q operations when viable to let Postgres do its thing using as few SQL commands as possible

## Issues
- Probably should have created object factories (factoryboy, model momma) for testing purposes, but the app got out of hand before I realized it
- Tests for payment application are failing due to wonky Celery integration with test database. Fix (spawning separate worker in test environment and allowing for database queries during test in TransactionTestCase) provided for event application aren't working for the other app.
- Code is a bit monolithic, but due to time constraints I have opted out of refactoring the whole thing.

## API
### Authorization
- `api-auth/`
    - `login/` **POST** `{username: -, password: -}` **RESPONSE** `auth-token` **REDIRECTS** to `reservations/` Logins and creates a session
    - `logout/` **POST** Logs out from session
- `register/` **POST** `{username: -, email: -, password: -}` Creates account

### Events
- `event/`
    - `events/` **GET** Returns a list of events and their tickets sorted by date
    - `tickets/<int:id>` **GET** Returns details about ticket
    - `reservations/` **GET/POST** **AUTHORIZED_ONLY** Lists or creates reservations for authorized user.
    - `reservations/<int:id>` **GET/DELETE** Returns or deletes reservation.

### Payments
- `payment/`
    - `payments/` **POST** **AUTHORIZED_ONLY** `{reservation_id:-}` Creates a payment for reservation.
    - `payments/` **GET** **AUTHORIZED_ONLY** Returns a list or creates payments for authorized user.
    - `payments/<int:id>` **GET/DELETE** Returns or deletes payment. 
        - `pay/` **POST** `{token:-}` Starts payment process.

### Stats
- `stats/`
    - `events/` **GET** Returns a list of all events, with amount of reservations, tickets sold and profit.
        - `top_popular/` **GET** Returns a list of top 5 events sorted by reservation amount.
        - `top_profit/` **GET** Returns a list of top 5 most profitable events.
        - `top_selling/` **GET** Returns a list of top 5 events sorted by amount of sold tickets.
    - `tickets/` **GET** Returns a list of all ticket types with amount of reservations, average amount of tickets per reservation, tickets sold and profit from tickets.
