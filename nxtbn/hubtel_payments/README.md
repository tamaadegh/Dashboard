Hubtel Receive Money integration
================================

Endpoints
- `POST /payments/api/initiate/` — Initiate a mobile money payment.
  - Request JSON: `{ "msisdn": "23324xxxxxxx", "amount": "10.00", "channel": "mtn-gh", "customer_name": "John" }`
  - Response JSON: `{ "client_reference": "<uuid>", "hubtel_response": { ... } }`

- `POST /payments/api/callback/` — Hubtel will POST asynchronous confirmation to this URL.
  - The callback contains `ClientReference` and `Status`/`ResponseCode` and other details. The endpoint is CSRF-exempt.

- `GET /payments/api/status/<client_reference>/` — Manual or scheduled status check. If transaction is pending for >5 minutes, backend queries Hubtel status API.

Environment
- Set the following variables in your `.env` (see `env.example`):
  - `HUBTEL_BASIC_AUTH_KEY` — Basic auth token (do NOT commit)
  - `HUBTEL_POS_SALES_ID` — POS Sales ID for your Hubtel merchant account
  - `HUBTEL_CALLBACK_URL` — Public HTTPS endpoint Hubtel will call (eg `https://your.domain.com/payments/api/callback/`)

Android integration (mobile app)
- Step 1: Call `POST /payments/api/initiate/` with `msisdn`, `amount` and `channel`.
- Step 2: Server returns `client_reference` and Hubtel initial response. Display a friendly message saying payment is being processed.
- Step 3: Hubtel will post a callback to the server when payment completes — server will update transaction state, no action required on the app side.
- Step 4: App can poll `GET /payments/api/status/<client_reference>/` to confirm final status or wait for push notification via your existing app notification flow.

Security
- The Hubtel API is IP-whitelisted; ensure your server IP is whitelisted in the Hubtel dashboard.
- Use HTTPS for `HUBTEL_CALLBACK_URL` and do not expose `HUBTEL_BASIC_AUTH_KEY` in logs.
