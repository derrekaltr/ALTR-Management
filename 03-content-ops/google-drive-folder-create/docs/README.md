# Altr Weekly Content-Outline System

Weekly pipeline that turns GPTease content ideas into organized, per-model folders and a
clean Altr-branded site with a shareable link.

## How it works

```
GPTease (weekly prompts)  →  content/<model>/<week>/<level>/idea-N.md  →  node site/build.js  →  dist/  →  Vercel (public link)
```

1. **Every week** (Monday), each model gets a new dated folder: `content/<model-slug>/<YYYY-MM-DD>/`.
2. Inside are three request folders — one per content level:
   - `level-1-implied/` — non-nude / implied only (hand bra, covered, tease framing)
   - `level-2-topless/` — topless allowed, nothing below the waist
   - `level-3-full-nude/` — full nude allowed
3. Each level folder gets **3 new idea files** (`idea-1.md`, `idea-2.md`, `idea-3.md`) generated
   with the master prompt in `prompts/weekly-outline-prompt.md`.
4. Each idea links its Google Drive upload folder — a "Submit Your Content"
   section on the idea page and PDF, and an "Upload Folders" map on the week page
   (same pattern as the original quote doc). Links come from each idea's
   `**Drive folder:**` line, falling back to the week root in `drive-folder.txt`.
5. `node site/build.js` renders everything into `dist/` as the branded site.
6. Pushing to `main` redeploys the Vercel site → the public link updates.

## Folder layout

```
content/
  valerie-bragg/
    profile.md            # internal only — NEVER published to the site
    2026-08-24/
      level-1-implied/
        idea-1.md idea-2.md idea-3.md
      level-2-topless/
      level-3-full-nude/
site/
  build.js                # static site generator (no dependencies)
  assets/style.css        # Altr branding
prompts/
  weekly-outline-prompt.md
  persona-setup-guide.md
```

`profile.md` files hold each creator's persona notes, assigned comfort level, and hard
boundaries. They are read by the team when prompting GPTease but are **excluded from the
built site** — the public pages only ever show stage names and the outlines themselves.

## Content levels

| Level | Folder | Rule |
|-------|--------|------|
| 1 | `level-1-implied` | Never nude. Hand bra, strategic covering, implied framing only. |
| 2 | `level-2-topless` | Topless allowed. Nothing below the waist. |
| 3 | `level-3-full-nude` | Full nude allowed. |

Every idea is generated *at* its level — an idea in a level folder must not exceed that
level, and each model's assigned comfort level (in her `profile.md`) is the floor the
chat team respects when picking which ideas to send her.

## Weekly run (manual, until the cron is enabled)

1. Run `scripts/new-week.sh` — creates this week's dated folders for every model.
2. Open GPTease (gptease.ai/chat) — must already be logged in — and select the model's persona.
3. Run the saved Prompt Library prompt (see `prompts/weekly-outline-prompt.md`) once per
   level: fill in the model name, level, and this week's theme direction.
4. Paste each of the 3 ideas into `content/<model>/<monday-date>/<level>/idea-N.md`
   using the file format below.
5. Build + check locally: `node site/build.js`, then preview with
   `python3 -m http.server 8471 --directory dist` → http://localhost:8471
6. Create the week's Google Drive upload folders (model → week → one folder per
   idea). Set sharing ONCE on the root folder ("Anyone with the link · Editor") so
   subfolders inherit it. Paste the week-root URL into
   `content/<model>/<week>/drive-folder.txt` and each idea folder's URL into that
   idea file's `**Drive folder:**` line. While a value is `TBD`, the submit
   links simply don't render.
7. Commit and push. Vercel redeploys automatically.

The automated version of this run (Claude driving the logged-in browser on a schedule)
is enabled after the first supervised pilot run — the Mac must be awake with Chrome
running at the scheduled time, since GPTease has no API.

## Idea file format

```markdown
# <Idea title>

**Theme:** <one line>
**Pairs with script:** <script/campaign name or TBD>
**Drive folder:** <Google Drive folder URL for this idea's uploads, or TBD>

| # | Type | Length | Description | Purpose |
|---|------|--------|-------------|---------|
| 1 | Photo | — | <framing/pose/wardrobe note> | Teaser |
| 2 | Voice note | 0:20 | <what she says, summarized> | Build |
| 3 | Video | 4:00 | <framing/action note> | Main |

**Totals:** X photos · Y videos (total Z min) · N voice notes

**Filming notes:** <outfit, location, lighting, camera setup>
```

The build script renders this markdown directly, so tables and bold labels come through
styled on the site.

## Deploy (one-time setup)

1. `npm i -g vercel` and `vercel login` (account owner does this — not Claude).
2. From the repo root: `vercel link`, then `vercel --prod`.
3. Set the project's build command to `node site/build.js` and output directory to `dist`.
4. Anyone with the resulting URL can view the site — keep real names, boundaries, and
   anything sensitive out of `content/**` idea files.
