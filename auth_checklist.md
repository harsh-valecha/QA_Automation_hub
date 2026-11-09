# Authentication Testing Cheat Sheet

## Core ideas

- **Authentication (AuthN):** proves who the caller is.
- **Authorization (AuthZ):** decides what that caller may do. A valid login does not imply access to every action.
- HTTP is usually stateless: credentials or a session/token must accompany each protected request, unless the client retains and resends a cookie.
- Test only systems and accounts you are authorized to use. Prefer dedicated test accounts and a non-production environment.

## Common mechanisms

| Mechanism                         | What the client sends                                                                  | Typical `requests` approach                                                                                   |
| --------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Basic auth                        | Username and password, Base64-encoded in `Authorization`                               | `requests.get(url, auth=(user, password))`                                                                    |
| Cookie/session login              | Credentials posted to a login form; server returns a session cookie                    | Reuse `requests.Session()` for login and later requests                                                       |
| Bearer token                      | `Authorization: Bearer <token>`; token may be opaque or a JWT                          | Log in, then send the returned token in a header                                                              |
| API key                           | A key in a header (preferred) or sometimes a query parameter                           | Send the configured header; avoid URLs because they are often logged                                          |
| OAuth 2.0 / OpenID Connect (OIDC) | OAuth grants issue access tokens; OIDC adds identity/login information using ID tokens | Use a registered test client and the provider's documented test flow; send the access token as a bearer token |
| MFA / passkeys                    | An additional factor or cryptographic challenge                                        | Use the provider's approved test flow, test account, or test hook; don't try to bypass the challenge          |

Basic auth and API keys are simple credentials, not a complete user-login/session design. Always use HTTPS outside local development. A JWT is a token format, not a login protocol; clients should treat it as opaque unless they have a specific reason to validate its claims.

## `requests` patterns

### Basic auth

```python
import requests

response = requests.get(
    "https://example.test/api/private",
    auth=(username, password),
    timeout=10,
)
```

### Cookie/session login

A session keeps cookies received from the server and sends them on later requests. The exact form fields and any CSRF token depend on the site.

```python
session = requests.Session()
login_page = session.get("https://example.test/login", timeout=10)
# Read the required CSRF token from the page if the app uses one.
response = session.post(
    "https://example.test/login",
    data={"username": username, "password": password},
    timeout=10,
)
private_page = session.get("https://example.test/private", timeout=10)
```

### Bearer token

```python
session = requests.Session()
login = session.post(
    "https://example.test/api/auth/login",
    json={"username": username, "password": password},
    timeout=10,
)
assert login.status_code == 200

token = login.json()["token"]
me = session.get(
    "https://example.test/api/auth/me",
    headers={"Authorization": f"Bearer {token}"},
    timeout=10,
)
assert me.status_code == 200
```

In this practice app, the demo credentials are `admin / admin123` and `user / user123`; the API uses the bearer-token flow above. Its UI login uses a cookie-backed session instead.

### API key

```python
response = requests.get(
    "https://example.test/api/data",
    headers={"X-API-Key": api_key},
    timeout=10,
)
```

Use the header name and placement required by the API documentation. Do not commit keys to source control or print them in test output.

## What to check

- Correct credentials succeed; incorrect credentials and missing required fields fail with the documented status and response shape.
- A protected endpoint rejects missing, malformed, invalid, and expired credentials (commonly `401`).
- A valid identity without the required permission is denied (commonly `403`). Check both allowed and forbidden roles.
- Session login retains its cookie; logout invalidates the session. For token flows, check expiry and refresh/revocation behavior if the API supports them.
- Form-based login handles CSRF protection as documented. Do not disable CSRF checks just to make a test pass.
- Redirects, error messages, and response bodies do not expose passwords, tokens, or other secrets.
- Use timeouts, assert the expected status and key response fields, and avoid depending on exact token values because they should vary.

## Secret handling

Load credentials from environment variables or a test-secret store. Never commit real credentials, put them in query strings, or include them in logs, screenshots, or assertion messages. Keep TLS certificate verification enabled; do not use `verify=False` to silence certificate errors.
