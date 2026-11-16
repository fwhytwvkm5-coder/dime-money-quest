# Dime's story (Season 1: "Dime's Year")

Started 2026-11-15 (user's decision 2026-11-14). Every boss fight is also a step in Dime's own money story.
Viewers see it in the quest panel during the payoff (`quest_bar` in studio/fx.py): story day, what Dime now
sets aside per month, and how many months until his goal. The tip itself always stays useful for the viewer
on its own (check 1: stands alone).

## Dime's fixed facts (fictional, all EXAMPLE NUMBERS)
- 22, first full-time job, lives in a shared flat.
- Net pay: €1,900 a month (from 2026-11-15: €2,300 after the raise in ep008).
- Room: €650 a month.
- Quest: a €3,000 safety net (emergency fund).
- Saving plan at the start: €50 a month.

## Rules for the ledger
- Story day = days since 2026-11-15, plus 1 (both boss fights of a posting date share the day).
- Every boss fight adds the monthly amount its tip wins to Dime's plan (`PLAN_AFTER = PLAN_BEFORE + monthly win`),
  only if it fits Dime's life; otherwise the plan stays the same and the panel still shows.
- Months to goal = ceil(3000 / plan). The plan may never exceed 30 % of Dime's net pay.
- Quick formats and carousels do not change the ledger.
- Once the goal would be reached (when the €3,000 is "saved" in story time), the season ends; the user decides what comes next.

## Ledger
| Date | Day | Episode | What Dime changed | Plan before | Plan after | Months to €3,000 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-11-15 | 1 | ep007 Fee Ghost | switched to a free account: +€15/month | 50 | 65 | 47 |
| 2026-11-15 | 1 | ep008 Lifestyle Creep | raise +€400, auto-saves €200 of it | 65 | 265 | 12 |
| 2026-11-16 | 2 | ep009 Drip Slimes | scanned 30 days, plugged 3 of 4 small leaks: +€30/month | 265 | 295 | 11 |
| 2026-11-16 | 2 | ep010 Chaos Blobs | 3 jars, SAVE jar filled first on payday: +€50/month | 295 | 345 | 9 |
| 2026-11-17 | 3 | ep011 Want Wisps | mapped his €2,300 pay 50/30/20: SAVE share 20% = €460 (+€115/month) | 345 | 460 | 7 |
| 2026-11-17 | 3 | ep012 Crumb Rats | pays himself first: €100 auto-transfer on payday before bills and fun: +€100/month | 460 | 560 | 6 |
