# Current-system refinement: acceptance and measurement plan

Optimise the existing system against its course requirements, test it and improve visual quality. Preserve existing A1/A2 review snapshots. Inherit `design-system/MASTER.md`; keep the Python/SQLite stack and local assets.

## Audit and acceptance

- Actual browser: 9px table headers and 10px badges. Increase these to at least 12px and input text to 16px.
- Replace horizontal mobile list browsing with semantic report rows presented as cards below 900px. Check list, form and detail at 390px, 768px and 1440px without document overflow.
- Bound browser pages to 25 reports, with stable order, accurate filtered totals, filter-preserving links and access to every record. Keep the unpaged Python interface for compatibility and compute each row's completeness once.
- Share explicit whitespace handling between Python and JS; test BOM/NEL/control-separator presence and persisted validation.
- Group fields into issue/reproduction/context without changing tab order; missing-field links focus their targets. Retain native form submission, collapsible mobile guidance and explicit status-update confirmation.

## Verification

Run existing and focused Python/HTTP/browser checks, inspect actual desktop/tablet/mobile screenshots and selected text contrast pairs. Selected checks are not a complete accessibility certification.

## Predeclared refined performance scenario

500 synthetic reports, one client, five warmups and 50 full-body requests rotating over all 20 pages. Each returns at most 25 rows. Preserve page/bytes/duration, audit all 500 distinct IDs across 20 pages, and record environment/source hashes. Keep p95 <250 ms. The prior 77.8756 ms result returned 500 reports in one response; this response-workload change prevents a direct speedup claim.

## Delivery

New review branch/PR and technical candidate, without automatic approval or merge. Archive raw evidence and changed conditions. Original `a2-review-v0.1` and its report remain historical evidence.
