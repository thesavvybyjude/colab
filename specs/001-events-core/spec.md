# Feature Specification: CoLab Events Core (slim v1)

**Feature Branch**: `001-events-core`

**Created**: 2026-11-16

**Status**: Draft

**Input**: User description: "A system for CoLab Jos where events are submitted and approved, checked against the space calendar, shown on a public events page, open for public registration and check-in, and turned into a ready-to-post graphic and caption from a template. Social auto-posting, branding and courses come later."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Staff publish an event and the public sees it (Priority: P1)

A CoLab admin signs in, enters an event (title, description, space, date, start and end time, host name) and publishes it. Anyone visiting the public events page sees it listed with upcoming events, soonest first, and can open its details.

**Why this priority**: The original goal is telling the public what is happening at the hub. This slice does that alone, with nothing else built.

**Independent Test**: An admin creates and publishes one event; a visitor who is not signed in opens the events page on a phone and finds the event with the right date, time and place.

**Acceptance Scenarios**:

1. **Given** a signed-in admin, **When** they publish an event with all required details, **Then** it appears on the public events page without any separate website update.
2. **Given** a published event, **When** an admin changes its time, **Then** the public page shows the new time.
3. **Given** an event already booked in a space, **When** an admin tries to publish another event in the same space at an overlapping time, **Then** the system refuses and names the clashing event.
4. **Given** an event whose end time has passed, **When** a visitor opens the events page, **Then** that event is no longer in the upcoming list.
5. **Given** a visitor who is not signed in, **When** they try to open any admin screen, **Then** they are sent to sign-in and see no admin data.

---

### User Story 2 - A host pitches an event and an admin decides (Priority: P2)

A host (for example Lily) submits an event proposal. The system tells her straight away if the space is already taken at that time. If it is free, the proposal waits for an admin, who approves it, rejects it with a reason, or sends it back for changes. Only an approved event becomes public.

**Why this priority**: It lets people other than staff bring events to the hub while keeping a human decision before anything goes out under CoLab's name.

**Independent Test**: A host submits a proposal; it is absent from the public page; an admin approves it; it then appears on the public page.

**Acceptance Scenarios**:

1. **Given** a host, **When** they submit a proposal for a free slot, **Then** it is saved as "Submitted" and is not visible to the public.
2. **Given** a proposal for a slot that overlaps an approved event in the same space, **When** the host submits it, **Then** the system reports the clash and asks for another time.
3. **Given** a submitted proposal, **When** an admin approves it, **Then** its status becomes "Approved", the slot is held, and it shows on the public page.
4. **Given** a submitted proposal, **When** an admin rejects it or asks for changes, **Then** a reason is required and the host can see it.
5. **Given** two submitted proposals for the same slot, **When** an admin approves one, **Then** the other can no longer be approved for that slot.
6. **Given** a host, **When** they view proposals, **Then** they see only their own.

---

### User Story 3 - A visitor registers for an event (Priority: P3)

A visitor opens an event that takes registrations, enters their name and phone number (email optional), and gets a confirmation screen with a reference. If the event is full, the page says so and takes no more registrations.

**Why this priority**: Registration tells CoLab who is coming and gives the hub a way to reach people again, which is how attendance grows.

**Independent Test**: With an event of capacity 2, three different visitors try to register; two succeed with distinct references and the third sees "Full".

**Acceptance Scenarios**:

1. **Given** an event with free places, **When** a visitor submits a valid name and phone number, **Then** a registration is saved and a confirmation with a unique reference is shown.
2. **Given** an event at capacity, **When** a visitor opens it, **Then** it shows "Full" and offers no registration form.
3. **Given** one place left, **When** two visitors submit at the same moment, **Then** exactly one registration succeeds.
4. **Given** a phone number already registered for an event, **When** it is submitted again for the same event, **Then** the visitor is shown their existing registration and no duplicate is created.
5. **Given** an event set to open attendance, **When** a visitor opens it, **Then** no registration form is shown.

---

