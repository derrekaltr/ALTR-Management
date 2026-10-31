# Weekly refresh — ALTR Case Board

The dashboard is generated, not hand-built. To refresh it after updating the data:

1. **Update the data** in `scratch/build_xlsx.py` — five plain Python lists:
   `pb` (priority board rows), `recv` (owed to ALTR), `pay` (refunds/payables),
   `dep` (deposit log), `tl` (timeline). Each row is a tuple; dates are `date(y,m,d)`.
2. **Regenerate everything:**
   ```bash
   cd scratch && python3 gen_dashboard.py
   ```
   That rewrites both `ALTR_Case_Board_Dashboard.html` and `ALTR_Case_Board.xlsx`.
3. Update `ASOF` in `build_xlsx.py` + the "Week of" / "As of" strings in
   `gen_dashboard.py` (search for `Sep 18`).

**Full re-audit** (re-reading the last N weeks of iMessage/WhatsApp and rebuilding
the case list) is an agent task, not a script — ask Claude: *"re-run the ALTR case
audit for the last week and refresh the dashboard."* The extraction pipeline
(`extract.py` → `rank_chats.py` → `micro.py`) is already here and takes ~5 min of
machine time; the reading/judgment part is what the agent redoes.

**Brand:** every color/font/shape lives in the `ALTR BRAND TOKENS` block at the
top of the HTML template in `gen_dashboard.py` — swap tokens there to re-skin.
Chart palette (`--c1..c4`) is validated for the dark surface; if you change it,
re-run the dataviz validator before shipping.
