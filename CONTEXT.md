# Context

## Glossary

### Series
A comic publication being tracked by the app. Covers both Japanese manga and Korean manhwa. The canonical domain term — never "manga" or "manhwa" in code or data models. A Series belongs to one or more Sources.

### Chapter
A single released instalment of a Series. The app detects when a new Chapter appears for a tracked Series and surfaces it to subscribed users.

### Source
An external website or API the app polls to detect new Chapters. Sources are either API-based (structured, reliable) or scrape-based (HTML parsing, brittle). Current sources: MangaDex (API), ManwhaClan (scrape), KunManga (scrape). Each Source has its own polling interval configured via environment variable.

### Subscription
A relationship between a User and a Series. A User subscribes to a Series by submitting a source URL (e.g. a MangaDex or ManwhaClan series page URL). The app derives the Source and series identity from the URL. A User receives in-app Notifications when a new Chapter is released for any subscribed Series.

### User
A registered account. Authentication is email + password. Users have a Subscription list and an in-app notification feed.

### Notification
An in-app alert surfaced to a User when a new Chapter is detected for a Series they are subscribed to. Notifications are not sent via email or external messaging — email is for auth only.
