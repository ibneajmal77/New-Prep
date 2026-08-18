# Part 4 - Secure Development: Interview Questions And Model Answers

Use this after `40-Part4-Secure-Development.md`. Practise aloud until the answers sound like
design judgment, not memorized security labels.

---

# Secure Coding Basics

## Q1. Allow-list or deny-list validation?

Allow-list. I define what valid input looks like: length, type, format, enum values and
business rules. Deny-lists are weak because attackers can find encodings and bypasses. I may
use deny-lists as a secondary control, but the primary approach is allow-list validation after
canonicalization.

## Q2. What is canonicalization?

It is converting input to a standard representation before validation. For example, decoding
URL-encoded characters, normalizing Unicode and resolving path forms. Without canonicalization,
I may block `../secret` but accept an encoded equivalent.

## Q3. Client-side validation or server-side validation?

Client-side validation is for UX. Server-side validation is the security boundary. Attackers
can bypass browser code, hidden fields and disabled controls, so the server must enforce all
syntactic and semantic rules.

## Q4. How do you secure file uploads?

Use allow-listed extensions, content-type and file signature checks, size limits, generated
filenames, private storage outside web root, malware scanning, CDR where required, archive bomb
protection, authorization on upload/download, CSRF protection and audit logging. Never trust
the user-provided filename or storage path.

## Q5. How do you prevent SQL injection?

Use parameterized queries, prepared statements or ORM parameter binding. Do not concatenate
user input into SQL. For dynamic sorting/filtering, map client options to an allow-list of
known columns. Use least-privilege database accounts as defense in depth.

## Q6. What is command injection prevention?

Avoid shell execution. Use library APIs where possible. If a command is required, pass
arguments as an array, allow-list options, do not invoke a shell, run as low privilege, set
timeouts and isolate execution.

## Q7. Stored vs reflected vs DOM XSS?

Stored XSS is saved and shown later. Reflected XSS is echoed in the response immediately. DOM
XSS happens when browser-side JavaScript writes untrusted data into unsafe sinks like
`innerHTML`. All need context-aware output encoding; DOM XSS also needs safe client-side APIs.

## Q8. What is context-aware output encoding?

Encoding depends on where data is placed: HTML body, attribute, JavaScript, URL or CSS. One
generic sanitizer is not enough. I use framework escaping, avoid dangerous sinks and use a
proven sanitizer only when rich HTML is allowed.

## Q9. What does CSP do?

CSP restricts where scripts, styles, frames and other resources can load from. It reduces XSS
and clickjacking exploitability, especially with nonces/hashes and `frame-ancestors`. It is
defense in depth, not a replacement for output encoding.

---

# Authentication And Entra

## Q10. OAuth 2.0 vs OIDC?

OAuth 2.0 is for delegated authorization to APIs. OIDC adds identity on top of OAuth and gives
the client an ID token. APIs should normally validate access tokens, not ID tokens, for
authorization.

## Q11. Which OAuth flow for a SPA?

Authorization code flow with PKCE. Implicit flow is legacy and not recommended for new SPAs
because of token leakage risks. PKCE protects the code exchange for public clients.

## Q12. Which OAuth flow for service-to-service?

Client credentials, preferably using managed identity in Azure rather than a stored client
secret. It is app-only access, so permissions must be least privilege and not confused with a
user's delegated permissions.

## Q13. Why is ROPC bad?

ROPC makes the app handle the user's password directly. It does not support modern controls
like MFA/Conditional Access in normal production scenarios and requires too much trust in the
application. I would avoid it except tightly controlled testing/legacy cases where no safer
flow exists.

## Q14. What must an API validate in a JWT?

Signature, issuer, audience, expiration, not-before where used, algorithm, token type/use, key
ID/signing key rotation and required claims such as scopes or roles. Decoding a JWT is not
validation.

## Q15. What is refresh token rotation?

A refresh token obtains new access tokens. When a new refresh token is issued, the app should
store it securely and delete the old one. Refresh tokens are sensitive and must be protected
like credentials.

## Q16. App registration vs enterprise application?

