# Part 3.1 - Docker

*Two layers: **Part A** is the build narrative. **Part B** is the complete reference. **Part C**
is the interview pressure test.*

---

# Part A - THE BUILD: From Source To Secure Image

## Step 1. The first container works, but it is too big

The Python API runs in Docker, but the first image includes build tools, package caches, test
dependencies and source files that are not needed at runtime. It works, but it is slow to
build, slow to pull and larger than the security team will accept.

We switch to a **multi-stage build**: one stage compiles/tests, the final stage carries only
runtime artifacts.

> Reference: [3.1.1 Multi-stage builds](#311-multi-stage-builds)

## Step 2. Builds are slow because the cache is wasted

Every source change invalidates dependency installation because the Dockerfile copies the whole
repo before restoring packages. We reorder layers so dependency manifests are copied before
application source.

> Reference: [3.1.2 Layer caching](#312-layer-caching)

## Step 3. The runtime image must be smaller and safer

We choose minimal runtime images: slim, distroless or chiseled depending on language/runtime
support and operational needs. The goal is not "smallest at any cost"; it is enough runtime,
fewer packages, fewer CVEs and predictable debugging strategy.

> Reference: [3.1.3 Image size and base images](#313-image-size-and-base-images)

## Step 4. Containers should not run as root

The container starts as root by default. That is unacceptable for production. We create a
non-root user, make the filesystem read-only where possible, drop Linux capabilities and mount
writable paths explicitly.

> Reference: [3.1.4 Runtime hardening](#314-runtime-hardening)

## Step 5. Images need provenance

The platform pushes images to Azure Container Registry. CI scans images, generates an SBOM,
signs or attests artifacts, and deploys by immutable digest rather than mutable `latest`.

> Reference: [3.1.5 Image scanning, signing and registry hygiene](#315-image-scanning-signing-and-registry-hygiene)

---

# Part B - THE REFERENCE

## 3.1.1 Multi-Stage Builds

Multi-stage builds separate build-time dependencies from runtime dependencies.

Bad shape:

```dockerfile
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "-m", "app"]
```

Problems:

- build tools stay in the runtime image,
- tests and caches may be copied,
- image is large,
- attack surface is larger,
- cache invalidation is poor.

Better shape:

```dockerfile
FROM python:3.12-slim AS build
WORKDIR /build
COPY requirements.txt .
RUN pip wheel --wheel-dir /wheels -r requirements.txt
COPY . .
RUN python -m pytest

FROM python:3.12-slim AS runtime
WORKDIR /app
RUN useradd --create-home --uid 10001 appuser
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/*
COPY --from=build /build/app ./app
USER appuser
CMD ["python", "-m", "app"]
```

Benefits:

- final image contains only runtime needs,
- build dependencies stay out,
- tests can gate the image build,
- smaller images pull faster,
- fewer packages means fewer vulnerability findings.

Senior note: multi-stage builds are not only for compiled languages. They are useful for
Python, Node and .NET because restore/build/test assets can be separated from runtime.

## 3.1.2 Layer Caching

Docker builds are layer-based. If one layer changes, following layers are rebuilt. Cache-aware
Dockerfiles put stable, expensive steps before frequently changing source files.

### 3.1.2.1 Cache-Friendly Node Example

Bad:

```dockerfile
COPY . .
RUN npm ci
```

Any source change invalidates dependency install.

Better:

```dockerfile
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build
```

Now dependency install reruns only when dependency manifests change.

### 3.1.2.2 Cache-Friendly .NET Example

```dockerfile
COPY src/App/App.csproj src/App/
RUN dotnet restore src/App/App.csproj
COPY . .
RUN dotnet publish src/App/App.csproj -c Release -o /out
```

### 3.1.2.3 Cache Controls

Good practices:

- use `.dockerignore`,
- copy dependency manifests first,
- keep build context small,
- pin base image versions or digests where policy requires,
- use BuildKit cache mounts for package managers,
- avoid secrets in build args,
- rebuild base images regularly for patches.

Common mistake:

```dockerfile
RUN apt-get update
RUN apt-get install -y curl
```

Better:

```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
```

## 3.1.3 Image Size And Base Images

Image size affects:

- pull time,
- node startup time,
- storage,
- CVE count,
- attack surface,
- scanning noise.

### 3.1.3.1 Base Image Options

| Base image type | Best fit | Tradeoffs |
|---|---|---|
| Full distro | debugging-heavy environments | larger attack surface |
| Slim | common production default | smaller but still shell/package-manager capable |
| Alpine | very small Linux base | musl compatibility issues for some workloads |
| Distroless | minimal runtime only | harder interactive debugging |
| Chiseled | minimal Ubuntu-style runtime for supported stacks | less shell/debug tooling; good security posture |
| Scratch | static binaries | very limited; only when app can run with nothing else |

Senior answer:

"I do not pick the smallest image blindly. I choose a trusted, supported, minimal runtime that
the team can patch and debug. For production, I prefer small images plus good observability
over relying on shell access inside containers."

### 3.1.3.2 Image Size Checklist

- Remove package-manager caches.
- Do not copy tests/docs/build caches into runtime.
- Use multi-stage builds.
- Use production dependency install modes.
- Avoid unnecessary OS packages.
- Use `.dockerignore`.
- Prefer runtime images over SDK/build images.
- Inspect layers with `docker history` or build tooling.

## 3.1.4 Runtime Hardening

Container hardening reduces blast radius if the application is compromised.

### 3.1.4.1 Non-Root Users

Containers often run as root unless changed. Running as non-root limits what an attacker can do
inside the container and on mounted filesystems.

Dockerfile:

```dockerfile
RUN useradd --create-home --uid 10001 appuser
USER 10001
```

Kubernetes:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  allowPrivilegeEscalation: false
```

### 3.1.4.2 Read-Only Filesystems

Use a read-only root filesystem when the app can support it:

```yaml
securityContext:
  readOnlyRootFilesystem: true
```

Mount only required writable paths:

- `/tmp`,
- upload staging directory,
- app-specific cache,
- mounted secret volume.

### 3.1.4.3 Capability Dropping

Linux capabilities split root privileges. Most web apps do not need extra capabilities.

```yaml
securityContext:
  capabilities:
    drop:
      - ALL
```

Add back only what is required and justified.

### 3.1.4.4 Other Runtime Controls

- no privileged containers,
- no host PID/IPC/network unless justified,
- seccomp profile,
- AppArmor where available,
- resource requests/limits,
- health probes,
- no secrets in environment variables when stronger options exist,
- mount service-account tokens only when needed.

## 3.1.5 Image Scanning, Signing And Registry Hygiene

### 3.1.5.1 Image Scanning

Scanning finds known vulnerabilities and misconfigurations.

Tools:

- Trivy in local/CI scans,
- Microsoft Defender for Containers/Cloud,
- registry scanning,
- admission/gated deployment controls.

Where to scan:

```text
Pull request: dependency and Dockerfile checks
CI build: image scan before push
Registry: continuous scan after new CVEs
Admission: block critical policy violations
Runtime: detect drift and vulnerable running images
```

Scanning rules:

- fail builds on critical/high findings according to policy,
- allow time-boxed exceptions with owner and expiry,
- scan base images regularly,
- rescan when new CVEs are published,
- do not treat "scanner clean" as "secure."

### 3.1.5.2 SBOM

An SBOM lists components and versions in the image. Use it for:

- vulnerability response,
- vendor assurance,
- license review,
- incident investigation,
- release governance.

Formats/tools vary, but CycloneDX and SPDX are common in the ecosystem.

### 3.1.5.3 Signing And Attestation

Signing answers: "Was this artifact produced by a trusted identity and not modified?"

Attestation/provenance answers: "Where and how was this built?"

Options:

- Cosign/Sigstore,
- Notary Project,
- GitHub artifact attestations,
- Azure ecosystem signing/provenance controls.

Important current point: Docker Content Trust/Notary v1 has deprecation timelines in Azure
Container Registry, so be ready to discuss transition toward Notary Project or Sigstore-style
approaches rather than relying only on legacy DCT.

### 3.1.5.4 Azure Container Registry

ACR hygiene:

- private registry with RBAC,
- disable admin user unless specifically justified,
- use managed identity/service principal with least privilege,
- use `AcrPull` for pull, `AcrPush` for CI push,
- separate dev/test/prod registries or repositories where governance requires,
- retention policies for old manifests,
- quarantine or promotion flow,
- private endpoint for restricted environments,
- geo-replication where needed,
- deploy by digest, not mutable tags.

### 3.1.5.5 Tags vs Digests

Tags are mutable labels:

```text
myacr.azurecr.io/portal-api:prod
```

Digests identify immutable content:

```text
myacr.azurecr.io/portal-api@sha256:abc123...
```

Production deployments should record or deploy by digest so rollback and audit know exactly
what ran.

---

# Part C - Interview Traps

## Trap 1. "Multi-stage builds are only for compiled languages."

Better answer: they help any stack where build/test dependencies differ from runtime
dependencies. Python, Node and .NET all benefit.

## Trap 2. "Use Alpine for everything because it is small."

Better answer: Alpine is small, but musl compatibility and debugging can be issues. I choose a
trusted, supported, minimal base that fits the runtime and operating model.

## Trap 3. "A container is secure because it is isolated."

Better answer: containers share the host kernel. I still run non-root, drop capabilities, avoid
privileged mode, use read-only filesystems, set resource limits and enforce admission policies.

## Trap 4. "Image scanning happens only in CI."

Better answer: CI scanning catches known issues before push, but images must be rescanned when
new CVEs appear. Registry/runtime scanning and admission policies complete the control.

## Trap 5. "latest is fine because the pipeline updates it."

Better answer: mutable tags are weak for audit and rollback. I can tag for readability, but
production should record or deploy immutable digests.

