# MDM Test Stratejisi

**Amaç**: Az ama kapsayıcı testler — "tüm dünya senaryoları" imkansız (sonsuz durum uzayı), pratikte aynı etki: **çekirdek invariants + metamorfik test + kapsama odaklı senaryo seçimi** ve her çalıştırmada **ölçülebilir rapor**.

---

## 1) Ne Test Ediyoruz? — 6 Çekirdek İddia

Tüm testler aşağıdaki 6 iddiaya indirgenir:

| # | İddia | Açıklama |
|---|--------|----------|
| 1 | **Determinism (Replay)** | Aynı input → aynı output (+ aynı trace hash / aynı seçim). |
| 2 | **Safety invariants** | `action ∈ [0,1]^4`, chaos invariant, fail-safe kuralları bozulmaz. |
| 3 | **Escalation correctness** | L0/L1/L2 koşulları beklenen yönde tetiklenir; kapsam teşhisi (L0 yoksa neden). |
| 4 | **Uncertainty/Drift correctness** | CUS, ΔCUS, cus_mean mantıklı ve tutarlı çıkar. |
| 5 | **Soft clamp correctness** | CUS arttıkça aksiyon yumuşar, sınır dışına çıkmaz; Δconfidence tutarlı. |
| 6 | **Observability contract** | Trace schema (vX) alanları tutarlı; dashboard/CSV contract'ı bozmuyor. |

Bunları geçen bir sistem için "aynı tip testi çoğaltmak" gereksizdir.

---

## 2) Test Algoritması: Çekirdek + Metamorfik + Kapsama

### A) Çekirdek senaryolar (8–12 tip)

Her biri "dünya tiplerinden" birini temsil eder:

- **Safe-stable** (L0 hedefi)
- **Uncertain-but-safe** (L1 hedefi)
- **Constraint-violation / critical** (L2 hedefi)
- **High drift spike** (ΔCUS tetikler)
- **Mean-high** (cus_mean tetikler)
- **Soft clamp active** (CUS yüksek, L1)
- **Adversarial extremes** (yüksek compassion / justice conflict / harm explosion)
- **Chaos/bounds** (aksiyon sınırları doğrulanır)

### B) Metamorfik varyasyonlar (çekirdek başına 3–5)

- **noise_small**: raw_state'e küçük gürültü → sonuç "yakın" veya escalation mantıklı yönde.
- **scale_features**: Ölçekleme → adapter contract bozulmadıkça davranış uçmamalı.
- **increase_uncertainty_proxy**: Belirsizlik tetikleyen alanlar artar → CUS artmalı; L seviyesi düşmemeli (L0→L1/L2 olabilir).
- **swap_order_of_irrelevant_fields**: Dict key sırası değişse determinism bozulmamalı.
- **repeat_in_context**: Aynı senaryo ardışık ver → drift/mean hesapları tutarlı.

### C) Kapsama güdümlü seçici (Coverage-driven sampling)

Scenario generator'dan çok sayıda state üretilir; hepsi koşulmaz. Şu **kapsama hücrelerini** dolduran en küçük altküme seçilir:

- `level ∈ {0, 1, 2}`
- `soft_clamp ∈ {T, F}`
- `human_escalation ∈ {T, F}`
- `cus_bin ∈ {0–0.3, 0.3–0.6, 0.6–0.8, 0.8–1.0}`
- `delta_cus_bin ∈ {None, ≤0, 0–0.15, >0.15}`
- Boundary bins: (J low/med/high), (H low/med/high)

**Amaç**: Her hücreden en az 1 örnek → pratikte "tüm dünya"ya yakın kapsam.

### D) Sonuç raporu

Her çalıştırmada otomatik:

- Kaç hücre doldu / toplam hücre
- Hangi hücreler boş kaldı (örn. L0 yoksa burada görülür)
- En kötü 5 örnek (en yüksek CUS, ΔCUS, latency)
- Determinism fail var mı
- Invariant fail var mı

Bu rapor **kanıt** olur (CI artifact veya log).

---

## 3) Az Ama Kapsayıcı: 6 Çekirdek Test

