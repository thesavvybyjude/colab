# Build Plan: CoLab Events Core (slim v1)

**Spec**: `specs/001-events-core/spec.md`

**Created**: 2026-11-17

**Status**: Draft, built on two assumptions that are still unconfirmed (see "Open items")

## Summary

One web application with one database. It serves two faces from the same records: a public events site (no sign-in) and a staff area (sign-in). It is built in five slices, in the order of the spec's user stories, and each slice is deployed and usable before the next starts.

## Technical choices

| Area | Choice | Why |
|---|---|---|
| Language and framework | Python 3.12, Django 5 | Accounts, roles, forms, an admin screen and database transactions come built in, which covers most of slices 1, 2 and 4 without extra code |
| Database | PostgreSQL (SQLite allowed for quick local runs) | Needed for the "never overbook" and "never double-book" guarantees |
| Pages | Django templates, server-rendered, plain CSS, a little HTMX for check-in | Fast on a phone on a slow connection; no separate front-end app to build and deploy |
| Graphics | An HTML/CSS template per design, rendered to PNG by headless Chromium (Playwright) | Templates are just HTML, so new designs need no code changes |
| Files | Local media folder in v1, behind Django's storage setting | Can move to object storage later by changing one setting |
| Tests | pytest with pytest-django | Each acceptance scenario in the spec becomes at least one test |
| Packaging | Docker and Docker Compose (app + database) | Same setup on the laptop and the server |
| CI | GitHub Actions: lint, tests, image build on every push | Evidence of working software on every commit |
| Hosting | One small Linux server or a managed app host, decided in slice 1 | Not decided yet; needs a cost check |

Deliberately not used: a separate JavaScript front end, microservices, task queues, social media APIs.

## Project structure

```text
colab/
├── config/                 # settings, urls
├── accounts/               # User with role (admin, host), sign-in
├── events/                 # Space, Event, statuses, clash check, public pages
├── registrations/          # Registration, capacity, check-in, export
├── publicity/              # Template, Media, Post, image rendering
├── templates/              # page templates
├── static/                 # CSS
├── tests/                  # one folder per app
├── Dockerfile
├── compose.yaml
├── .github/workflows/ci.yml
└── specs/001-events-core/  # spec.md, plan.md
```

## Data model

- **User**: name, phone, email, role (`admin` or `host`), active.
- **Space**: name, capacity (optional).
- **Event**: title, description, space, start, end, host name, status, registration mode (`registration` or `open`), capacity (optional), submitted by (User), decided by (User), decided at, decision reason.
- **Registration**: event, name, phone (normalised), email (optional), reference, walk-in flag, checked-in at. Unique on (event, phone).
- **Template**: name, HTML file, preview image, active.
- **Media**: file, kind (`generated` or `uploaded`).
- **Post**: event, template (optional), media, caption, channel (optional), posted at (optional), out-of-date flag.

Rules enforced in the database, not only in forms:

- No two `Approved` events overlap in the same space (exclusion constraint on space and time range; checked in a transaction on SQLite).
- Registrations never exceed capacity (the event row is locked while a registration is created).
- One registration per phone number per event (unique constraint).

## Build order

Each slice ends with: tests passing in CI, deployed, and a short note in the README on what works.

### Slice 0: Foundation

- Create the GitHub repository and move this spec into it.
- Django project, Docker Compose, CI running an empty test suite.
- Deploy a "hello" page to the chosen host, so deployment is solved on day one.

**Done when**: a push to `main` runs CI and the live URL shows the page.

### Slice 1: Staff publish, public sees (User Story 1)

- User model with role; sign-in and sign-out.
- Space and Event models; admin create/edit screens.
- Clash check on publish.
- Public events list and event detail page.

**Done when**: all five acceptance scenarios of User Story 1 pass as tests, and a real event is visible on the live URL from a phone.

### Slice 2: Pitch and approve (User Story 2)

- Host role screens: submit a proposal, see own proposals and decisions.
- Statuses and the admin review screen: approve, reject, request changes, with reason.
- Clash warning at submission; approval blocked on clash.

**Done when**: the six scenarios of User Story 2 pass.

### Slice 3: Registration (User Story 3)

- Registration mode and capacity on Event.
- Public registration form, confirmation screen with reference.
- Capacity lock, duplicate check, phone number normalisation.

**Done when**: the five scenarios pass, including a test that fires simultaneous registrations at the last place.

### Slice 4: Check-in and attendance (User Story 4)

- Attendee list with search, one-tap arrival, walk-in entry.
- Counts on the event; CSV export.

**Done when**: the four scenarios pass and check-in works on a phone.

### Slice 5: Publicity (User Story 5)

- Template, Media and Post models; three starter templates in neutral styling.
- Render to PNG; caption text; download and copy.
- Custom image upload; "posted to" record; out-of-date flag on event change.

**Done when**: the four scenarios pass and each template renders a long title without cutting off date, time or place.

## Suggested pace

Sized in focused build sessions of about three to four hours. These are estimates and have not been tested against real progress.

| Slice | Sessions |
|---|---|
| 0 Foundation | 1 |
| 1 Staff publish, public sees | 2 |
| 2 Pitch and approve | 1 to 2 |
| 3 Registration | 1 to 2 |
| 4 Check-in | 1 |
| 5 Publicity | 2 |

Total: 8 to 10 sessions. Slices 0 and 1 together (3 sessions) give something real to show CoLab.

## Checkpoint after Slice 1

Show the live site to whoever runs CoLab before building further. Their answers decide whether slices 2 to 5 are built as written, reordered, or dropped.

## Open items

1. **Host access** (spec FR-005): assumed hosts get logins. If staff enter all events, Slice 2 shrinks to the review statuses only.
2. **Spaces** (spec FR-012): assumed a short list starting with one. The model already supports several, so this changes data, not code.
3. **CoLab's buy-in, your role there, and monthly event volume**: unknown. These decide whether to continue past Slice 1, not how to build it.
4. **Hosting**: not chosen; needs a cost comparison.
5. **Spec Kit constitution**: still the blank template.
