# Part 1.4 - Frontend: React And Modern Web

*Two layers: **Part A** is the build narrative. **Part B** is the complete reference. **Part C**
is the interview pressure test.*

---

# Part A - THE BUILD: The Bilingual Portal

## Step 1. The first screen is not a landing page

Employees open the portal to submit leave, request letters, check approvals and view
notifications. This is an operational government system, so the UI should be efficient,
accessible and bilingual, not marketing-heavy.

We choose **Next.js with React** because we need:

- server-rendered pages for fast first load,
- client interactivity where workflows need it,
- route-level architecture,
- caching controls,
- code splitting,
- accessibility discipline,
- Arabic/English routing and formatting.

> Reference: [1.4.1 React 19](#141-react-19)

## Step 2. Server rendering reduces blank-page risk

The dashboard should render useful HTML quickly. React Server Components and Next.js App Router
let server-only data access and server-rendered UI coexist with client components for forms,
filters and real-time interactions.

> Reference: [1.4.3 Next.js 15 App Router](#143-nextjs-15-app-router)

## Step 3. State must be divided by ownership

The leave balance is server state. The open/closed state of a filter panel is client UI state.
The current authenticated user may be app/session state. Mixing all of that into one global
store creates unnecessary complexity.

> Reference: [1.4.2 State management](#142-state-management)

## Step 4. Accessibility is a requirement, not a polish pass

Government systems must work for keyboard users, screen readers, low vision users and people
using assistive technologies. WCAG 2.1/2.2 AA concepts should be baked into component design,
not tested only at the end.

> Reference: [1.4.6 Accessibility and WCAG AA](#146-accessibility-and-wcag-aa)

## Step 5. Arabic/RTL changes layout, not just words

Arabic is not an afterthought translation. Direction, spacing, icons, typography, dates,
numbers, validation messages and document names all change.

> Reference: [1.4.7 Arabic, RTL and bilingual UI](#147-arabic-rtl-and-bilingual-ui)

## Step 6. Performance is measured at the user edge

The portal may be used from different devices and networks. We optimize Core Web Vitals,
hydration cost, bundle size and caching behavior, then enforce budgets in CI.

> Reference: [1.4.5 Performance](#145-performance)

---

# Part B - THE REFERENCE

## 1.4.1 React 19

React is a UI library. Modern React architecture is less about "components only" and more
about deciding what runs on the server, what runs in the browser, and where data ownership
lives.

### 1.4.1.1 Server Components

React Server Components render on the server and do not ship their component code to the
browser. In frameworks such as Next.js App Router, they are useful for:

- reading server-side data,
- reducing client JavaScript,
- keeping secrets and database access off the browser,
- rendering stable page structure.

Use server components for:

- dashboards,
- read-heavy detail pages,
- navigation shells,
- content assembled from server data.

Use client components for:

- event handlers,
- browser APIs,
- local interactive state,
- forms with dynamic behavior,
- drag/drop and rich widgets.

Senior point: server components are not an API security boundary by themselves. Authorization
must still happen on the server data access path.

### 1.4.1.2 Suspense

`Suspense` lets a component tree show fallback UI while async work is loading. It is useful
with streaming and route-level loading states.

Good usage:

- skeletons for slow panels,
- split dashboard sections,
- stream stable shell first, then slower content,
- avoid blocking an entire page for one slow widget.

Poor usage:

- wrapping everything in one giant fallback,
- layout shift caused by unstable fallback dimensions,
- hiding errors instead of designing error boundaries.

### 1.4.1.3 Concurrent Rendering

Concurrent rendering lets React interrupt, pause and resume rendering work to keep the UI
responsive. It is an implementation capability used by features such as transitions and
Suspense.

Interview phrasing:

"Concurrent rendering does not mean my code runs in parallel threads. It means React can
prioritize rendering work and avoid blocking urgent updates."

### 1.4.1.4 Hooks Rules

Rules:

- call hooks only at the top level of React functions,
- do not call hooks inside loops, conditions or nested functions,
- call hooks only from React components or custom hooks.

Why: React relies on consistent hook call order between renders.

### 1.4.1.5 `useMemo` / `useCallback` Misuse

These hooks are performance tools, not defaults.

Use them when:

- expensive computation is repeated,
- referential stability prevents child re-renders,
- dependency arrays are well understood,
- profiling shows benefit.

Avoid them when:

- computation is cheap,
- dependencies change every render anyway,
- they make code harder to read,
- they mask poor component boundaries.

Senior answer: unnecessary memoization can add cognitive cost and sometimes runtime overhead.
Measure before spreading it everywhere.

## 1.4.2 State Management

Classify state before choosing a tool.

| State type | Examples | Best fit |
|---|---|---|
| Server state | leave balance, profile, approvals, search results | React Query, RTK Query, framework loaders/server components |
| Client UI state | modal open, selected tab, draft filter | local component state |
| Cross-page app state | locale, theme, auth shell, feature flags | context or small store |
| Complex client workflow | multi-step wizard, offline queue, rich editor | Redux Toolkit, Zustand or state machine |
| Cached API state with mutations | entity lists, invalidation, optimistic updates | React Query or RTK Query |

### Redux Toolkit

Use when:

- client-side state transitions are complex,
- many components need the same state,
- debugging state history matters,
- app has established Redux patterns.

Avoid for every API response if a server-state tool handles caching/invalidation better.

### React Query / TanStack Query

Use for server state:

- caching,
- refetching,
- stale time,
- mutations,
- retries,
- optimistic updates,
- invalidation.

Great for API-driven portals.

### RTK Query

Use when:

- the app already uses Redux Toolkit,
- API cache should integrate with Redux,
- generated endpoints and tags fit the team style.

### Context

Use for stable, low-frequency app-wide values:

- locale,
- theme,
- current user shell,
- feature flags.

Avoid putting frequently changing large state in one context because it can cause broad
re-renders.

## 1.4.3 Next.js 15 App Router

Next.js App Router organizes routes using the `app/` directory and supports server components,
layouts, route groups, loading states, error boundaries and server actions.

### 1.4.3.1 SSR, SSG And ISR

| Rendering strategy | Use when | Example |
|---|---|---|
| SSR | request-time user-specific data | employee dashboard |
| SSG | content is same for all users and rarely changes | public help pages |
| ISR | static content updates periodically or on demand | service catalogue, policy summaries |

For authenticated government portals, SSR/server components are common because user-specific
permissions and data matter.

### 1.4.3.2 Edge Runtime

Edge runtime can reduce latency for lightweight logic near the user, but has constraints:

- limited Node APIs,
- runtime/package compatibility limits,
- database connection concerns,
- observability differences,
- security review for regional/data residency requirements.

Use it for:

- simple redirects,
- lightweight personalization,
- geolocation/routing,
- headers and auth edge checks where supported.

Be cautious for:

- heavy business logic,
- direct database access,
- complex SDKs,
- data residency-sensitive operations.

### 1.4.3.3 Caching Layers

Modern Next.js has multiple cache concepts:

- browser cache,
- CDN cache,
- route segment caching,
- fetch/data cache,
- router cache,
- application cache,
- backend/API cache.

Next.js 15 made caching more explicit in important areas. Do not assume every `fetch` is
cached by default; choose caching behavior deliberately with framework options and headers.

Questions to ask:

- Is the data public or user-specific?
- Can it be cached across users?
- How stale may it be?
- What invalidates it?
- Does authorization affect it?
- Which layer should own the cache?

### 1.4.3.4 Server Actions

Server Actions can submit mutations from React components to server functions. Use them for
simple form-style mutations where the framework pattern fits.

Be careful:

- validate input on the server,
- authorize the action,
- enforce idempotency for risky writes,
- handle errors accessibly,
- do not put secrets in client components.

## 1.4.4 Micro-Frontends And Module Federation

Micro-frontends split a frontend into independently deployable parts, often owned by different
teams. Module Federation is a common mechanism for loading separately built frontend modules.

Use when:

- multiple teams own different domains,
- independent deployment is necessary,
- a large portal has clear domain boundaries,
- shared shell and design system are mature,
- governance can manage versioning and accessibility consistency.

Avoid when:

- one team owns the whole app,
- the system is still discovering its domain boundaries,
- shared dependency/version conflicts would dominate,
- accessibility and design consistency are not mature,
- runtime integration risk is higher than deployment benefit.

Answer to "Why not just a monolith SPA?":

"A monolith SPA is often the better starting point. I would introduce micro-frontends only when
team autonomy and deployment independence are worth the complexity: shared design system,
routing contracts, dependency governance, auth propagation, observability and failure
isolation."

## 1.4.5 Performance

### 1.4.5.1 Core Web Vitals

Key metrics:

- **LCP:** largest contentful paint; measures loading experience.
- **INP:** interaction to next paint; measures responsiveness.
- **CLS:** cumulative layout shift; measures visual stability.

Practical controls:

- optimize server response time,
- preload critical assets carefully,
- reduce render-blocking resources,
- compress and cache static assets,
- use responsive images,
- reserve dimensions for images and dynamic content,
- avoid expensive client-side rendering for first paint.

### 1.4.5.2 Bundle Splitting

Do:

- split by route,
- lazy-load rare heavy components,
- audit dependency size,
- avoid shipping server-only code to the client,
- prefer native browser capabilities where sufficient.

Do not:

- import giant date/chart libraries into the root layout casually,
- ship admin-only code to normal users,
- duplicate dependencies across micro-frontends without governance.

### 1.4.5.3 Hydration Cost

Hydration is the browser attaching React behavior to server-rendered HTML. Too much client
JavaScript can delay interactivity.

Controls:

- keep components server-side by default,
- mark client components only where interaction is needed,
- move heavy logic off the critical path,
- stream sections,
- use partial loading/skeletons,
- measure INP and long tasks.

### 1.4.5.4 Lighthouse CI

Use Lighthouse CI or similar tooling to enforce budgets:

- performance score,
- accessibility score,
- bundle size,
- Core Web Vitals lab signals,
- unused JavaScript,
- image optimization.

Senior note: Lighthouse lab tests are not enough. Combine them with real-user monitoring.

## 1.4.6 Accessibility And WCAG AA

WCAG is organized around **POUR**:

- **Perceivable:** users can perceive content.
- **Operable:** users can operate controls.
- **Understandable:** UI and errors are clear.
- **Robust:** works with assistive technologies.

### 1.4.6.1 WCAG 2.1/2.2 AA Practical Checklist

- Keyboard access for all interactive controls.
- Visible focus indicators.
- Correct heading structure.
- Sufficient contrast.
- Labels for form fields.
- Error messages tied to inputs.
- No color-only meaning.
- Responsive zoom support.
- Skip links where useful.
- Language attributes on pages/sections.
- Motion reduction support.
- Screen-reader testing for core workflows.

### 1.4.6.2 ARIA

Use semantic HTML first:

- `button` for buttons,
- `a` for navigation,
- `label` for inputs,
- `fieldset`/`legend` for grouped controls,
- headings in order.

Use ARIA when native semantics are insufficient:

- custom combobox,
- tabs,
- modal dialog,
- live region,
- disclosure widget.

Bad ARIA can make accessibility worse. Do not add `role="button"` to a `div` when a real
`button` works.

### 1.4.6.3 Keyboard Navigation

Expected behavior:

- `Tab` moves through focusable controls in logical order,
- `Enter` and `Space` activate buttons,
- `Esc` closes modals/menus,
- arrow keys work in menus/tabs/grids where expected,
- focus is trapped inside modal dialogs,
- focus returns to the triggering control when a modal closes.

### 1.4.6.4 Contrast Ratios

Know the common AA targets:

- normal text: 4.5:1,
- large text: 3:1,
- non-text UI indicators: 3:1.

Always verify with tools because perceived contrast can be misleading.

### 1.4.6.5 Screen-Reader Testing

Test at least:

- page title,
- heading navigation,
- landmark navigation,
- form labels and errors,
- dynamic updates,
- modals,
- language switching,
- Arabic text direction.

Tools:

- NVDA on Windows,
- VoiceOver on macOS/iOS,
- browser accessibility tree,
- axe/Playwright checks as automation support.

Automation catches many issues, but not all workflow comprehension issues.

## 1.4.7 Arabic, RTL And Bilingual UI

Arabic support is a product and architecture requirement.

### 1.4.7.1 Direction

Set direction at the document or route level:

```html
<html lang="ar" dir="rtl">
```

For English:

```html
<html lang="en" dir="ltr">
```

Use `dir="auto"` for user-generated mixed text where appropriate.

### 1.4.7.2 Logical CSS Properties

Prefer logical properties:

```css
.card {
  margin-inline-start: 1rem;
  padding-inline: 1rem;
  border-start-start-radius: 0.5rem;
}
```

Instead of physical left/right:

```css
.card {
  margin-left: 1rem;
}
```

Logical properties adapt to RTL/LTR.

### 1.4.7.3 Mirrored Icons

Directional icons often need mirroring:

- back/forward arrows,
- chevrons,
- progress indicators,
- stepper direction,
- breadcrumbs.

Do not mirror icons with fixed meaning:

- play icon,
- download,
- external link,
- check mark,
- information icon.

### 1.4.7.4 Arabic Fonts

Arabic needs fonts designed for Arabic reading, not fallback glyphs. Check:

- legibility at small sizes,
- line height,
- diacritics,
- mixed Arabic/English numbers,
- weight availability,
- performance of webfont loading.

### 1.4.7.5 i18n Resource Strategy

Use resource files/translation keys, not inline conditional text.

Good practices:

- key by meaning, not English sentence when possible,
- support pluralization,
- keep validation messages translatable,
- avoid concatenating translated fragments,
- localize emails and PDFs too,
- test long Arabic labels and longer English labels.

### 1.4.7.6 Dates, Numbers And Calendars

Use locale-aware formatting:

- Arabic numerals vs Latin digits depending on requirement,
- Gregorian and Hijri calendar expectations,
- local time zone,
- date order,
- currency formatting,
- percent formatting,
- right-to-left embedding around mixed text.

Do not format dates manually with string concatenation.

### 1.4.7.7 Forms

Arabic form details:

- labels align naturally with direction,
- validation summary reads in the right order,
- phone and ID fields may remain LTR,
- placeholders are not labels,
- mixed-direction names need testing,
- table column order may need redesign, not simple reversal.

---

# Part C - Interview Traps

## Trap 1. "React Server Components mean no API security needed."

Better answer: server components reduce client JavaScript and keep server-only code off the
browser, but authorization must still be enforced on the server data access path. Never rely on
UI visibility for security.

## Trap 2. "Put all state in Redux."

Better answer: classify state first. Server state usually belongs in React Query/RTK Query or
framework data loading. Local UI state belongs near the component. Redux Toolkit is useful for
complex shared client workflows, not every API response.

## Trap 3. "Micro-frontends are more scalable."

Better answer: organizationally scalable, not automatically technically simpler. They add
runtime integration, dependency versioning, design consistency, accessibility governance and
observability complexity. A modular monolith SPA is often better until team boundaries justify
the cost.

## Trap 4. "Accessibility can be tested at the end."

Better answer: late accessibility is expensive. Component primitives, focus behavior, semantic
HTML, color tokens, form errors and keyboard support must be built in from the start.

## Trap 5. "RTL means text-align right."

Better answer: RTL affects document direction, layout flow, icons, spacing, data tables,
forms, dates, numbers, fonts and bidirectional text. Use `dir`, logical CSS and locale-aware
formatting.

