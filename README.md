# POPROX RSS Feed — Step 0

A minimal pipeline: fetch your newsletter via IMAP, parse it into
articles, and publish a standard RSS 2.0 feed via GitHub Pages. Point
DAKboard's News widget (or any RSS reader) at the resulting feed URL.

## Setup

1. **Create a repo** on GitHub, push this folder's contents.

2. **Enable GitHub Pages**
   Settings → Pages → Source: "Deploy from a branch" → Branch: `main`,
   folder: `/docs`.

3. **Add repo secrets** (Settings → Secrets and variables → Actions → Secrets):
   - `IMAP_HOST` — e.g. `imap.gmail.com`
   - `IMAP_USER` — your email address
   - `IMAP_PASS` — an app-specific password (not your real one)
   - `SENDER_FILTER` — substring of the newsletter's From address

4. **Add a repo variable** (same page, "Variables" tab):
   - `FEED_SITE_URL` — `https://<your-username>.github.io/<repo-name>/`

5. **Adjust `scripts/generate_feed.py`**
   `parse_articles()` is a generic starting point. Open your actual
   newsletter email, view its HTML source, and adjust the selectors to
   match its real structure. This step is required — every newsletter's
   HTML is different.

6. **Run it once manually**: Actions tab → "Update RSS Feed" → Run
   workflow. Confirm `docs/feed.xml` gets created with real articles.

7. **Point DAKboard (or any reader) at**:
   `https://<your-username>.github.io/<repo-name>/feed.xml`

## How it stays updated

A GitHub Actions workflow runs daily (adjust the cron time in
`.github/workflows/update-feed.yml` to match your newsletter's delivery
time), re-fetches and re-parses, and commits the refreshed `feed.xml`.
GitHub Pages auto-redeploys whenever that file changes.

## Notes

- Free on GitHub's public-repo tier.
- If your newsletter's HTML template changes, `parse_articles()` will
  need a matching update.
- This step 0 version outputs a flat article list — no custom sections,
  images, or layout. If you want the newspaper-style HTML dashboard back
  on top of this same data, that's a separate, later step.
