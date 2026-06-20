# Labeled Issue Dataset

Used to verify that the preflight evaluation skill's gap identification is accurate.

Each issue is labeled **good** or **bad** with annotated ground-truth gaps.
The skill should surface these gaps (or their precursors) when run against the issue content.

**Annotation perspective (v2, re-annotated 2026-06-15):** Ground-truth gaps reflect
*implementer readiness* — what a developer assigned to fix or build this would need
to resolve before writing code. Not reporter quality ("did they fill out the form?").

---

## Issue 1 — Implementer-ambiguous (previously labeled `good`)

**Title:** [React 19] Wrong `@types/react*` default version and build fails if the correct version is installed
**URL:** https://github.com/vercel/next.js/issues/65599
**Label:** `implementer-ambiguous`

### Why it's implementer-ambiguous
The issue is well-specified as a *bug report* — reproduction repo, clear symptom,
environment info, even a pinpointed root-cause area. A triager can assign it.
But an implementer hits real gaps: the ticket bundles two distinct deliverables,
the detection failure mechanism determines which code to change, and the exact
`@types/react` installation spec (npm alias vs. override) is not in the ticket.

### Ground-truth gaps (implementer perspective)
| Gap | Category | Disposition |
|-----|----------|-------------|
| Ticket conflates two deliverables: (1) fix `create-next-app` defaulting to `@types/react@^18`, and (2) fix `next build`'s detection logic rejecting an installed React-19-compatible types package. These are changes in different parts of the codebase with different owners. Which is in scope? | Scope gap | ⚠️ Needs input |
| Root cause of detection failure is unspecified. The React 19 upgrade guide installs types via an npm alias (`"@types/react": "npm:types-react@rc"`), not a standard dependency. The detection code may fail because the package resolves under a different on-disk name, or because version-range parsing rejects an `rc` string. The fix differs by root cause. | Contract gap | ⚠️ Needs input |
| The exact `package.json` spec for the installed types (overrides, resolutions, or alias) is not in the ticket — only a link to the repo. Required to reproduce and validate any detection fix, especially since the bug may be pnpm-specific (pnpm is used in the repro; npm/yarn behavior unconfirmed). | Configuration gap | ⚠️ Needs input |

**Risk level (implementer):** Medium — repro is solid, root cause area is known, but the deliverable scope and detection mechanism must be confirmed before a developer can choose the right fix.

---

## Issue 2 — Implementer-ambiguous (previously labeled `good`)

**Title:** React Refresh Bug affecting NextJS when using useClient
**URL:** https://github.com/vercel/next.js/issues/74559
**Label:** `implementer-ambiguous`

### Why it's implementer-ambiguous
Strong reproduction, upstream issue and fix PR linked. But the fix ownership
is entirely unclear (React vs. Next.js vs. dependency bump), the React version
is internally contradicted, and there's no definition of done.

### Annotation correction
The original annotation missed a genuine inconsistency: the ticket body says
`React version: 18.2.0` inline, while the environment block reports `react: 19.0.0`.
These behave differently for Fast Refresh. This is a real gap, not reporter sloppiness.

