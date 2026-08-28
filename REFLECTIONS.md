# wont — reflections

> Dated, append-only. Loose threads and things worth holding that are not
> decisions (those go to DECISIONS.md) and not lessons (LIBRARY.md). `/wakeup`
> reads the dates to flag entries that have gone stale.

- [2026-08-28] `scenarios/*/runs/` holds the one irreplaceable asset in this
  project — frozen human listening time — and it is gitignored by design (D19
  tier 1). It is therefore one `rm -rf` from gone, and no repo gate can protect
  it. Confirm the capture dir sits under a backed-up / synced path before real
  capture sessions accumulate.
- [2026-08-28] The DESIGN §8 policy knobs (slice threshold + hysteresis,
  min-span length, value normalization) are deliberately deferred to Phase-2
  build time, which makes them easy to slide past unnoticed while writing the
  slicer. Decide them explicitly, with the reasoning recorded, rather than
  letting the first implementation become the default by accident.
- [2026-08-28] Wend has not been told about response-2's per-run-pooling ruling,
  and it lands on Wend's own architecture: the D10 staging buffer is an
  attribution + cross-scope render-efficiency lever, NOT within-scope
  statistical power ([L0005]). Wend's agent may still believe parallel scoped
  sessions multiply significance. A cross-repo notice is owed (INTEGRATIONS.md
  governs; writes stay home).
- [2026-08-28] Two drafts were written into Tonality's channel this session
  (`brief-2.md`, `ack-per-run-pooling.md`). brief-2 was filed; the ack was
  reported handled. Worth a glance that both actually landed as intended —
  channel artifacts written by one repo into another are exactly the kind of
  thing that silently half-lands.
