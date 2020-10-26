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
- frontend can get data using dedicated endpoints
- `events/` will return a generic list with only ids of available ticket types
- `events/<pk>` will return a detailed view about the event
- after logging in, user can create a reservation and will be able to get information when the reservation was made
- the reservation will be valid for ~15 minutes
- if the user tries to process payment after reservation has timed out, he will be met with an error

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
- Tests for payment application are failing due to wonky Celery integration with test database. Fix (spawning separate worker in test environment and allowing for database queries during test in TransactionTestCase) provided for event application aren't working for the other app.
- Code is a bit monolythic, but due to time constraints I have opted out of refactoring the whole thing.

## API
### Authorization
- `api-auth/`
    - `login/` **POST** `{username: -, password: -}` **RESPONSE** `auth-token` **REDIRECTS** to `reservations/` Logins and creates a session
    - `logout/` **POST** Logs out from session
- `register/` **POST** `{username: -, email: -, password: -}` Creates account

### Events
- `events/` **GET** Returns a list of events and their tickets sorted by date
- `tickets/<int:id>` **GET** Returns details about ticket
- `reservations/` **GET**/**POST** **AUTHORIZED_ONLY** Lists or creates reservations for authorized user.
    - `reservations/<int:id>` **GET** **DELETE** Returns or deletes reservation.

