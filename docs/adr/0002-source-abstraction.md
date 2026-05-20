# ADR-0002: Abstract Source interface

## Status
Accepted

## Context
The app polls multiple external sources for new Chapters: one API (MangaDex) and two scrape-based sites (ManwhaClan, KunManga). Each source has different authentication, HTML structure, rate limits, and reliability characteristics.

## Decision
Each Source is implemented as a module conforming to a shared interface (e.g. `get_latest_chapter(series_url: str) -> Chapter | None`). The polling worker calls this interface without knowing which Source type it is talking to.

## Reasons
- Adding a new Source requires only a new module — no changes to the polling worker or data model
- Per-Source error handling and metrics are isolated — a scraper failure doesn't affect the MangaDex poller
- Makes it straightforward to mock individual Sources in tests

## Alternatives considered
- **Hardcoded per-source logic in the poller** — simpler initially, but tightly couples source-specific brittle code to the scheduling logic; adding a fourth source means modifying the poller