### User Story 4 - Staff check people in and see attendance (Priority: P4)

On the day, an admin opens the event's attendee list on a phone, searches by name or phone number, and marks people as arrived. Walk-ins can be added on the spot. Afterwards the event shows how many registered and how many came.

**Why this priority**: Registered-versus-attended is the evidence that the hub's events are working, but events can run without it.

**Independent Test**: With three registrations, an admin checks in two and adds one walk-in; the event shows 3 registered, 1 walk-in, 3 attended.

**Acceptance Scenarios**:

1. **Given** a registered attendee, **When** an admin marks them arrived, **Then** the time is recorded and the attended count goes up by one.
2. **Given** an attendee already marked arrived, **When** an admin marks them again, **Then** the count does not change.
3. **Given** a person with no registration, **When** an admin adds them as a walk-in, **Then** they are recorded as attended and counted separately from registrations.
4. **Given** an event, **When** an admin exports the attendee list, **Then** they receive names, phone numbers and attendance status.

---

### User Story 5 - A ready-to-post graphic and caption (Priority: P5)

For an approved event, an admin picks one of the available templates. The system fills it with the event's details and produces an image and a caption to download or copy. The admin posts them by hand and records where they were posted.

**Why this priority**: It standardises publicity and saves design time, but the hub can announce events without it. Automatic posting is deliberately left out.

**Independent Test**: For one approved event, generate a graphic from each template; each image shows the event's correct title, date, time and space; mark one as posted to a channel and see that record on the event.

**Acceptance Scenarios**:

1. **Given** an approved event and a chosen template, **When** an admin generates publicity, **Then** an image and caption are produced using the event's stored details.
2. **Given** generated publicity, **When** the event's time changes, **Then** the old publicity is flagged as out of date and can be regenerated.
3. **Given** generated publicity, **When** an admin records it as posted to a channel, **Then** the event shows that channel and date.
4. **Given** an event that needs its own design, **When** an admin uploads a custom image, **Then** it is used in place of a template.

---

### Edge Cases

- An approved event is cancelled: it leaves the upcoming list, its slot is freed, and the admin can export the registrants' contacts to inform them.
- An approved event is moved to a slot that clashes with another: the change is refused.
- Capacity is lowered below the number already registered: the change is refused or the admin is warned; no registration is silently removed.
- End time is before start time, or the date is in the past: the form is rejected.
- A very long title or description: generated graphics still fit the text without cutting off the date, time or place.
- Poor connection during check-in: a repeated tap does not double-count.
- A visitor enters a phone number in local or international format: both are treated as the same number.

## Requirements *(mandatory)*

### Functional Requirements

**Accounts and access**

