# St. Clair Square — approved documents hub

A single-page app that gives the team (and the public) one permanent home for the
current approved St. Clair Square documents. Hosted free on GitHub Pages. Installs
to iPhone and iPad home screens as a full-screen app; works as a normal page on
laptops.

**The core rule that makes links permanent:** every PDF keeps its filename forever.
When a document is revised and re-approved, you replace the file at the same path.
Every link ever emailed, texted, or bookmarked keeps working and always shows the
latest approved version.

## Contents

```
index.html      the app (single file, no dependencies)
docs.json       the document list — edit this to add/change entries
manifest.json   PWA manifest (home-screen install)
assets/         app icons
docs/           the PDFs themselves (currently sample placeholders)
```

## One-time setup (10 minutes)

1. Create a repo under the Yar-Project org, e.g. `scs-docs-hub`. **It must be
   public** for free GitHub Pages — fine here, since these files are approved for
   public discussion. (Private repos need GitHub Pro/Team for Pages.)
2. Push this folder's contents to the repo root on `main`.
3. Repo → Settings → Pages → Source: **Deploy from a branch** → `main` / root → Save.
4. After a minute the app is live at
   `https://yar-project.github.io/scs-docs-hub/`
5. Optional, recommended for public-facing polish: point a subdomain like
   `docs.stclairsquare.com` at it (Settings → Pages → Custom domain, plus one
   CNAME record at the registrar). All links below then use that domain.

## Publishing or updating a document

1. Name the PDF once, stably and generically: `scs-project-overview.pdf`,
   not `SCS_Overview_v3_FINAL.pdf`. The version lives in git, not the filename.
2. Drop it into `docs/` (replacing the old file if it's an update) and commit.
3. If it's a **new** document, add an entry to `docs.json`:

```json
{
  "title": "Project overview",
  "description": "One line on what this is.",
  "approved": "2026-07-02",
  "file": "docs/scs-project-overview.pdf"
}
```

4. If it's an **update**, just bump the `approved` date and the top-level
   `updated` date. Done — the link never changed.

Entries can also point at any external URL (`"file": "https://…"`), e.g. a
DocSend/Papermark link if a specific document later needs tracking.

Git gives you the audit trail for free: every superseded version of every PDF is
recoverable from history, with a timestamp of exactly when it was replaced.

## Getting it onto the team's phones (30 seconds each)

Send this to the team:

> 1. Open `https://yar-project.github.io/scs-docs-hub/` in **Safari**
> 2. Tap the Share button (square with the up arrow)
> 3. Tap **Add to Home Screen**, then **Add**

A St. Clair Square icon appears on the home screen and opens full-screen, no
browser bars. On laptops, the same URL is just a bookmark. A QR code of the URL
on one slide at the next team meeting gets everyone installed at once.

## Sharing documents by email

Each document has four actions in the app:

- **Open document** — views the PDF (opens with a Done button inside the
  home-screen app on iOS)
- **Share** — the native iOS/iPadOS share sheet: Mail, Messages, AirDrop, Slack…
- **Copy link** — copies the permanent URL
- **Email** — opens a pre-drafted email with the subject, the link, the approval
  date, and a note that the link always shows the latest approved version

No sign-in is ever required to view anything — the PDFs are served as plain
public files.

## Notes

- iOS home-screen apps cache aggressively; `docs.json` is fetched with a
  cache-buster on every open, so the list is always current.
- Keep only public-approved material in this repo. Anything internal stays in
  Drive/private repos — this hub is world-readable by design.
