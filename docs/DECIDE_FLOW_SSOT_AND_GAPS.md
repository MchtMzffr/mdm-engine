# Karar akışı SSOT + Eksiklerin kapatılması

Bu belge: (1) tek bakışta karar akışı, (2) eksik/güçlendirilecek noktalar, (3) yapılan uygulamalar.

---

## 1) Karar akışı: decide() uçtan uca SSOT

**Tek gerçek pipeline:** `moral_decision_engine()` (mdm_engine/engine.py) = SSOT. Akış:

1. **raw_state + context** → state_encoder (x_ext, x_moral) + **input_quality / evidence_consistency** (missing_mask → missing_fields)
2. **action_generator** → coarse grid + refine (top-5 ±0.25) + SAFE_ACTION her zaman dahil
3. **moral_evaluator** → W, J, H, C per candidate
4. **constraint_validator** → valid/invalid + margin; **invalid_reason_counts** toplanır
5. **fail_safe** → worst_J / worst_H → override ise SAFE_ACTION + L2, reason=fail_safe
6. **Geçerli aday yoksa** → yine SAFE_ACTION + L2, driver=**no_valid_candidates**
7. **action_selector** → Pareto front + tie-break (margin → H → J → W → C); **selection_reason** = "pareto_tiebreak:margin>H>J>W>C" veya diğer
8. **confidence** → internal / external / used + margin (input_quality penalty uygulanır)
9. **uncertainty** → HI, DE, AS, CUS + divergence + as_norm_missing
10. **temporal_drift** → cus_history → mean/delta + warmup; **drift.driver** + **drift.applied**
11. **soft_override** → L0/L1/L2 + driver + hysteresis (H_high band dahil)
12. **L1 ise** → soft_clamp (severity/intervention azalt, delay artır)
13. **Trace + decision packet** → trace_hash, **state_hash**, **config_hash** (replay kanıtı)

Fail_safe kararı **worst_H / worst_J** üzerinden; seçilen aksiyonun skorları confidence/uncertainty ve margin için. (mdm_H vs H_critical ayrımı bu yüzden doğru.)

---

## 2) Eksikler — değerlendirme ve yapılanlar

| # | Öneri | Değerlendirme | Yapılan |
|---|--------|----------------|--------|
| **2.1** | missing_mask’in packet/CSV’de compact gösterimi | **Katılıyorum.** "input_quality 0.72" tek başına yetmez; *hangi alanlar eksik?* şart. | **Yapıldı.** `missing_fields`: eksik/geçersiz state alanları listesi (örn. `["risk","harm_sens"]`). Engine çıktısı + CSV kolonu. |
| **2.2** | Geçerli aday kalmadı (valid_candidate_count=0) | **Katılıyorum.** SAFE_ACTION + L2 + net driver; packet’te valid_candidate_count ve invalid_reason_counts. | **Yapıldı.** `no_valid_fallback` → escalation=2, escalation_drivers=\["no_valid_candidates"\]. `valid_candidate_count`, `invalid_reason_counts` (J_below_min: n, …) engine + CSV. |
| **2.3** | Pareto tie-break sırası net + selection_reason string | **Katılıyorum.** Denetimde "neden bu aksiyon?" tek bakışta. | **Yapıldı.** Tie-break sırası: margin max → H min → J max → W max → C max. `selection_reason` = "pareto_tiebreak:margin>H>J>W>C" (Pareto seçiminde). |
| **2.4** | confidence: internal / external / used / source | Zaten vardı. | **Korundu.** confidence_internal, confidence_external, confidence_used, confidence_source ("internal" \| "external"). İleride blend olursa "mixed" eklenebilir. |
| **2.5** | drift.driver + drift.applied (tek standarda bağlı) | **Katılıyorum.** driver = taxonomy (warmup/mean/delta/delta+mean); applied = sinyal gerçekten uygulandı mı. | **Yapıldı.** temporal_drift içinde `driver` + `applied` (bool). CSV: drift_applied. |
| **2.6** | Replay / determinism: state_hash + config_hash | **Katılıyorum.** Aynı packet replay’de aynı karar = denetim kanıtı. | **Yapıldı.** `state_hash`, `config_hash` (canonical JSON hash) engine çıktısında; CSV’ye eklenebilir. Replay’de aynı raw_state + config → aynı state_hash/config_hash ve trace_hash beklenir. |

---

## 3) Yapılan kod değişiklikleri (özet)

- **engine.py:**  
  - `invalid_reason_counts` constraint döngüsünde toplanıyor.  
  - `sel.reason == "no_valid_fallback"` → escalation=2, escalation_drivers=\["no_valid_candidates"\].  
  - `selection_reason` = "pareto_tiebreak:margin>H>J>W>C" (Pareto iken).  
  - temporal_drift_data’ya `applied` eklendi.  
  - Çıktıya: `missing_fields`, `valid_candidate_count`, `invalid_reason_counts`, `state_hash`, `config_hash`.
- **audit_spec.py:**  
  - CSV: `missing_fields` (noktalı virgülle), `valid_candidate_count`, `invalid_reason_counts` (reason:n;…), `state_hash`, `config_hash`, `drift_applied`.
- **core.state_encoder:** STATE_KEYS engine’de kullanılıyor (missing_fields türetmek için).

---

## 4) Hızlı doğrulama (L0/L1/L2)

- **L2 fail_safe:** worst_H > H_CRITICAL veya worst_J < J_CRITICAL → escalation_driver "fail_safe", selection_reason "fail_safe".  
- **L2 no_valid_candidates:** valid_candidate_count=0 → escalation_driver "no_valid_candidates", selection_reason "no_valid_fallback".  
- **L1:** confidence/margin/drift/as_norm → driver (constraint_violation, H_high, as_norm_low, temporal_drift:…) → soft_clamp uygulanır.  
- **L0:** driver "none", clamp yok.  
- **Pareto:** Geçerli adaylar varsa selection_reason "pareto_tiebreak:margin>H>J>W>C", frontier_size/pareto_gap dolu.

Sinyal → driver → aksiyon tutarlılığı: escalation_driver ve selection_reason pakette; CSV’de aynı alanlar kullanılıyor.
