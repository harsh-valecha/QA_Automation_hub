# API Status Codes Cheat Sheet

A quick reference for understanding API responses, choosing assertions, and remembering the codes you see most often.

> **Fast rule:** `2xx` = success, `3xx` = redirect/cache, `4xx` = request or client-side problem, `5xx` = server-side problem.

## Contents

- [The codes to memorize first](#the-codes-to-memorize-first)
- [All the commonly encountered codes](#commonly-encountered-codes)
- [Easy-to-confuse pairs](#easy-to-confuse-pairs)
- [API testing quick checks](#api-testing-quick-checks)
- [Recall quiz](#recall-quiz)

## The codes to memorize first

| Code | Name | Remember it as |
|---:|---|---|
| `200` | OK | Request worked; response usually has a body. |
| `201` | Created | A resource was created. Look for its representation or `Location`. |
| `202` | Accepted | Work was accepted, but may not be finished yet. |
| `204` | No Content | Worked; there is no response body. |
| `301` / `302` | Moved / Found | Redirect; commonly used for permanent / temporary redirects. |
| `304` | Not Modified | Cached representation can be reused; not an error. |
| `400` | Bad Request | The request is malformed or invalid. |
| `401` | Unauthorized | Authentication is missing or invalid: **who are you?** |
| `403` | Forbidden | Caller is understood but not allowed: **you can't do that.** |
| `404` | Not Found | No matching resource (or the server chooses not to reveal it). |
| `409` | Conflict | Request conflicts with the current resource state. |
| `422` | Unprocessable Content | Syntax is understood, but validation/business rules fail. |
| `429` | Too Many Requests | Rate limit hit; check `Retry-After`. |
| `500` | Internal Server Error | Unexpected server failure. |
| `502` | Bad Gateway | A gateway/proxy got an invalid upstream response. |
| `503` | Service Unavailable | Temporarily unable to serve; check `Retry-After`. |
| `504` | Gateway Timeout | A gateway/proxy did not get an upstream response in time. |

## Commonly encountered codes

<details>
<summary><strong>1xx — Informational</strong> (request is still in progress)</summary>

| Code | Name | Typical meaning |
|---:|---|---|
| `100` | Continue | Server says the client may send the request body. |
| `101` | Switching Protocols | Server is switching protocols, such as to WebSocket. |
| `103` | Early Hints | Server sends preliminary headers while preparing the response. |

These are uncommon in ordinary API test assertions; the final response is usually what your client exposes.
</details>

<details>
<summary><strong>2xx — Success</strong></summary>

| Code | Name | Typical meaning |
|---:|---|---|
| `200` | OK | Request succeeded. Common for reads and successful updates. |
| `201` | Created | Request created a resource. Often returned by `POST`. |
| `202` | Accepted | Request accepted for asynchronous processing; completion is not guaranteed yet. |
| `203` | Non-Authoritative Information | Response metadata/payload was modified by a transforming proxy. |
| `204` | No Content | Request succeeded and intentionally has no response body. Common for `DELETE`. |
| `205` | Reset Content | Request succeeded; client should reset the current view/form. |
| `206` | Partial Content | Server returned a requested range of a representation. |
| `207` | Multi-Status | Multiple independent results; used mainly by WebDAV. |
| `208` | Already Reported | Resource already appeared in a WebDAV multistatus response. |
| `226` | IM Used | Server returned a delta/instance manipulation; uncommon. |

</details>

<details>
<summary><strong>3xx — Redirection and caching</strong></summary>

| Code | Name | Typical meaning |
|---:|---|---|
| `300` | Multiple Choices | More than one representation/action is available. |
| `301` | Moved Permanently | Resource has a permanent new URL. |
| `302` | Found | Temporary redirect; clients may historically change `POST` to `GET`. |
| `303` | See Other | Follow the redirect with `GET` (often after a form submission). |
| `304` | Not Modified | Conditional request says the cached copy is still current; no body. |
| `307` | Temporary Redirect | Temporary redirect; preserve the request method and body. |
| `308` | Permanent Redirect | Permanent redirect; preserve the request method and body. |

</details>

<details>
<summary><strong>4xx — Request or client-side errors</strong></summary>

| Code | Name | Typical meaning |
|---:|---|---|
| `400` | Bad Request | Malformed request or invalid syntax/parameters. |
| `401` | Unauthorized | Authentication is required or failed. APIs commonly include `WWW-Authenticate`. |
| `402` | Payment Required | Reserved for future use; some services use it for payment-related rules. |
| `403` | Forbidden | Request understood, but the caller lacks permission. |
| `404` | Not Found | No matching resource, or the server intentionally hides its existence. |
| `405` | Method Not Allowed | Method is not supported for this resource; check the `Allow` header. |
| `406` | Not Acceptable | Server cannot produce a representation matching `Accept`. |
| `407` | Proxy Authentication Required | Authentication with a proxy is required. |
| `408` | Request Timeout | Server timed out waiting for the request. |
| `409` | Conflict | Request conflicts with current state, such as a duplicate unique value. |
| `410` | Gone | Resource is intentionally and permanently unavailable. |
| `411` | Length Required | Server requires a `Content-Length` header. |
| `412` | Precondition Failed | A condition in headers such as `If-Match` was not met. |
| `413` | Content Too Large | Request body exceeds the server's limit. |
| `414` | URI Too Long | Request URI exceeds the server's limit. |
| `415` | Unsupported Media Type | Request body format/content type is not supported. |
| `416` | Range Not Satisfiable | Requested byte range cannot be served. |
| `417` | Expectation Failed | Server cannot meet the request's `Expect` header. |
| `418` | I'm a Teapot | April Fools' code; not for normal API behavior. |
| `421` | Misdirected Request | Request was sent to a server unable to produce a response. |
| `422` | Unprocessable Content | Request format is understood, but its instructions/values fail validation. |
| `423` | Locked | Resource is locked; used mainly by WebDAV. |
| `424` | Failed Dependency | Request failed because a related operation failed; mainly WebDAV. |
| `425` | Too Early | Server is unwilling to risk replaying an early request. |
| `426` | Upgrade Required | Client must switch to a different protocol. |
| `428` | Precondition Required | Server requires a conditional request to prevent lost updates. |
| `429` | Too Many Requests | Client exceeded a rate limit; response may include `Retry-After`. |
| `431` | Request Header Fields Too Large | Request headers are too large. |
| `451` | Unavailable For Legal Reasons | Access is denied due to a legal demand/restriction. |

</details>

<details>
<summary><strong>5xx — Server-side errors</strong></summary>

| Code | Name | Typical meaning |
|---:|---|---|
| `500` | Internal Server Error | Unexpected condition prevented the server from fulfilling the request. |
| `501` | Not Implemented | Server does not support the requested functionality. |
| `502` | Bad Gateway | Gateway/proxy received an invalid response from upstream. |
| `503` | Service Unavailable | Server is temporarily unavailable or overloaded; may include `Retry-After`. |
| `504` | Gateway Timeout | Gateway/proxy did not receive an upstream response in time. |
| `505` | HTTP Version Not Supported | Server does not support the request's HTTP version. |
| `507` | Insufficient Storage | Server could not store the representation; mainly WebDAV. |
| `508` | Loop Detected | Server detected an infinite loop while processing; mainly WebDAV. |
| `510` | Not Extended | Further extensions to the request are required; uncommon. |
| `511` | Network Authentication Required | Client needs to authenticate to gain network access, often a captive portal. |

</details>

## Easy-to-confuse pairs

<details>
<summary><strong>Reveal the distinctions</strong></summary>

- **`200` vs `201`:** the request succeeded vs a new resource was created.
- **`201` vs `202`:** created now vs accepted for processing that may finish later.
- **`200` vs `204`:** successful response with a representation vs successful response with no body. Don't try to parse JSON from `204`.
- **`301` / `302` vs `307` / `308`:** redirects where clients may change the method vs redirects that preserve it. `301`/`308` are permanent; `302`/`307` are temporary.
- **`304` vs `404`:** cached representation is still valid vs no available representation for that resource.
- **`400` vs `422`:** malformed/invalid request vs well-formed request whose values fail validation. APIs vary; follow their contract.
- **`401` vs `403`:** authentication problem vs authorization problem. A `401` is not simply “logged in but forbidden.”
- **`404` vs `410`:** not found/unknown vs known to be permanently gone.
- **`409` vs `422`:** conflict with current state (for example, duplicate ISBN) vs invalid field/value (for example, ISBN format).
- **`500` vs `502` vs `503` vs `504`:** local unexpected failure vs invalid upstream response vs temporarily unavailable vs upstream timeout.

</details>

## API testing quick checks

- Assert the **status and response contract**, not just that the request did not throw.
- For `201`, check the created resource and, when promised, the `Location` header.
- For `202`, check how the API reports job status or lets you poll for completion.
- For `204` and `304`, don't expect a response body.
- For `401`/`403`, test both missing/invalid identity and insufficient permission as separate cases.
- For `405`, check the `Allow` header when your API specifies it.
- For `409`/`422`, assert useful, stable error fields; avoid asserting incidental wording.
- For `429`/`503`, respect `Retry-After` if provided; don't make tests hammer a service.
- Treat `5xx` as a server/service failure, but check the API's documented retry policy before retrying writes.

Example with `requests`:

```python
response = requests.post(
    f"{base_url}/api/books",
    json={"title": "API Testing", "isbn": "9780000000001"},
    timeout=10,
)

assert response.status_code == 201
assert response.json()["title"] == "API Testing"
assert "Location" in response.headers
```

In this practice hub, useful examples include `201` on book creation, `204` on deletion, `401` for missing authentication, `403` for insufficient permission, `404` for a missing book, `409` for duplicate ISBN, and `422` for validation errors. See the [API examples in the project README](./README.md#2-features-each-testable-via-ui-and-api).

## Recall quiz

Try to answer before opening each item.

<details>
<summary>Authentication is missing or invalid. Which status?</summary>

`401 Unauthorized`
</details>

<details>
<summary>The user is authenticated but lacks permission. Which status?</summary>

`403 Forbidden`
</details>

<details>
<summary>A POST successfully creates a new resource. What status should you usually expect?</summary>

`201 Created`
</details>

<details>
<summary>A DELETE succeeds and intentionally returns no body. Which status fits?</summary>

`204 No Content`
</details>

<details>
<summary>The JSON is valid, but a required field fails validation. Which status is commonly used?</summary>

`422 Unprocessable Content` (some APIs use `400`; follow the API contract).
</details>

<details>
<summary>A duplicate value conflicts with the resource's current state. Which status?</summary>

`409 Conflict`
</details>

<details>
<summary>The client sent too many requests. Which status, and which header might help?</summary>

`429 Too Many Requests`; check `Retry-After`.
</details>

<details>
<summary>A proxy timed out waiting for its upstream server. Which status?</summary>

`504 Gateway Timeout`
</details>

---

**Memory hook:** `401` = identify yourself; `403` = not allowed; `404` = can't find it; `409` = state conflict; `422` = values don't pass; `429` = slow down; `5xx` = server-side trouble.

> Status codes are standardized, but APIs sometimes use them differently. When testing a specific service, its documented contract is the source of truth.
