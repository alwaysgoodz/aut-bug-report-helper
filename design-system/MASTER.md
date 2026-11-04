# Structured Bug Report Helper: UI decisions

The ui-ux-pro-max searches for a developer tracker and SaaS dashboard both returned marketing/documentation page patterns. Those patterns were rejected; no unrelated search result was persisted as the app specification. This spec applies the skill's general priorities and verified form-error guidance, with the existing A1 report's teal accent.

Use a quiet, light workspace: dark teal navigation, warm off-white canvas, white panels, teal primary buttons and restrained severity/status badges with visible text. No marketing hero, fictitious statistics, remote fonts or decorative animation. System sans-serif keeps the local application self-contained. Body text 16px, control labels at least 14px, 44px touch targets, consistent 4/8/16/24/32 spacing, visible keyboard focus, skip link, responsive layout, and reduced-motion support.

Reports, New report and report details have real URLs. Empty state offers a creation action. Every form field has a visible label; validation retains entered data, connects each inline error with aria-describedby, and focuses a linked error summary after submission. Never communicate severity or status using colour alone. A completeness percentage must explain that it measures information presence, not correctness.

## Refinement after the browser audit

Keep the same teal palette and local system-font approach. Use a continuous four-part summary with meaningful status links, 12px minimum table headers/badges, 16px inputs, tabular numbers and a 25-row list. At widths below 900px, preserve table semantics while presenting report rows as cards. At tablet widths, use the existing navigation as a top bar rather than squeezing the workspace beside a sidebar.

Group form fields into issue/reproduction/context and retain their original keyboard order. Desktop guidance stays beside the form with bounded scrolling; small-screen guidance is compact and uses native disclosure. Missing-field links focus actual controls, status success is explicit, and the seven-field rules/meaning remain unchanged. No decorative animation, remote font or fabricated data is added.