### Ground-truth gaps (implementer perspective)
| Gap | Category | Disposition |
|-----|----------|-------------|
| Fix ownership is undefined. The linked upstream React issue and fix PR (facebook/react#30660) both live in the React repo. There may be nothing to implement in the Next.js repo — the deliverable could be a dependency bump, a Next.js-side workaround, or "wait and close." A developer cannot start without knowing which. | Scope gap | ⚠️ Needs input |
| The environment block says `react: 19.0.0` but the ticket body says `React version: 18.2.0`. The affected version determines which upstream fix applies and which version to target. | Configuration gap | ⚠️ Needs input |
| "Done" is undefined. Possible outcomes include: verify the upstream fix resolves it, write a regression test, ship a Next.js-side workaround, bump the bundled React version, or close as "fixed upstream." Each is a different scope of work. | Requirements gap | ⚠️ Needs input |
| The merge/release status of PR #30660 is not stated. If the fix is already released in a React version available to Next.js, the implementation may be a dep bump or a no-op — but if unmerged, the work is blocked on an external dependency. | Dependency gap | ⚠️ Needs input |

**Risk level (implementer):** High — developer cannot determine what to build or even whether to build anything in this repo without resolving the scope and dependency gaps first.

---

## Issue 3 — Bad Quality

**Title:** Deployment Issue
**URL:** https://github.com/vercel/next.js/issues/74769
**Label:** `bad`

### Why it's bad
- Title is completely generic
- Environment info block is empty
- No error message or stack trace
- "To Reproduce" field contains "Please help me"
- Unclear whether the problem is a Next.js bug or an IIS/Windows Server configuration issue
- No version information for Next.js or dependencies

### Ground-truth gaps (implementer perspective)
| Gap | Category | Disposition |
|-----|----------|-------------|
| No reproduction steps — "Please help me" is the entire repro section. There is no failing URL, no file path, no request/response. Cannot be reproduced or verified. | Requirements gap | ⚠️ Needs input |
| No error message or stack trace. The only symptom is "images throw 404 error." The server response, IIS log, and Next.js log are all absent. | Contract gap | ⚠️ Needs input |
| Environment block is empty. Next.js version, Node version, deployment mode (standalone output, static export, `next start` behind proxy) are all unknown. Each produces a different file layout for static assets. | Configuration gap | ⚠️ Needs input |
| No Next.js or dependency versions provided. The blank canary-release checkbox is uncredible given no env info. | Configuration gap | ⚠️ Needs input |
| It is unclear whether this is a Next.js bug or an IIS/hosting misconfiguration. Static assets from `public/` are served by the running Next.js Node server, not IIS directly — unless the app was exported or IIS is configured to serve them statically. If the root cause is the hosting setup, there is no Next.js code to change. | Scope gap | ⚠️ Needs input |
| Deployment method is unspecified: `next start` + reverse proxy, `output: 'standalone'` (requires manual `public/` copy), or `output: 'export'` (static files served by IIS). Each has a different root cause for a 404 on `public/` assets. | Contract gap | ⚠️ Needs input |

**Risk level (implementer):** High — ticket is not actionable in any dimension; every field a developer needs to start work is missing.

---

## Issue 4 — Bad Quality

**Title:** Page crashes and "Error: Connection closed." in log
**URL:** https://github.com/vercel/next.js/issues/74518
**Label:** `bad`

### Why it's bad
- "Current behavior" section is copy-pasted verbatim from "To Reproduce" — no actual error described
- Error message mentioned in the title ("Error: Connection closed.") never explained or shown in the body
- Environment info is incomplete (only package versions, no OS or Node)
- The deployment platform is Netlify (`store-thing.netlify.app`), contradicting the "Vercel (Deployed)" stage tag
- "Error: Connection closed." in Next.js App Router is the signature of an RSC streaming failure, not a page/Link bug — the ticket frames the wrong layer

### Ground-truth gaps (implementer perspective)
| Gap | Category | Disposition |
|-----|----------|-------------|
| The full error message and server-side stack trace are absent. "Error: Connection closed." is quoted only in the title, with no origin, no stack, and no network trace of the failing RSC request (`?_rsc=...`). Cannot identify the failure layer without this. | Contract gap | ⚠️ Needs input |
| "Current behavior" duplicates "To Reproduce" verbatim. No actual description of what fails: no console output, no network response, no server log. | Requirements gap | ⚠️ Needs input |
| Incomplete environment info: only package versions are listed (`next: 15.1.3`, `react: ^19.0.0`). OS and Node version are absent — both are relevant to whether this is a runtime or environment-specific issue. | Configuration gap | ⚠️ Needs input |
| The live deployment is on Netlify (`store-thing.netlify.app`) but the "stage affected" says "Vercel (Deployed)." Next.js 15 RSC streaming behavior differs significantly between the Vercel-native runtime and the Netlify adapter. The developer cannot reproduce or triage without knowing the actual platform and adapter version. | Scope gap | ⚠️ Needs input |
| The ticket frames this as a `<Link>` or page bug, but "works on hard refresh, fails on client navigation" + "Error: Connection closed." is the signature of a failed RSC payload fetch during client navigation — not a routing failure. A developer who starts in the page component or Link implementation will not find the bug. The relevant layer is the RSC streaming response from the server. | Wrong mental model | ⚠️ Needs input |

**Risk level (implementer):** High — fundamental framing is misdirected (wrong layer), platform is wrong, and the error evidence is absent. All of these cause thrown-away work.

---

## Issue 5 — Borderline

**Title:** Next revalidate cache when no implicitly server indication
**URL:** https://github.com/vercel/next.js/issues/74558
**Label:** `borderline`

### Why it's borderline
Structurally complete: sandbox, full env info, clear steps, stated workaround.
But the premise is likely wrong (the "bug" is expected Next 15 behavior), and
the ticket conflates a caching behavior complaint with a DX warning feature request.

### Ground-truth gaps (implementer perspective)
| Gap | Category | Disposition |
|-----|----------|-------------|
| The ticket's premise may be incorrect. In Next 15, `fetch` is no longer cached by default — caching requires explicit opt-in (`cache: 'force-cache'` or `next: { revalidate: N }`). The reported "bug" (fresh data served) is likely expected behavior. If a developer treats this as a caching defect, they'll attempt to restore intentionally-removed behavior. | Wrong mental model | ⚠️ Needs input |
| The deliverable is undefined. The ticket simultaneously argues for fixing caching behavior AND for adding a warning message when caching is silently skipped in a client context. These are entirely different implementations. The warning interpretation (last sentence) is the more defensible ask, but neither is stated as the actual deliverable. | Requirements gap | ⚠️ Needs input |
| If the deliverable is a warning message, the trigger condition is undefined: which APIs trigger it, what counts as "used in a client context," what is the message text, and does it appear in `next dev` only or also `next build`/`next start`. | Contract gap | ⚠️ Needs input |
| The actual `product.service.ts` fetch call (its options, cache configuration, and import chain) is not shown — only a sandbox link that may expire. Without the exact fetch signature, a developer cannot determine why caching is or isn't applied or where to hook any warning. | Contract gap | ⚠️ Needs input |

**Risk level (implementer):** High — developer cannot determine what to build until the wrong-mental-model and conflated-deliverable gaps are resolved. Starting on either interpretation before confirmation risks full rework.
# Phase 2 Labeled Issue Dataset

Used to verify that the preflight evaluation skill's gap identification is accurate
across diverse issue genres: vague feature requests, dependency-blocked tickets,
API contract assumption tickets, and epic/tracking issues.

Each issue is labeled with an implementer-readiness assessment and annotated
ground-truth gaps. The skill should surface these gaps (or their precursors)
when run against the issue content.

**Annotation perspective:** Ground-truth gaps reflect *implementer readiness* —
what a developer assigned to fix or build this would need to resolve before
writing code. Not reporter quality ("did they fill out the form?").

---

## Issue 6 — Bad Quality

**Title:** Feature Request: Allow Customization of Tooltip Content in VSCode
**URL:** https://github.com/microsoft/vscode/issues/226561
**Genre:** vague-feature
**Label:** `bad`

### Why it's bad
The reporter wants tooltip customization in VS Code but proposes "a feature or API"
with no specifics on what kind of API surface, which extension points, what data model,
or any scope boundaries. Nothing is implementable as written.

### Ground-truth gaps (implementer perspective)
| Gap | Category | Disposition |
|-----|----------|-------------|
| "Customize tooltip content" is undefined — via extension API? settings? CSS? declarative config? No acceptance criteria. | Requirements gap | :warning: Needs input |
| No API surface proposed — the request is "a feature or API" with no shape, methods, events, or data model. | Contract gap | :warning: Needs input |
| "Tooltips" in VS Code span hover providers, signature help, parameter hints, completions — it's unclear which tooltip types are in scope. | Scope gap | :warning: Needs input |
| No mention of how custom tooltips interact with existing language server tooltips, or what happens with conflicting customizations. | Edge case gap | :warning: Needs input |

**Risk level (implementer):** High — nothing is implementable as written.

---

## Issue 7 — Borderline

**Title:** [DevTools Feature Request]: Full support for RSC server elements (component tree, props, inspect)
**URL:** https://github.com/facebook/react/issues/27758
**Genre:** vague-feature
**Label:** `borderline`

### Why it's borderline
The issue identifies a real, significant gap (server elements are invisible in DevTools)
and links to the RFC acknowledging it as an open research area. But "full support" is
undefined and the architectural implications are enormous.

### Ground-truth gaps (implementer perspective)
| Gap | Category | Disposition |
|-----|----------|-------------|
| "Full support" is undefined — which DevTools panels, what data should display for server-only components, what "inspect" means for a component not in the browser DOM. | Requirements gap | :warning: Needs input |
| Server elements have no client-side runtime representation — the DevTools architecture may need fundamental changes (new data channel from server), not just bug fixes. Blast radius undefined. | Scope gap | :warning: Needs input |
| `_debugOwner` and `_debugSource` being null is described as the problem, but no contract is defined for what these fields SHOULD contain for server elements, or whether the fix is in React core, the DevTools extension, or both. | Contract gap | :warning: Needs input |

**Risk level (implementer):** High — scope and API design decisions must be made before any implementation.

---

## Issue 8 — Implementer-ambiguous

**Title:** Using Prisma at the edge seems to cause React Server Components to randomly return 500s during prefetching
**URL:** https://github.com/prisma/prisma/issues/20567
**Genre:** blocked-dependency
**Label:** `implementer-ambiguous`

### Why it's implementer-ambiguous
The bug report is detailed with clear repro steps, schema, and environment info.
But the fix spans three packages (Prisma, next-auth, Vercel edge runtime) and it's
unclear which team owns the fix or whether all three need changes.

### Ground-truth gaps (implementer perspective)
| Gap | Category | Disposition |
|-----|----------|-------------|
| The fix spans Prisma, next-auth, and Vercel's edge runtime. Labeled `status/blocked-by-dependency`. It's unclear which team owns the fix or whether all three need changes. | Dependency gap | :warning: Needs input |
| The bug only reproduces on Vercel deployment (not locally), pointing to an edge runtime constraint. Unclear if the fix is in Prisma's edge client, next-auth's adapter, Vercel's middleware runtime, or the interaction between them. | Scope gap | :warning: Needs input |
| The reporter uses Prisma Data Proxy (cloud.prisma.io) but it's unclear whether the issue is the proxy itself, the edge client connecting to it, or next-auth's session handling over the proxy. | Configuration gap | :warning: Needs input |
| The reporter frames this as a Prisma bug, but the error (`INTERNAL_EDGE_FUNCTION_UNHANDLED_ERROR`) originates from Vercel's edge runtime, not Prisma. The fix may not be in this repo at all. | Wrong mental model | :warning: Needs input |

**Risk level (implementer):** High — multi-package dependency chain with unclear ownership.

---

## Issue 9 — Good Feature Request

**Title:** feat: Client side error transformation
**URL:** https://github.com/trpc/trpc/issues/5581
**Genre:** api-contract
**Label:** `good-feature-request`

### Why it's a good feature request
Well-scoped problem with clear reproduction: proxies return non-tRPC JSON, the client
can't handle it. Reporter has tried custom links, transformer option, and fetch override,
documenting why each fails. The gap is in API design for the solution, not problem clarity.

### Ground-truth gaps (implementer perspective)
| Gap | Category | Disposition |
|-----|----------|-------------|
| The proposed solution ("ability to transform the json parsed") doesn't specify where in the request/response pipeline the transformation hook would live, what its signature would be, or how it composes with existing links. | Contract gap | :warning: Needs input |
| It's unclear whether the goal is (a) graceful error recovery when a proxy returns non-tRPC JSON, or (b) general response transformation capabilities. Different scope. | Requirements gap | :warning: Needs input |
| The ticket only covers the proxy-returns-non-tRPC-JSON case. Other contract mismatches (wrong status codes, HTML error pages, empty responses) aren't addressed but would likely hit the same code path. | Edge case gap | :warning: Needs input |

**Risk level (implementer):** Medium — well-scoped problem with clear reproduction, but the API design for the solution needs definition.

---

## Issue 10 — Bad Quality

**Title:** 200 status after update, but nothing is updated (from the context of a lambda)
**URL:** https://github.com/supabase/supabase/issues/28041
**Genre:** api-contract
**Label:** `bad`

### Why it's bad
The reporter assumes 200 = row was updated, but PostgREST returns 200 for "query executed
successfully" even if zero rows matched the filter. This is likely not a bug at all.
The reporter needs to understand PostgREST PATCH semantics.

### Ground-truth gaps (implementer perspective)
| Gap | Category | Disposition |
|-----|----------|-------------|
| The reporter assumes 200 = row was updated. PostgREST (underlying Supabase) returns 200 for "query executed successfully" even if zero rows matched the filter. This is by design, not a bug. The reporter may need `.single()` or to check the returned data array length. | Wrong mental model | :warning: Needs input |
| The reporter uses `service_role` key (bypasses RLS) but has RLS policies on Insert/Delete. It's unclear whether some policy is still interfering, or whether the `.eq('id', chapterId)` filter simply doesn't match. The actual API contract (PostgREST PATCH semantics) isn't understood. | Contract gap | :warning: Needs input |
| The reporter says "No error. Or Data is returned" — this is ambiguous. Does `data` contain an empty array (zero rows matched)? Or does it contain the row (matched but not updated)? The actual response shape is not shown. | Configuration gap | :warning: Needs input |
| No reproduction steps beyond "call `.update()` from Lambda." The table structure, the actual `updateData` value, and the `chapterId` are not shown. | Requirements gap | :warning: Needs input |

**Risk level (implementer):** High — likely not a bug at all; reporter needs to understand PostgREST PATCH semantics.

---

## Issue 11 — Tracking Issue (not implementable)

**Title:** Tracking Issue for Reproducible Build bugs and challenges
**URL:** https://github.com/rust-lang/rust/issues/129080
**Genre:** epic-spike
**Label:** `tracking-issue (not implementable)`

### Why it's a tracking issue
This is a coordination hub linking ~50 sub-issues about reproducible/deterministic builds.
It explicitly states "not meant for large scale discussion" and is labeled `S-tracking-forever`.
A developer should not attempt to "implement" this.

### Ground-truth gaps (implementer perspective)
| Gap | Category | Disposition |
|-----|----------|-------------|
| This is a tracking/coordination issue, not an implementation ticket. It explicitly says "not meant for large scale discussion" and is labeled `S-tracking-forever`. A developer should not attempt to "implement" this. | Wrong mental model (for the skill) | :information_source: Not applicable |
| No single deliverable — this links to ~50 sub-issues. There is no acceptance criterion because closing this issue is not the goal. | Requirements gap | :information_source: Not applicable |

**Risk level (implementer):** Low — the skill should recognize this as a tracking issue and say "this is not implementable as a single ticket."

---

## Issue 12 — Good Feature Request

**Title:** feat: overwrite input in middleware
**URL:** https://github.com/trpc/trpc/issues/6892
**Genre:** api-contract
**Label:** `good-feature-request`

### Why it's a good feature request
Clear problem statement with concrete code examples showing the runtime/type mismatch.
Reporter documents two workarounds and their downsides. The gap is in type-system
design work, not problem clarity.

### Ground-truth gaps (implementer perspective)
| Gap | Category | Disposition |
|-----|----------|-------------|
| The proposed API change (type-level input transformation through middleware) has type inference implications that aren't specified. How does the type system track input shape through chained `.use()` calls? Does it use generics, conditional types, or declaration merging? | Contract gap | :warning: Needs input |
| This changes tRPC's core type pipeline for procedures. Every middleware that passes input would need to participate in type narrowing. The blast radius for the type system is larger than the issue implies. | Scope gap | :warning: Needs input |
| What happens when multiple middlewares each modify input? Do transformations compose left-to-right? What if a middleware adds fields rather than removing them? | Edge case gap | :warning: Needs input |
| The reporter links to tRPC internals (`httpUtils.ts` line 210) — the fix may require changes to the link layer, the middleware layer, AND the type inference layer. These may need coordinated changes. | Dependency gap | :warning: Needs input |

**Risk level (implementer):** Medium — clear problem, good code examples, but the type-system design work is significant and unspecified.
