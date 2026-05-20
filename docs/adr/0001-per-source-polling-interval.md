# ADR-0001: Per-source polling interval

## Status
Accepted

## Context
The app needs a background worker that periodically checks each Source for new Chapters. The interval could be global (same for all sources) or per-source.

## Decision
Each Source has its own polling interval, configured via environment variable. Current defaults:
- MangaDex (API): every 30 minutes
- ManwhaClan (scrape): every 2 hours
- KunManga (scrape): every 2 hours

## Reasons
- Scrape sites risk IP bans or rate-limiting at high frequency; API sources can be polled more aggressively
- Per-source observability: poll success rate and latency can be tracked independently per Source, making the Discord DevOps alerts meaningful
- Intervals as environment variables follows Twelve-Factor App config practice — no code change needed to tune them

## Alternatives considered
- **Fixed global interval** — simpler, but treats a generous API the same as a fragile scraper
- **Adaptive interval** (based on release cadence) — interesting but adds complexity that distracts from the core DevOps learning goals