An app registration is the application definition: client ID, redirect URIs, scopes, app roles,
credentials and owners. The enterprise application is the tenant-local service principal used
for assignment, SSO, Conditional Access, provisioning and admin consent.

## Q17. App roles vs groups vs scopes?

Scopes represent delegated API permissions and appear in `scp`. App roles represent
application-defined roles and appear in `roles`. Groups are tenant memberships. A good pattern
is to define app-level permissions with scopes/app roles and assign users or groups to those
roles.

## Q18. What is Conditional Access?

Conditional Access evaluates signals such as user, group, app, device, location, risk and
workload identity, then enforces controls such as MFA, compliant device, block or session
restrictions. It is central to Entra security governance.

## Q19. Managed identity?

Managed identity gives an Azure resource an Entra identity without storing credentials. I use
it for App Service, Functions, AKS workloads or VMs calling Key Vault, Storage, Service Bus or
Azure APIs.

## Q20. B2B vs B2C/External ID?

B2B is for collaboration with partners and guests in a workforce tenant. B2C/External ID style
patterns are for citizen/customer-facing identity. I would not mix employee and citizen trust
models casually.

## Q21. What is SCIM provisioning?

SCIM automates user/group provisioning and deprovisioning between identity systems and
applications. It helps maintain account lifecycle, especially when HR or group assignments
change.

---

# Authorization

## Q22. Authentication vs authorization?

Authentication proves who the caller is. Authorization decides whether that caller can perform
this action on this resource in this context. Most serious API bugs are authorization bugs, not
login bugs.

## Q23. RBAC vs ABAC vs ReBAC?

RBAC grants permissions through roles. ABAC uses attributes like department, grade, location or
classification. ReBAC uses relationships like manager-of, owner-of or delegate-for. Real
enterprise systems often combine them.

## Q24. What is IDOR/BOLA?

Broken object-level authorization happens when an authenticated user changes an object ID and
accesses another user's record. The fix is object-level authorization on every access, not just
hidden UI buttons or route-level role checks.

## Q25. How do you enforce tenant or business-unit isolation?

Include tenant/BU context in every query and authorization check, derive it from trusted
identity/session context, never trust client-supplied tenant IDs, include tenant/user in cache
keys, test cross-tenant access and use database row-level security where appropriate.

## Q26. What is broken object property authorization?

The user may access the object but not every field. For example, an HR officer may see leave
status but not salary or medical details. Responses and updates must enforce field/property
level rules.

---

# OWASP And Web Risks

## Q27. Name OWASP Top 10 2021.

Broken Access Control, Cryptographic Failures, Injection, Insecure Design, Security
Misconfiguration, Vulnerable and Outdated Components, Identification and Authentication
Failures, Software and Data Integrity Failures, Security Logging and Monitoring Failures, and
SSRF.

## Q28. What is special about OWASP API Top 10?

It emphasizes API-specific authorization and business-flow risks: BOLA, broken auth, object
property authorization, resource consumption, function-level authorization, sensitive business
flows, SSRF, misconfiguration, inventory and unsafe consumption of APIs.

## Q29. What is CSRF?

CSRF tricks a browser into sending an authenticated state-changing request using existing
cookies. Controls include CSRF tokens, SameSite cookies, custom headers with strict CORS,
step-up auth for sensitive actions and never using GET for state changes.

## Q30. What is SSRF and how do you prevent it?

SSRF makes the server request attacker-controlled URLs. Prevent with destination allow-lists,
DNS/final-IP validation, blocking private/internal ranges where not needed, egress firewall,
timeouts, response size limits, careful redirect handling and never sending credentials to
arbitrary URLs.

## Q31. What is a dangerous CORS config?

Reflecting arbitrary origins or using wildcard origins with credentials. CORS is only a browser
control, not API authorization. Use exact trusted origins, restrict methods/headers and enforce
normal authz on the server.

## Q32. How do you prevent clickjacking?

Use CSP `frame-ancestors` and optionally `X-Frame-Options` for older compatibility. Sensitive
pages should not be frameable unless explicitly required.

## Q33. Which security headers matter?

