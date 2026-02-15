# Karar invariants, hash determinism, schema 1.2, operasyon metrikleri

## 1) Karar invariants (test + runtime assert)

Paket/CSV'de **asla bozulmaması gereken** kurallar:

| Kural | Açıklama |
|-------|----------|
| driver == "fail_safe" | ⇒ level == 2 AND final_action == HOLD_REVIEW AND clamp_applied == False |
| driver == "no_valid_candidates" | ⇒ level == 2 AND valid_candidate_count == 0 |
| level == 1 | ⇒ clamp_applied == True |
| level == 0 | ⇒ driver == "none" |
| constraint_margin < 0 | ⇒ driver en az constraint_violation içermeli |

- **Test:** `mdm_engine.invariants.check_decision_invariants(packet)` → ihlal listesi. `tests/test_invariants.py`.
- **Debug:** `context["assert_invariants"] = True` veya `MDM_ASSERT_INVARIANTS=1` ile engine çıkışında assert.

## 2) Hash determinism

- **state_hash / config_hash:** Float 1e-6 quantize, key/liste sıralı (`_canonical_for_hash`).
- **missing_fields:** Alfabetik sıra.
- **invalid_reason_counts:** Alfabetik sıra (`sorted(counts.items())`).

## 3) Schema 1.2 + geri uyumluluk

- **SCHEMA_VERSION = "1.2"** (live_wiki_audit).
- Eski kayıt: missing_fields yoksa `[]`, drift_applied yoksa NA, invalid_reason_counts yoksa `{}`.

## 4) Operasyon metrikleri (6 metrik)

`mdm_engine.operasyon_metrics.compute_operasyon_metrics(packets)`:

- **L0_rate** — L0 oranı (%)
- **L2_backlog_rate** — no_valid + fail_safe L2 oranı
- **driver_distribution** + **driver_max_pct** — degenerate_driver_alarm (tek driver %80+)
- **override_rate** — L2 Reject %
- **mismatch_rate** — external vs final_action
- **replay_pass_rate** — (opsiyonel) aynı packet → aynı hash

## 5) Golden packet set (driver bazlı)

Her driver için 1–2 sabit fixture ile regression ve dashboard görsel testi yapılabilir. Fixture’lar: fail_safe, no_valid_candidates, as_norm_low, constraint_violation, H_high, temporal_drift:mean/delta, divergence_high, confidence_low. İleride `tests/fixtures/golden_packets/` veya beklenen alan kataloğu eklenebilir.