- **FR-001**: System MUST require sign-in for all non-public screens.
- **FR-002**: System MUST support two signed-in roles, admin and host, plus the unauthenticated public.
- **FR-003**: Admins MUST be able to create and deactivate accounts and set their role.
- **FR-004**: Hosts MUST only be able to view and edit their own proposals.
- **FR-005**: Event hosts submit proposals via [NEEDS CLARIFICATION: do hosts get their own logins, or do staff enter events on their behalf? This spec assumes host logins created by an admin; if staff enter everything, the host role and User Story 2's host-side screens are dropped.]

**Events and scheduling**

- **FR-006**: An event MUST have a title, description, space, date, start time, end time and host name.
- **FR-007**: An event MUST have one status from: Draft, Submitted, Changes requested, Approved, Rejected, Cancelled. "Completed" is derived from the end time.
- **FR-008**: System MUST prevent two approved events from overlapping in the same space.
- **FR-009**: System MUST warn at submission when a requested slot overlaps an approved event.
- **FR-010**: Only admins MUST be able to approve, reject, request changes to, or cancel an event; rejection and change requests MUST carry a reason.
- **FR-011**: System MUST record who approved an event and when.
- **FR-012**: System MUST support [NEEDS CLARIFICATION: how many bookable spaces does CoLab have? This spec assumes a short list of named spaces that admins can add to, starting with one.]

**Public events page**

- **FR-013**: System MUST show approved, upcoming events to anyone without sign-in, soonest first.
- **FR-014**: Each event MUST have its own shareable public page with its details.
- **FR-015**: The public pages MUST read from the same event records the admins manage, with no separate update step.
- **FR-016**: Public pages MUST be usable on a phone on a slow connection.

**Registration and attendance**

- **FR-017**: Each event MUST be set to either "registration" or "open attendance", with an optional capacity.
- **FR-018**: Visitors MUST be able to register with name and phone number, with email optional, and without creating an account.
- **FR-019**: System MUST never accept more registrations than capacity, including under simultaneous submissions.
- **FR-020**: System MUST prevent duplicate registration of the same phone number for the same event.
- **FR-021**: System MUST give each registration a unique reference shown on the confirmation screen.
- **FR-022**: Admins MUST be able to search an event's attendees, mark arrival, add walk-ins and export the list.
- **FR-023**: System MUST show registered, walk-in and attended counts per event.
- **FR-024**: Registrants' contact details MUST be visible only to admins and to the host of that event.

**Publicity**

- **FR-025**: System MUST keep a small set of templates (three to start) that admins can add to or replace without changing event records.
- **FR-026**: System MUST generate an image and caption for an approved event from a chosen template and the event's stored details.
- **FR-027**: Admins MUST be able to download the image, copy the caption, and upload a custom image instead.
- **FR-028**: System MUST let admins record that publicity was posted, with channel and date, and MUST flag publicity as out of date when the event's key details change.

**Explicitly out of scope for v1**

- Automatic posting to WhatsApp, Instagram, X or LinkedIn.
- CoLab branding and visual identity work.
- Courses, payments, waitlists, custom registration questions, QR check-in, automated reminders.
- Recurring events, equipment booking, setup and cleanup buffers.
- Fine-grained permissions, multi-level approval, full audit history, analytics.

### Key Entities

- **User**: A person with an account. Has a name, contact, role (admin or host) and active status.
- **Space**: A bookable place at the hub. Has a name and an optional capacity.
- **Event**: Something happening in a Space at a set time. Holds its details, status, registration mode, capacity, the User who submitted it and the admin who decided it.
- **Registration**: One person's place at an Event. Holds name, phone, optional email, reference, whether it was a walk-in, and arrival time.
- **Template**: A reusable publicity layout with named slots for event details.
- **Media**: A stored image, either generated or uploaded.
- **Post**: A piece of publicity for an Event: the Template used, its Media, the caption, and where and when it was posted by hand.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An admin can go from a blank form to an event visible on the public page in under 3 minutes.
- **SC-002**: A visitor can register for an event on a phone in under 1 minute.
- **SC-003**: No two approved events ever overlap in the same space.
- **SC-004**: No event ever holds more registrations than its capacity.
- **SC-005**: An admin can check in an attendee in under 10 seconds per person.
- **SC-006**: A graphic and caption for an approved event are ready to post in under 2 minutes, with no design tool opened.
- **SC-007**: After the first month of use, every event held at the hub that month is in the system, and each has registered and attended numbers.

## Assumptions

- The system is for CoLab's new Jos branch. CoLab has run its Kaduna hub since 2016, so it may already have ways of handling events; what it uses today has not been checked.
- CoLab's leadership has not yet confirmed that it wants this system; the builder's role at CoLab and the hub's monthly event volume are unknown. If volume is low, User Stories 1 and 3 may be enough on their own.
- Any admin can approve any event; there is one level of approval.
- Staff use phones as much as laptops, so every screen must work on a phone.
- Phone number is the main contact because the hub's community lives on WhatsApp; reminders are sent by hand through the WhatsApp community.
- The interface starts neutral; CoLab's visual identity is applied later through templates and styling without changing the data.
- One hub, one time zone (Africa/Lagos), English only.
- Courses, when they come, will reuse the Event record before anything larger is built.
