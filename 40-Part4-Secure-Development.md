# Part 4 - Secure Development

*Two layers: **Part A** is the build narrative. **Part B** is the complete reference. **Part C**
is the interview pressure test.*

---

# Part A - THE BUILD: Securing The Employee-Services Platform

## Step 1. Every boundary validates input

The portal accepts forms, file uploads, API payloads, webhook payloads, SFTP files and data from
legacy systems. All of them are untrusted. We validate at the server boundary using allow-lists,
canonicalization, schema validation, semantic business validation and file-specific checks.

> Reference: [4.1 Input validation](#41-input-validation)

## Step 2. Injection is prevented by design, not filtering

The platform uses SQL, search, shell scripts, LDAP-like directories, templates and NoSQL-style
stores. Injection prevention means safe APIs, parameterization, escaping where no safe API
exists, and never passing untrusted input into interpreters.

> Reference: [4.2 Injection](#42-injection)

## Step 3. Output must be encoded for its context

Stored XSS appears when a user-controlled field is rendered later in an admin page. The fix is
context-aware output encoding, safe rendering, CSP and sanitization libraries for rich content.

> Reference: [4.3 Output encoding, XSS, CSP and sanitization](#43-output-encoding-xss-csp-and-sanitization)

## Step 4. Authentication runs through Microsoft Entra

Employees authenticate through Microsoft Entra ID. APIs validate JWTs. Service-to-service
calls use client credentials, managed identities or on-behalf-of flow where user delegation is
required. Public or citizen-facing scenarios may use External ID/B2C-style patterns.

> Reference: [4.4 Authentication](#44-authentication)

## Step 5. Authorization is where most serious API bugs live

The user is authenticated, but can they access this employee record, approval, document or
department? Authorization requires RBAC/ABAC/ReBAC thinking, tenant/BU isolation, row-level
checks and BOLA/IDOR prevention.

> Reference: [4.6 Authorization](#46-authorization)

## Step 6. Web protections still matter behind SSO

SSO does not remove CSRF, SSRF, CORS, clickjacking or security-header risks. Browser behavior
and server-side outbound calls need explicit controls.

> Reference: [4.8 Browser and platform web risks](#48-browser-and-platform-web-risks)

## Step 7. Secrets and keys are platform responsibilities

No secrets in code, Docker images, Kubernetes YAML or CI logs. Use Key Vault, managed identity,
rotation and clear break-glass process. Cryptography must distinguish hashing, encryption,
TLS, mTLS, CMK and PMK.

> Reference: [4.9 Secrets management](#49-secrets-management)
> Reference: [4.10 Cryptography](#410-cryptography)

## Step 8. Network design supports zero trust

Private endpoints, VNet integration, NSGs, WAF, DDoS protection and least-privilege egress
reduce exposure. Network controls support application authorization; they do not replace it.

> Reference: [4.11 Network security](#411-network-security)

## Step 9. Security must be inside SDLC

Threat modeling, security requirements, DevSecOps gates, pen-test remediation and vulnerability
SLAs must be part of delivery. Late security creates release surprises.

> Reference: [4.12 Secure SDLC](#412-secure-sdlc)

## Step 10. Audit logs must be useful and safe

Government systems need auditability: who did what, to which record, from where, and when. But
logs must not leak passwords, tokens, secrets or excessive PII.

> Reference: [4.13 Logging and auditability](#413-logging-and-auditability)

---

# Part B - THE REFERENCE

## 4.1 Input Validation

Input validation ensures only well-formed data enters the workflow. It is not the only defense
against injection or XSS, but it reduces attack surface and protects downstream systems.

### 4.1.1 Allow-List vs Deny-List

Allow-list validation defines what is acceptable.

Examples:

- employee number pattern,
- allowed document types,
- allowed file extensions,
- known workflow status transitions,
- fixed enum values,
- maximum length.

Deny-list validation tries to block known bad values. It is weaker because attackers can find
new encodings or bypasses.

Use deny-lists only as an extra layer, not the primary control.

### 4.1.2 Canonicalization

Canonicalization converts input to a standard representation before validation.

Why it matters:

- encoded path traversal,
- Unicode normalization,
- mixed path separators,
- URL-encoded payloads,
- case-insensitive identifiers,
- Arabic/English text normalization,
- double extensions in filenames.

Bad:

```text
Validate "../secret" is blocked, but accept "%2e%2e%2fsecret"
```

Better:

```text
Decode/canonicalize first -> validate normalized value -> use safe API
```

### 4.1.3 Server-Side Enforcement

Client-side validation improves UX. Server-side validation enforces security.

Never trust:

- disabled fields,
- hidden fields,
- client-calculated totals,
- frontend role checks,
- JavaScript validation,
- mobile app behavior.

### 4.1.4 Syntactic vs Semantic Validation

Syntactic:

- date format is valid,
- email shape is valid,
- number is an integer,
- enum value exists.

Semantic:

- leave end date is after start date,
- employee can submit for this department,
- amount is within policy,
- uploaded file belongs to this case.

Both are required.

### 4.1.5 File Upload Validation

File upload is high risk.

Controls:

- allow-list extensions,
- validate MIME/content type but do not trust the header alone,
- file signature/magic-number check,
- maximum size,
- generated storage filename,
- store outside web root or in private blob storage,
- antivirus/malware scan,
- content disarm and reconstruction where required,
- image/PDF rewriting where useful,
- block dangerous file types,
- prevent ZIP bombs and path traversal in archives,
- authorize upload and download,
- protect from CSRF,
- log metadata safely.

Do not let the user control the storage path.

## 4.2 Injection

Injection happens when untrusted data is interpreted as code, query, command or expression.

### 4.2.1 SQL Injection

Bad:

```sql
"SELECT * FROM Employees WHERE Id = '" + employeeId + "'"
```

Good:

- parameterized queries,
- prepared statements,
- ORM parameter binding,
- stored procedures only if they avoid dynamic SQL,
- least-privilege DB accounts,
- query allow-lists for dynamic sorting/filtering.

Dynamic order-by needs allow-listing:

```text
sort = "createdAt" -> ORDER BY CreatedAt
sort = "status" -> ORDER BY Status
```

Never pass raw column names from the client.

### 4.2.2 NoSQL Injection

Risk appears when user input controls query operators.

Example risk:

```json
{ "username": { "$ne": null }, "password": { "$ne": null } }
```

Controls:

- schema validation,
- reject objects where strings are expected,
- parameterized query APIs where available,
- allow-list operators,
- avoid direct merge of request body into query object.

### 4.2.3 Command Injection

Bad:

```python
os.system("convert " + uploaded_file)
```

Controls:

- avoid shell where possible,
- use library APIs instead of shell commands,
- pass arguments as arrays,
- allow-list command options,
- isolate execution,
- run as low-privilege user,
- set timeouts and resource limits.

### 4.2.4 LDAP Injection

LDAP injection occurs when input modifies directory queries.

Controls:

- parameterized/escaped LDAP filters,
- allow-list expected identifiers,
- least privilege directory account,
- avoid using user-controlled filter fragments.

### 4.2.5 SSTI

Server-Side Template Injection happens when untrusted input becomes template code.

Risk:

```text
Template: "Hello {{ user_input }}"
user_input: "{{ config.SECRET_KEY }}"
```

Controls:

- never treat user content as templates,
- separate templates from data,
- sandbox template engines where possible,
- restrict filters/functions,
- encode output.

### 4.2.6 General Injection Rule

Use a safe API that separates code from data. If a safe API does not exist, use context-specific
escaping and strict allow-list validation.

## 4.3 Output Encoding, XSS, CSP And Sanitization

XSS happens when attacker-controlled content executes in another user's browser.

Types:

- stored XSS,
- reflected XSS,
- DOM XSS.

### 4.3.1 Output Encoding

Encode for the context:

| Context | Control |
|---|---|
| HTML body | HTML entity encoding |
| HTML attribute | attribute encoding and quote attributes |
| JavaScript string | JavaScript string encoding; avoid inline JS |
| URL | URL encoding |
| CSS | avoid dynamic CSS; CSS escaping if required |

Do not use one generic sanitizer for every context.

### 4.3.2 Stored XSS

Example:

- user enters malicious display name,
- it is stored in database,
- admin page renders it without encoding.

Fix:

- encode on output,
- sanitize rich HTML if allowed,
- restrict input where business allows,
- CSP as defense in depth.

### 4.3.3 Reflected XSS

Example:

- search query echoed into page without encoding.

Fix:

- output encoding,
- framework escaping,
- avoid dangerous sinks,
- CSP.

### 4.3.4 DOM XSS

Happens in browser-side JavaScript when untrusted data reaches dangerous sinks:

- `innerHTML`,
- `document.write`,
- `eval`,
- unsafe URL navigation,
- template strings inserted as HTML.

Use:

- `textContent`,
- safe DOM APIs,
- trusted sanitization library for HTML,
- framework-safe rendering.

### 4.3.5 CSP

Content Security Policy reduces XSS exploitability by restricting sources of scripts, styles,
frames and other resources.

Strong concepts:

- avoid inline scripts,
- use nonces/hashes where needed,
- restrict `script-src`,
- use `frame-ancestors` for clickjacking protection,
- report-only mode before enforce,
- monitor violations.

CSP is defense in depth. It does not replace encoding.

### 4.3.6 Sanitization Libraries

Use when users are allowed to submit rich HTML.

Requirements:

- proven library,
- allow-list tags/attributes,
- strip scripts/events/styles as needed,
- update library,
- sanitize on server,
- encode after sanitization for final context if needed.

Do not write your own HTML sanitizer.

## 4.4 Authentication

Authentication proves who the caller is. Authorization decides what they can do.

### 4.4.1 OAuth 2.0

OAuth 2.0 is an authorization framework for delegated access. It issues access tokens for
clients to call protected resources.

Common flows:

- authorization code + PKCE,
- client credentials,
- on-behalf-of,
- device code for input-constrained devices,
- legacy implicit/ROPC flows to avoid.

### 4.4.2 Authorization Code + PKCE

Use for:

- single-page apps,
- mobile apps,
- web apps needing user sign-in.

PKCE protects the authorization code exchange and is the preferred modern flow for public
clients such as SPAs.

### 4.4.3 Client Credentials

Use for service-to-service app-only access.

Example:

- nightly integration service calls document API as itself,
- no user is present.

Use least-privilege app permissions and managed identity where possible.

### 4.4.4 Why Implicit And ROPC Are Dead

Implicit grant is replaced by authorization code + PKCE for SPAs because tokens in browser
URLs/fragments create leakage risks and modern browser/security practices support better
flows.

ROPC asks the app to handle the user's password directly. It does not support modern controls
such as MFA/Conditional Access in normal scenarios and is not recommended for production.

Interview phrasing:

"If someone proposes ROPC for convenience, I challenge it immediately and move them toward auth
code + PKCE, device code for constrained devices, or client credentials for app-only access."

### 4.4.5 OIDC

OpenID Connect adds identity on top of OAuth 2.0.

Tokens:

- ID token: tells the client who the user is.
- Access token: used to call APIs.
- Refresh token: obtains new access tokens.

Do not send ID tokens to APIs as authorization proof when an access token is required.

### 4.4.6 JWT Validation

APIs must validate:

- signature,
- issuer (`iss`),
- audience (`aud`),
- expiration (`exp`),
- not-before where used,
- token type/use,
- algorithm,
- key ID (`kid`) and signing-key rotation,
- scopes/roles/claims.

Do not:

- decode without verifying,
- accept tokens for the wrong audience,
- trust claims without checking issuer,
- disable signature validation in production.

### 4.4.7 Refresh Token Rotation And Sessions

Refresh tokens are sensitive and long-lived compared with access tokens.

Controls:

- store securely,
- rotate where platform supports/returns new tokens,
- delete old tokens after use,
- use short-lived access tokens,
- handle revocation/sign-out,
- protect browser apps from token theft,
- use secure, HttpOnly, SameSite cookies for web sessions where appropriate.

### 4.4.8 MFA And SSO

MFA reduces risk from stolen passwords. SSO centralizes authentication policy and user
lifecycle.

Use Conditional Access to require MFA based on:

- app sensitivity,
- user/group,
- location,
- device compliance,
- risk level,
- external user type.

## 4.5 Microsoft Entra ID

Government Microsoft environments often route identity through Microsoft Entra ID. Know the
vocabulary.

### 4.5.1 App Registrations

App registration defines an application in Entra:

- client/application ID,
- redirect URIs,
- certificates/secrets/federated credentials,
- API permissions,
- exposed scopes,
- app roles,
- owners.

Used by developers to define identity configuration.

### 4.5.2 Enterprise Applications

Enterprise application is the service principal instance in a tenant.

Used by admins for:

- assignments,
- SSO configuration,
- Conditional Access targeting,
- provisioning,
- permissions/admin consent,
- sign-in logs.

Simple phrasing:

"App registration is the app definition. Enterprise application/service principal is the
tenant-local instance used for access and administration."

### 4.5.3 App Roles vs Groups vs Scopes

| Concept | Best use | Token claim |
|---|---|---|
| Scopes | delegated permissions for user-consented API access | `scp` |
| App roles | app-defined roles for users/apps | `roles` |
| Groups | tenant-wide membership managed by admins | `groups` |

Good pattern:

- define application permissions as app roles/scopes,
- assign users/groups to app roles,
- avoid hardcoding group IDs deep in business code where portability matters,
- use groups for administration and app roles for app-level authorization semantics.

### 4.5.4 Conditional Access

Conditional Access evaluates signals and enforces controls.

Signals:

- user/group,
- app,
- location,
- device,
- risk,
- workload identity,
- external user,
- authentication strength.

Controls:

- require MFA,
- require compliant device,
- block,
- require approved client,
- session controls.

Plan break-glass accounts and exclusions carefully.

### 4.5.5 Managed Identity

Managed identity gives Azure resources an Entra identity without stored credentials.

Types:

- system-assigned,
- user-assigned.

Use for:

- App Service to Key Vault,
- AKS workload to Storage/Key Vault,
- Function App to Service Bus,
- VM to Azure APIs.

Prefer managed identity over client secrets when running in Azure.

### 4.5.6 B2B, B2C And External ID

B2B:

- collaboration with partners/guests,
- external users represented in workforce tenant,
- access controlled by guest policies and Conditional Access.

B2C/External ID style:

- citizen/customer-facing identity,
- separate external tenant/user journeys depending on platform,
- custom branding and sign-up/sign-in flows.

Interview answer:

"Employees and internal partners are workforce/B2B scenarios. Citizens or public-service users
are external identity/CIAM scenarios. I would not mix those casually in the same trust model."

### 4.5.7 SCIM Provisioning

SCIM automates user/group provisioning and deprovisioning between identity systems and apps.

Use for:

- SaaS app account lifecycle,
- HR-driven provisioning,
- guest/partner app provisioning,
- deprovisioning when employment or assignment changes.

Design:

- map attributes carefully,
- use assignment-based scoping,
- monitor provisioning errors,
- handle soft delete/deactivation,
- audit lifecycle changes.

## 4.6 Authorization

Authorization answers: "Can this authenticated principal perform this action on this resource
in this context?"

### 4.6.1 RBAC

Role-Based Access Control assigns permissions through roles.

Examples:

- Employee,
- Manager,
- HR Officer,
- HR Admin,
- Auditor.

Pros:

- simple,
- understandable,
- easy to audit.

Risk:

- role explosion,
- too coarse for row-level decisions.

### 4.6.2 ABAC

Attribute-Based Access Control uses attributes:

- department,
- grade,
- location,
- classification,
- employment type,
- request amount,
- workflow status.

Example:

"Managers can approve leave requests for employees in their department unless the request is
their own."

### 4.6.3 ReBAC

Relationship-Based Access Control uses relationships:

- manager of employee,
- owner of request,
- delegate for approver,
- member of case team.

Useful for workflows and case management.

### 4.6.4 Least Privilege

Principles:

- default deny,
- grant only needed permissions,
- separate read/write/admin,
- time-bound elevation,
- audit privileged actions,
- review access periodically.

### 4.6.5 Tenant/BU Isolation

In government and enterprise systems, isolation may be by:

- tenant,
- business unit,
- department,
- agency,
- region,
- data classification.

Controls:

- include tenant/BU in every query,
- enforce at service layer and database where possible,
- test cross-tenant access,
- avoid trusting client-supplied tenant IDs,
- ensure cache keys include tenant/user context.

### 4.6.6 Row-Level Authorization

Every object access must check both action and object:

```text
Can user U read document D?
Can manager M approve request R?
Can HR officer H edit employee E?
```

Do not check only route-level role.

### 4.6.7 IDOR / BOLA

IDOR/BOLA happens when an attacker changes an object ID and accesses someone else's resource.

Example:

```text
GET /api/employees/1001/salary-letter
GET /api/employees/1002/salary-letter
```

If the API checks only "user is logged in", it is vulnerable.

Controls:

- object-level authorization on every access,
- avoid relying on hidden UI buttons,
- indirect IDs are not a complete fix,
- central authorization helpers/policies,
- tests for cross-user access,
- audit denied access.

## 4.7 OWASP Top 10 And API Security Top 10

### 4.7.1 OWASP Top 10 2021

Know the list:

1. Broken Access Control.
2. Cryptographic Failures.
3. Injection.
4. Insecure Design.
5. Security Misconfiguration.
6. Vulnerable and Outdated Components.
7. Identification and Authentication Failures.
8. Software and Data Integrity Failures.
9. Security Logging and Monitoring Failures.
10. Server-Side Request Forgery.

Senior answer: do not recite only the list. Map it to controls:

- access control tests,
- threat modeling,
- parameterization,
- dependency scanning,
- secure configuration,
- logging/monitoring,
- SSRF-safe outbound calls.

### 4.7.2 OWASP API Security Top 10 2023

Know the API list:

1. Broken Object Level Authorization.
2. Broken Authentication.
3. Broken Object Property Level Authorization.
4. Unrestricted Resource Consumption.
5. Broken Function Level Authorization.
6. Unrestricted Access to Sensitive Business Flows.
7. Server-Side Request Forgery.
8. Security Misconfiguration.
9. Improper Inventory Management.
10. Unsafe Consumption of APIs.

Government/API answer:

"For APIs, authorization is usually the highest-risk area: object-level, property-level and
function-level authorization. I test that a user cannot access another user's record, cannot
see fields beyond their role, and cannot trigger business flows outside policy."

## 4.8 Browser And Platform Web Risks

### 4.8.1 CSRF

CSRF tricks a browser into sending an authenticated request to a trusted site.

Risk exists when:

- browser automatically sends cookies,
- state-changing endpoint lacks CSRF defense,
- CORS is misconfigured,
- SameSite is weak or absent.

Controls:

- CSRF tokens,
- SameSite cookies,
- custom request headers with CORS allow-list,
- re-auth/step-up for sensitive actions,
- avoid state-changing GET requests.

### 4.8.2 SSRF

SSRF abuses a server to make requests chosen by an attacker.

High-risk features:

- webhook URL registration,
- fetch image from URL,
- document import from URL,
- metadata/proxy services,
- integrations that follow redirects.

Controls:

- allow-list outbound destinations,
- block private/internal IP ranges where not required,
- resolve DNS and validate final IP,
- disable open redirects/follow carefully,
- egress firewall,
- metadata endpoint protection,
- timeouts and response size limits,
- no credentials sent to arbitrary URLs.

### 4.8.3 CORS Misconfiguration

CORS controls browser cross-origin access. It is not server-to-server authorization.

Bad:

```text
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

Controls:

- allow-list exact trusted origins,
- do not reflect arbitrary `Origin`,
- do not use wildcard with credentials,
- restrict methods/headers,
- keep API authorization independent of CORS.

### 4.8.4 Clickjacking

Clickjacking frames your app inside another page to trick users.

Controls:

- CSP `frame-ancestors`,
- `X-Frame-Options` for legacy compatibility,
- avoid embedding sensitive pages unless explicitly needed.

### 4.8.5 Security Headers

Common headers:

- `Strict-Transport-Security`,
- `Content-Security-Policy`,
- `X-Content-Type-Options: nosniff`,
- `Referrer-Policy`,
- `Permissions-Policy`,
- `frame-ancestors` in CSP,
- secure cookie attributes.

### 4.8.6 HSTS

HSTS tells browsers to use HTTPS for future requests.

Use after:

- HTTPS is stable everywhere,
- subdomain impact is understood,
- preload decision is reviewed if used.

## 4.9 Secrets Management

Secrets include:

- passwords,
- API keys,
- connection strings,
- private keys,
- certificates,
- signing keys,
- client secrets,
- storage keys.

Rules:

- no secrets in code,
- no secrets in Docker images,
- no secrets in Git history,
- no secrets in CI logs,
- no broad secret access,
- rotate secrets,
- audit reads,
- use managed identity where possible.

### 4.9.1 Azure Key Vault

Use Key Vault for:

- secrets,
- keys,
- certificates,
- rotation events,
- access logging,
- RBAC/access policy control.

Design:

- private endpoint for sensitive environments,
- purge protection/soft delete,
- least-privilege RBAC,
- managed identity access,
- separate vaults by environment/criticality,
- alert on suspicious access.

### 4.9.2 Rotation

Rotation process:

1. create new secret version,
2. update consuming system,
3. reload app or wait for refresh,
4. verify,
5. disable old version after safe window,
6. delete only according to policy.

Prefer identity-based access over shared secrets because rotation burden is lower.

## 4.10 Cryptography

### 4.10.1 TLS 1.2/1.3

Use TLS for all sensitive traffic, internal and external.

Controls:

- disable weak protocols/ciphers,
- valid certificates,
- automated certificate renewal,
- HSTS for web,
- monitor expiry,
- use private CA where needed.

### 4.10.2 mTLS

Mutual TLS authenticates both client and server with certificates.

Use for:

- high-trust service-to-service calls,
- partner APIs,
- internal APIs with strong client identity requirements.

Operational cost:

- certificate issuance,
- rotation,
- revocation,
- trust stores,
- troubleshooting.

### 4.10.3 At-Rest Encryption

Most Azure services encrypt at rest by default. Understand who manages keys.

### 4.10.4 CMK vs PMK

PMK: platform-managed key. Cloud provider manages keys.

CMK: customer-managed key. Organization controls key in Key Vault/managed HSM.

Use CMK when:

- regulation requires customer key control,
- separation of duties matters,
- key rotation/revocation control is required.

Costs:

- operational complexity,
- key availability dependency,
- rotation planning,
- access control.

### 4.10.5 Hashing Passwords

Passwords are not encrypted; they are hashed with slow password hashing algorithms.

Use:

- Argon2id where supported,
- bcrypt/scrypt/PBKDF2 where appropriate,
- unique salt,
- work factor,
- migration path for old hashes.

Do not use fast hashes like SHA-256 alone for passwords.

## 4.11 Network Security

### 4.11.1 Private Endpoints

Private endpoints expose Azure services through private IPs in your VNet.

Use for:

- Key Vault,
- Storage,
- SQL,
- ACR,
- private PaaS access.

Needs:

- private DNS,
- network routing,
- firewall rules,
- CI/CD agent connectivity.

### 4.11.2 VNet Integration

Lets services such as App Service or Functions reach private network resources. It is outbound
connectivity from the service into a VNet, not automatically private inbound exposure.

### 4.11.3 NSGs

Network Security Groups filter subnet/NIC traffic.

Use:

- restrict backend subnets,
- allow only gateway/AKS/app traffic,
- deny broad inbound,
- document rules.

### 4.11.4 WAF

Web Application Firewall protects HTTP/S entry points against common web attacks.

Use:

- Azure Application Gateway WAF,
- Front Door WAF,
- tuned OWASP rules,
- detection mode before prevention if false positives are unknown,
- exclusions with owner and expiry.

### 4.11.5 DDoS Protection

Use Azure DDoS Network Protection for public-facing resources where availability matters.

DDoS does not replace WAF. WAF handles application-layer patterns; DDoS handles volumetric and
network-layer resilience.

### 4.11.6 Zero-Trust Model

Principles:

- verify explicitly,
- least privilege,
- assume breach.

Applied:

- authenticate every request,
- authorize per resource/action,
- segment networks,
- restrict egress,
- monitor continuously,
- use managed identities,
- log privileged activity.

## 4.12 Secure SDLC

### 4.12.1 Threat Modeling With STRIDE

STRIDE:

- Spoofing,
- Tampering,
- Repudiation,
- Information disclosure,
- Denial of service,
- Elevation of privilege.

Process:

1. draw data flow diagram,
2. identify trust boundaries,
3. list threats per component/flow,
4. define mitigations,
5. track residual risk,
6. validate controls with tests.

### 4.12.2 Security Requirements

Examples:

- all APIs require Entra-issued access tokens,
- salary documents require row-level authorization,
- uploaded files require malware scan before release,
- secrets must come from Key Vault,
- all production changes require approved pipeline,
- audit logs retained for required period.

### 4.12.3 DevSecOps Gates

Gates:

- SAST,
- dependency scan,
- secret scan,
- IaC scan,
- container scan,
- DAST,
- threat-model review for high-risk changes,
- manual security approval for exceptions.

Use severity SLAs and exception expiry. Do not block delivery forever on low-risk noise.

### 4.12.4 Pen-Test Remediation

Good remediation process:

- triage severity,
- assign owner,
- reproduce,
- fix root cause,
- add regression test/control,
- retest,
- document evidence,
- close with security approval.

### 4.12.5 Vulnerability SLAs

Example:

- critical: fix or mitigate within 24-72 hours,
- high: fix within 7-14 days,
- medium: scheduled sprint,
- low: backlog with review.

Actual SLA depends on organization policy and exploitability.

## 4.13 Logging And Auditability

### 4.13.1 What Must Be Logged

Security/audit events:

- login success/failure,
- token validation failures,
- access denied,
- privileged action,
- role/group/app-role assignment change,
- data export,
- document download,
- approval decision,
- admin configuration change,
- secret/key access events,
- integration failures,
- policy exceptions.

Include:

- actor,
- action,
- target resource,
- timestamp,
- source IP/device where appropriate,
- correlation ID,
- outcome,
- reason/error code,
- approver where relevant.

### 4.13.2 What Must Never Be Logged

Never log:

- passwords,
- access tokens,
- refresh tokens,
- private keys,
- client secrets,
- full connection strings,
- OTP/MFA codes,
- raw sensitive documents,
- unnecessary PII.

Redact:

- national IDs,
- employee IDs where not needed,
- salary values,
- medical/leave details,
- phone/email depending on context.

### 4.13.3 Tamper-Evident Audit Trails

Government systems may require stronger audit integrity:

- append-only logs,
- immutable storage,
- restricted write/delete permissions,
- hash chaining or signing for high assurance,
- separate audit account/storage,
- monitored access,
- retention/legal hold.

### 4.13.4 Retention

Retention must balance:

- regulatory requirements,
- investigation needs,
- privacy/data minimization,
- cost,
- legal hold,
- classification.

Do not keep sensitive logs forever by default.

---

# Part C - Interview Traps

## Trap 1. "Input validation prevents SQL injection."

Better answer: input validation helps, but SQL injection is primarily prevented by
parameterized queries/safe APIs. Validation is an additional control.

## Trap 2. "Authentication means authorization."

Better answer: authentication proves identity. Authorization checks action/resource/context.
Most API breaches happen because authenticated users can access objects they should not.

## Trap 3. "CORS protects the API."

Better answer: CORS is a browser control. Server-to-server clients ignore it. APIs still need
authentication, authorization and CSRF protection where cookies are used.

## Trap 4. "JWT validation means decode the token."

Better answer: decoding is not validation. Validate signature, issuer, audience, expiry,
algorithm, key rotation and required claims.

## Trap 5. "Kubernetes secrets or app settings are secret management."

Better answer: they can store values, but enterprise secret management needs Key Vault or
equivalent, managed identity, RBAC, rotation, audit and no leakage into code/images/logs.

## Trap 6. "Encryption solves data protection."

Better answer: encryption helps confidentiality, but access control, key management, logging,
data minimization, retention and monitoring are also required.

## Trap 7. "WAF fixes insecure code."

Better answer: WAF is defense in depth. It can reduce common attack traffic, but the app still
needs secure design, validation, authorization and patching.

