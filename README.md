# St. Clair Square — documents hub

One permanent link for the current St. Clair Square documents, shared with the
team and (when cleared) the public. A single static page on GitHub Pages;
documents render natively in the browser. Nothing to maintain, nothing to pay for.

Live at: **https://ix-b-io.github.io/scs-docs-hub/**

**The rule that makes links permanent:** every PDF keeps its filename forever.
To update a document, replace the file at the same path. Every link ever sent
keeps working and always shows the latest version. The version history lives
in git.

## Contents

```
index.html      the page (single file, no dependencies)
docs.json       the document list — edit this to add or change entries
sw.js           offline support: caches the page and all listed PDFs on first visit
robots.txt      keeps search engines away (prototype phase — remove at go-live)
assets/         header artwork and the home-screen icon
docs/           the PDFs themselves
```

There is deliberately **no web app manifest**. As of iOS 26, app-vs-bookmark
behavior is decided by the user's "Open as Web App" toggle at install time —
site code has no say — so the stack carries nothing app-related.

## Team install instructions (copy-paste)

> St. Clair Square documents — one link, always current:
> https://ix-b-io.github.io/scs-docs-hub/
> To put it on your phone: open the link in **Safari** → Share →
> **Add to Home Screen** → **switch OFF "Open as Web App"** → Add.
> Tap any document title to open it. Links you copy or email always show the
> latest version.

The toggle step matters: left on (the iOS 26 default), the icon opens an
app-style window without browser controls. Switched off, it is a true Safari
bookmark. The custom icon appears either way.

## Publishing or updating a document

1. Name new PDFs once, stably and generically: `scs-topic-name.pdf`.
   The version lives in git, not the filename.
2. Optimize before upload — screen-resolution exports only. Print-resolution
   files (100MB+) are slow everywhere and GitHub rejects files over 100MB.
3. Drop the file into `docs/` (replacing the old one if it's an update), and
   for new documents add an entry to `docs.json`:

```json
{
  "title": "Document title",
  "description": "One line on what this is.",
  "uploaded": "2026-07-09",
  "file": "docs/scs-topic-name.pdf"
}
```

4. For updates, replace the file and bump the `uploaded` date. Done.

**Timing rule:** caches can serve the previous file for up to ~10 minutes after
a push. Never update a document within 15 minutes of it being presented.

## Offline behavior

Opening the page once quietly caches it and every listed PDF on the device.
Online, every open fetches the live version (no one can be served a stale file
while connected); offline, the last-seen copy serves instantly. Safari purges
these caches for anyone who hasn't visited in ~7 days — their next open needs
a connection. Team habit before travel or important meetings: open the page
once on wifi.

## Go-live checklist (before public circulation)

- Replace/confirm all documents are cleared versions
- Remove `robots.txt` and the `noindex` meta in `index.html`
- Consider the custom domain (one CNAME + Pages settings field); it also makes
  links survive any future repo transfer
- Keep only public-approved material in this repo — it is world-readable,
  including its git history

## Security

Read access is public by design. Write access is the whole game: it is
controlled by the GitHub accounts with push rights to this repo (keep 2FA on).
There is no server, no database, and no code that executes anywhere except
this static page in the visitor's browser.
