# Weekly Content Batch Runbook

Run this once a week (per goal.md's cadence decision). Output: N new
articles published to the site and their pins queued in Pinterest's
scheduler. N = 5 for the very first batch (Tasks 15-19 of the
implementation plan); afterwards, pick N to match available review time.

## 1. Pick topics

```bash
cd 07_blogtoolstack/pipeline
python3 keyword_backlog.py list --status backlog
```

Take the top N by priority score. Mark each `in_progress`:

```bash
python3 keyword_backlog.py set-status --keyword "<keyword>" --status in_progress
```

## 2. Draft (Claude session, not a script)

For each topic, start a Claude Code session and give it:
- The target keyword and its child keywords (from the backlog entry)
- The format (comparison/review/how-to/listicle)
- `pipeline/article-template.md` as the structural contract
- Instruction: cover the comparison points listed in the template
  honestly (per the playbook: don't just push Kit -- a genuinely
  evenhanded comparison is what builds the trust the strategy depends on)
- The Kit affiliate link from `content-backlog/kit-affiliate-link.txt`
  to substitute into `<KitSignupCTA href="...">`
- Do NOT mention the actual commission percentage anywhere in the
  article text -- only the generic `<AffiliateDisclosure />` belongs
  on the page (see goal.md's Global Constraints)

## 3. Humanize

Run the `humanizer` Claude Code skill on the draft to strip AI-writing
tells (inflated language, rule-of-three, filler phrases, em-dash
overuse, etc.) before the review pass.

## 4. AI review (separate pass/session from the writer)

In a fresh Claude session (not the one that drafted it), review for:
- Factual accuracy of any claims about Kit or the compared products
  (cross-check against official pricing/feature pages, not memory)
- Tone/readability fit for the bloggers/niche-site-owner audience
- No AI-writing tells remain after the Humanizer pass

## 5. Validate

```bash
python3 pipeline/validate_article.py site/src/content/articles/<slug>.md
```

Fix any reported errors and re-run until `OK`.

## 6. Human spot-check (first ~10-20 articles only)

Run a random subset of this batch through an external tool (e.g.
Grammarly) as a cheap safety net beyond the AI review, given Joel is
not a native English writer. Taper this off once the pipeline's
failure rate is known to be low.

## 7. Publish

```bash
cd site && npm run build && npx wrangler pages deploy dist --project-name=blogtoolstack
```

Mark each backlog entry `published`:

```bash
python3 pipeline/keyword_backlog.py set-status --keyword "<keyword>" --status published
```

## 8. Pins

Follow `pipeline/pin-and-schedule-runbook.md` (Task 21) for each newly
published article.