HSTS, CSP, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`,
`frame-ancestors` in CSP and secure cookie attributes like HttpOnly, Secure and SameSite.

---

# Secrets, Crypto And Network

## Q34. What belongs in Key Vault?

Secrets, keys and certificates: API keys, connection strings, certificates, encryption keys and
client secrets where managed identity is not possible. Access should use RBAC, managed
identity, private endpoints where required, rotation and auditing.

## Q35. What should never be in code or CI logs?

Passwords, access tokens, refresh tokens, private keys, client secrets, connection strings,
storage keys, OTP/MFA codes and sensitive documents. If exposed, rotate immediately and
investigate use.

## Q36. TLS vs mTLS?

TLS authenticates the server and encrypts traffic. mTLS authenticates both client and server
with certificates. mTLS is useful for high-trust service-to-service or partner APIs but adds
certificate lifecycle complexity.

## Q37. CMK vs PMK?

PMK means platform-managed key. CMK means customer-managed key, usually in Key Vault or managed
HSM. CMK gives more control and may satisfy regulatory requirements but adds operational
responsibility around access, rotation and availability.

## Q38. How should passwords be stored?

Use slow password hashing such as Argon2id, bcrypt, scrypt or PBKDF2 with unique salts and
appropriate work factor. Do not encrypt passwords or use fast hashes like SHA-256 alone.

## Q39. Private endpoint vs VNet integration?

Private endpoint gives an Azure service a private IP in your VNet for private inbound access
to that service. VNet integration lets a service like App Service make outbound calls into a
VNet. They solve different directions of connectivity.

## Q40. WAF vs DDoS protection?

WAF protects HTTP/S applications against application-layer patterns like XSS and SQLi. DDoS
protection handles volumetric/network-layer availability attacks. They complement each other.

## Q41. What does zero trust mean practically?

Verify explicitly, use least privilege and assume breach. In practice: authenticate every
request, authorize per resource, use managed identities, segment networks, restrict egress,
monitor continuously and audit privileged actions.

---

# SDLC And Audit

## Q42. How do you threat model with STRIDE?

Draw the data flow diagram, mark trust boundaries, then examine spoofing, tampering,
repudiation, information disclosure, denial of service and elevation of privilege for each
component/flow. Capture mitigations and residual risk.

## Q43. What are good DevSecOps gates?

SAST, dependency scanning, secret scanning, IaC scanning, container scanning, DAST in deployed
test/staging, threat-model review for high-risk changes and manual approval for security
exceptions with expiry.

## Q44. How do you handle pen-test findings?

Triage severity, assign owner, reproduce, fix root cause, add regression tests/controls,
retest, document evidence and close with security approval. Do not just patch symptoms.

## Q45. What are vulnerability SLAs?

Time targets for remediation based on severity and exploitability, such as critical in 24-72
hours, high in 7-14 days, medium in a planned sprint and low in backlog review. Actual numbers
come from organization policy.

## Q46. What must be logged for audit?

Actor, action, target resource, timestamp, source context, correlation ID, outcome, reason,
approval identity where relevant, access denied, privileged changes, document downloads, data
exports and admin configuration changes.

## Q47. What must never be logged?

Passwords, tokens, private keys, client secrets, full connection strings, OTP/MFA codes, raw
sensitive documents and unnecessary PII. Sensitive fields should be redacted or hashed where a
stable identifier is needed.

## Q48. What is a tamper-evident audit trail?

An audit trail designed so modification or deletion is detectable: append-only storage,
immutable retention, restricted delete permissions, separate audit account/storage, hash
chaining or signing for high assurance, and monitored access.

## Q49. How long should logs be retained?

Based on regulation, investigation needs, privacy, data minimization and cost. Security audit
logs may need longer retention than debug logs. Keeping sensitive logs forever by default is
bad security and bad governance.

## Q50. How would you summarize secure development to a government panel?

I would secure the whole lifecycle: validate inputs, prevent injection with safe APIs, encode
outputs, use Entra with modern OAuth/OIDC flows, enforce object-level authorization, manage
secrets in Key Vault with managed identity, protect networks with private endpoints/WAF/DDoS,
build DevSecOps gates, threat model high-risk changes and maintain safe, tamper-evident audit
logs.