| Test | İddia | Ne yapar |
|------|--------|----------|
| **Test-1** | Determinism + Replay | 20 random state; `decide(..., deterministic=True)` iki kez; `action`, `trace_hash`, replay ile aynı mı? |
| **Test-2** | Safety Invariants | 200 state (balanced/safe/chaos karışık); her sonuç için `action ∈ [0,1]^4`; fail-safe uygulandıysa bounds bozulmasın. |
| **Test-3** | Escalation Coverage | `scenario_test` + 200 state; L0, L1, L2 hepsi en az 1 kez görülmeli. Görülmüyorsa **teşhis**: config, cus dağılımı, worst J/H, öneri. |
| **Test-4** | Soft Clamp Metamorfik | Aynı state + belirsizlik artıran varyant; CUS artar → soft_clamp False→True olabilir (monotonluk); clamp aktifse raw vs final farkı olabilir. |
| **Test-5** | Temporal Drift | Aynı state 3 kez, araya "spike" state; ΔCUS histogram boş değil; spike sonrası preemptive_escalation beklenen yönde. |
| **Test-6** | Trace Contract | `build_decision_trace` çıktısında required alanlar; schema version; CSV export kolonları eksiksiz. |

Bu 6 test "az ama dünyayı kapsar".

---

## 4) Mevcut Testleri Sınıflandırma (A/B/C/D)

- **A (Core invariant)**: Mutlaka kalsın (yukarıdaki 6 başlıkla eşleşen).
- **B (Regression bug)**: Geçmişte bug yakaladıysa kalsın.
- **C (Duplicate)**: Aynı invariant'ı başka test zaten yakalıyorsa kaldırılabilir.
- **D (Slow)**: Nightly / CI schedule'a taşınır (Monte Carlo, Chaos).

Pratikte:

- Unit testlerin bir kısmı kalır; "senaryo tabanlı büyük testler" azaltılır.
- Monte Carlo / Chaos gibi ağır testler **nightly** olur; PR'da sadece çekirdek 6 + kısa kapsama seti koşar.

Ayrıntılı eşleme: `tests/TEST_CLASSIFICATION.md`.

---

## 5) L0 Görülmeme: Teşhis + Warning (Fail Değil)

L0 hiç yoksa rapor **teşhis + warning** üretir; test **fail etmez**. Bazı profillerde (örn. `production_safe`) L0 bilinçli az çıkabilir (policy choice). Rapor:

- Hangi config/profil ile koşuldu
- CUS dağılımı, worst_J / worst_H
- "Policy choice (sıkı profil) vs generator bug" ayrımı için not

Böylece "L0 yok" hem görünür hem de yanlış alarm fail’e yol açmaz.

---

## 6) Replay Garantileri

- **Replay hard guarantee**: Sabit state ile regression set (`run_all_tests` + çekirdek Test-1 sabit state). Zorunlu, fail = regresyon.
- **Random replay**: Rastgele state ile replay best-effort (non-blocking); bazı ortamlarda global random sırası nedeniyle birebir eşleşmeyebilir.

---

## 7) Kapsam Hedef Döngüsü

- **Çekirdek hücre seti**: `level × cus_bin × soft_clamp` (24 hücre).
- **Döngü**: Boş çekirdek hücre kaldıkça batch batch state üret, doldur; `max_states`’ta dur.
- **Rapor**: `target_cells_total`, `filled_cells`, `coverage_ratio`, `empty_cells`, `attempted_states`, `stop_reason` (`reached` | `max_states`).
- **Guided sampling / quantile / reachable**: `run_coverage_until_target` boş hücreye yönlendirme, quantile CUS binleri ve observed_reachable raporluyor. CI'da ratio &lt; 0.35 uyarı, &lt; 0.20 "sampler guidance required". CI’da coverage oranı %X altına düşerse warning veya fail.

---

## 8) Çalıştırma ve CI Stratejisi

- **PR / push**: `lint` + `run_core_tests.py` + kapsam hedef döngüsü (max 300 state). Artifact: `coverage_report.json`, `traces_live.jsonl`.
- **Nightly**: `run_all_tests.py` (Monte Carlo n=500, Chaos, adversarial). Workflow: `.github/workflows/nightly.yml`.

Böylece PR’da kimse beklemez; ağır kanıtlar nightly’de otomatik akar.
