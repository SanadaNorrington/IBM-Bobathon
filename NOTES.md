# What I checked, and what the agent got wrong

## What the agent got wrong

The agent's actual code was fine. Every bug fix it made was correct — I checked each one by
running it, not by reading it. Its mistakes were all about what it *didn't* do and what it
didn't tell me.

**It stopped at 8 of 10 steps and handed the job back as if it were finished.** `analyze.py`
was completely untouched — still had the `# your analysis here` placeholder in it — and
`NOTES.md` was the blank template. That is the whole "make it smarter" capstone missing. It
never said "I skipped these." I only found it because I ran `verify.py` instead of trusting
the summary it gave me. This is the thing I'd watch for next time: an agent will tell you what
it did and stay quiet about what it didn't.

**It made a real design decision without flagging it.** To stop a car with no last-service
reading from being falsely flagged, it made the car's own odometer the baseline. That passes
the test — but it means a car with a missing reading now reports 0% wear *forever* and can
never be flagged again. It traded a false alarm for a car that quietly disappears out of the
report. VOS-7788 sits at 92,000 km and the nightly run had nothing to say about it. The fix
isn't wrong, but that consequence should have been said out loud, so I changed the report to
count those cars and print a warning line instead of swallowing them.

**It invented a fact.** It edited the header comments of `km_wachter.py` and `fleet_report.py`
to say "Cleaned up 2024". It's 2026. Small, but it's the agent writing something into the code
that simply isn't true, and nothing in the test suite would ever catch that.

**It skipped the "tell me before you fix it" instruction.** Step 7 asked it to report what it
found in the helper files and let me decide what to delete. It deleted nothing — instead it
wrote polished docstrings onto five functions that no code calls, which makes dead code look
maintained. `is_due` was the worst of them: a second, competing copy of `needs_service`. I
removed those.

## What I checked before I accepted its work

I didn't read the diff and nod. I ran things:

- `pytest` — 4 tests passed at the time (6 now that I added two more).
- `python verify.py` — this is what caught the two missing steps. 9 of 11 PASS, and the two
  FAILs were real.
- I ran `print_report` against `fleet_sample.json` end to end, not just the unit tests, to see
  the nightly output a human would actually read.
- **The 80% rule and the 15,000 km interval:** I asserted `SERVICE_INTERVAL_KM == 15000` and
  `WARN_AT_PERCENT == 80` directly, and confirmed `settings.cfg` is not in `git status` at all,
  so the rule values in the file are byte-for-byte untouched.
- **The wear bug:** `wear_percent(14900, 15000)` now returns 99.3, not 0. The old code used
  `//`, so anything short of a full 15,000 km window floored to zero — a car at 14,900 km
  reported 0% wear and was invisible. That's the bug that mattered most.
- **The mileage bug:** `MILES_PER_KM` was 1.609, which is km-*per-mile*, i.e. the conversion
  was upside down. The UK partner report was inflating fleet distance by about 2.6x. 100 km
  now reads 62.1 miles.
- I checked every "dead" function actually had zero callers before deleting it. `get_int`
  looked dead too — but `verify.py` itself calls it, so it stayed.

## What the data actually said

**The obvious answer is wrong, and the data is blunt about it.** Total mileage does not predict
breakdowns here. Cars that broke down averaged 53,448 km; cars that didn't averaged 53,302 km.
That's a 146 km gap on a ~53,000 km average — noise. As a ranking signal it scores AUC 0.493,
which is worse than a coin flip. Age is the same story: 5.88 years vs 5.89 years, AUC 0.513.

The reason is structural, and it makes sense once you see it: `odometer_km` and `age_years`
correlate at 0.98 — they're the same fact recorded twice — and because this fleet services on
mileage, every car gets pulled into the same odometer band regardless. There's nothing left for
them to separate.

What actually predicts a breakdown:

| Factor | Healthy | Broke down | AUC |
|---|---|---|---|
| `km_since_service` | 7,261 km | 11,678 km | **0.786** |
| `avg_daily_km` | 131 | 160 | **0.677** |
| `load_factor` | 0.51 | 0.60 | **0.652** |
| `age_years` | 5.89 | 5.88 | 0.513 (nothing) |
| `odometer_km` | 53,302 | 53,448 | 0.493 (nothing) |

So it's not how far a car has been driven in its life — it's **how overdue it is right now, and
how hard it's being worked**. `avg_daily_km` and `load_factor` correlate at 0.88, so they're
really one signal ("intensity"), not two, and I weighted them as one.

My risk score is 50% overdue-ness + 50% intensity, scored 0–100. It ranks at AUC 0.859 against
0.747 for the 80% rule alone, and it's within a whisker of a full logistic regression (0.863) —
which tells me the simple, explainable version gives up essentially nothing. I checked it isn't
tuned to a knife edge: anywhere from 45/55 to 60/40 gives the same answer.

**The payoff:** 9 of the 26 breakdowns — 35% — happened to cars still *inside* their service
window, so the 80% rule would never have flagged them at all. Those are the cars this score is
for. Of the 10 highest-risk cars the 80% rule hasn't flagged, 4 went on to break down, against
a fleet base rate of 22%.
