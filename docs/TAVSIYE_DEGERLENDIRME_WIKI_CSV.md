# Tavsiye Değerlendirmesi — Wiki CSV ve Üç Aksiyon

Bu belge, `mdm_audit_1771060762.csv` ve “verilen tavsiye” metninin kod ve davranışla karşılaştırmalı değerlendirmesidir.

---

## 1) Tavsiyenin özeti

- **Ne denetliyoruz:** EventStreams → ORES (damaging/goodfaith) → dış karar (FLAG/ALLOW) → MDM bu kararı L0/L1/L2 ve final_action ile denetliyor. ✅ Doğru.
- **Bu CSV’de:** config_profile=scenario_test, confidence external 45/45, 44 L1 + 1 L2, unc_as_norm hep 0 → as_norm_low (ve drift mean) L1’e kilitliyor. ✅ Doğru.
- **“Confidence ORES’e bağlı değil”** bu CSV için artık geçerli değil. ✅ Kabul.
- **Üç aksiyon:** (A) Profil karışıklığını düzelt, (B) Wiki demo için as_norm_low’u kapat / drift eşiğini yükselt, (C) Telemetri ekle (valid_candidate_count, score_best, score_second, action_spread_raw, as_norm_missing).

---

## 2) Haklılık payı

| Tavsiye | Değerlendirme |
|--------|----------------|
| **A) Profil karışıklığı** | **Haklı.** Koşu `MDM_CONFIG_PROFILE` env ile alınıyor; default `scenario_test`. `wiki_calibrated` kullanmak için `MDM_CONFIG_PROFILE=wiki_calibrated` gerekir. Ek olarak **wiki_calibrated** profili paket içi profile loader’da kayıtlı değildi → `get_config("wiki_calibrated")` DEFAULT_CONFIG dönüyordu. **Yapılan:** `mdm_engine/config_profiles/__init__.py` içinde `wiki_calibrated` profili eklendi; artık `MDM_CONFIG_PROFILE=wiki_calibrated` ile koşunca gerçekten wiki_calibrated config kullanılır. |
| **B) Wiki demo: as_norm_low kapat / drift yükselt** | **Haklı.** CUS_mean ~0.849, default CUS_MEAN_THRESHOLD 0.65 → mean sürekli tetikleniyor. Wiki profilde `CUS_MEAN_THRESHOLD=0.88` zaten vardı. “as_norm_low’u kapat” için `AS_SOFT_THRESHOLD=0.0` önerisi: as_norm ∈ [0,1] olduğu için `as_norm < 0` hiç sağlanmaz → as_norm_low fiilen devre dışı kalır; ORES denetimi öne çıkar. İstersen wiki_calibrated’e `AS_SOFT_THRESHOLD: 0.0` ekleyebilirsin (demo modu). |
| **C) Telemetri** | **Haklı.** “as_norm=0 gerçek tie mi, missing mi?” sorusu CSV’den cevaplanamıyordu. **Yapılan:** Engine çıktısındaki `uncertainty` dict’e eklendi: `n_candidates`, `score_best`, `score_second`, `action_spread_raw`, `as_norm_missing`. Audit CSV’ye yansıyan kolonlar: `unc_n_candidates`, `unc_score_best`, `unc_score_second`, `unc_action_spread_raw`, `unc_as_norm_missing`. Böylece tek bakışta tie vs missing ayrımı yapılabiliyor. |

---

## 3) Yapılan kod değişiklikleri

1. **wiki_calibrated profil kaydı**  
   `mdm_engine/config_profiles/__init__.py`: `wiki_calibrated` import edilip `PROFILES` içine eklendi. Canlı koşuda `MDM_CONFIG_PROFILE=wiki_calibrated` kullanıldığında artık bu profil uygulanıyor.

2. **Uncertainty telemetri**  
   - **engine:** `uncertainty` dict’e `n_candidates`, `score_best`, `score_second`, `action_spread_raw`, `as_norm_missing` eklendi (ana seçim ve soft-clamp yolu).  
   - **audit_spec:** CSV satırına `unc_n_candidates`, `unc_score_best`, `unc_score_second`, `unc_action_spread_raw`, `unc_as_norm_missing` kolonları eklendi.

3. **Wiki demo (opsiyonel)**  
   Eğer “sadece ORES denetimi, as_norm_low yok” demek istersen `config_profiles/wiki_calibrated.py` içinde `AS_SOFT_THRESHOLD: 0.0` yapabilirsin; şu an 0.10 (L0’a biraz daha izin veren değer) bırakıldı.

---

## 4) Sonraki koşuda kontrol listesi

- Ortam: `MDM_CONFIG_PROFILE=wiki_calibrated` ile koş.
- CSV’de: `config_profile == wiki_calibrated`.
- Yeni kolonlar: `unc_n_candidates`, `unc_as_norm_missing`, `unc_action_spread_raw` → tie vs missing net.
- L0 oranı, `escalation_driver` dağılımı, drift mean tetiklenmesi (CUS_MEAN_THRESHOLD=0.88 ile) birlikte yorumlanabilir.

Özet: Tavsiye hem doğru okuma hem de aksiyonlar açısından haklı; (A) ve (C) kodla uygulandı, (B) için seçenekler dokümante edildi ve wiki_calibrated’te CUS_MEAN_THRESHOLD zaten yükseltilmiş durumda.

---

## 5) İkinci öneri değerlendirmesi (mdm_audit_1771102493 sonrası)

**Bağlam:** as_norm_low kapatıldıktan sonra koşulan CSV’de (1771102493) config_profile=wiki_calibrated doğru, ama **tüm satırlar L2 / HOLD_REVIEW**, escalation_driver **H_critical** (29) veya **H_critical|temporal_drift:mean** (3). İki farklı öneri karşılaştırılıp ortak öneri çıkarıldı.

### 5.1) Öneri A (ilk özet)

- SSE timeout: try/except ile yakala, LIVE_STATUS["error"] set et, thread temiz kapansın.
- Streamlit: `use_container_width` → `width="stretch"`.
- L2’lerin nedeni: H_critical (fail_safe); L0 için H eşiği veya state kalibrasyonu.

### 5.2) Öneri B (ikinci öneri)

- **“mdm_H=0 ama driver H_critical” tutarsızlığı:** H_critical koşulu bug’lı mı (örn. H≥0) yoksa etiket yanlış mı?
- **Çözüm:** CSV config snapshot’a **cfg_H_CRIT** ve **cfg_ENABLE_CONSTRAINTS** (veya constraint ile ilgili bayrak) ekle; mdm_H ile yan yana bakınca netleşir.
- **constraint_margin = -0.1 sabit:** Constraint sürekli ihlal ediliyor; wiki_calibrated’ta constraint’i kapat veya margin None ise tetikleme.
- **SSE:** try/except + **reconnect/backoff** (timeout=(5, None), thread crash etmesin, “reconnecting” göster).
- **Streamlit:** Aynı (use_container_width → width).

### 5.3) Kodla netleşen gerçek

- **mdm_H vs H_critical:** Engine’de escalation kararı **worst_H** (tüm aksiyonlar üzerinden max H) ile alınıyor; **mdm_H** ise **seçilen aksiyonun** (fail_safe’te safe action’ın) H’si. Yani H_critical tetiklenince seçilen aksiyon = safe_action → mdm_H düşük (0) olabilir; driver doğru, “bug” değil. Ama CSV’de bunu görmek için **worst_H** görünür olmalı.
- **constraint_margin -0.1:** Seçilen aksiyon (safe action) constraint kutusunun (J_MIN, H_MAX, …) dışında kaldığı için margin negatif. Fail_safe zaten L2’ye attığı için “constraint_violation” sırası gelmiyor; ama H’yi yükseltince bir sonraki engel constraint_margin < 0 → L1 olurdu.

### 5.4) Ortak öneri (uygulanan + önerilen)

| Madde | Öneri A | Öneri B | Ortak karar |
|-------|--------|--------|-------------|
| Streamlit | width="stretch" | Aynı | ✅ Uygulandı |
| SSE hata | try/except, status set, thread temiz bitir | try/except + reconnect/backoff | ✅ Önce try/except uygulandı; reconnect/backoff isteğe bağlı sonraki adım |
| H_critical / mdm_H=0 | — | cfg_H_CRIT + açıklama | ✅ **cfg_H_CRIT**, **cfg_H_MAX** CSV snapshot’a eklendi; **mdm_worst_H**, **mdm_worst_J** eklendi → “H_critical neden?” tek bakışta |
| Constraint / L0 | H eşiği veya state | wiki_calibrated’ta constraint kapat veya margin None | ✅ **wiki_calibrated**: **H_CRITICAL=0.95** (fail_safe sadece aşırı H’da), **H_MAX=0.55** (kutu gevşetildi, margin -0.1’ten çıkabilir) |

### 5.5) Yapılan kod değişiklikleri (birleşik)

1. **CSV config snapshot** (`audit_spec._config_snapshot_for_csv`): **cfg_H_CRIT**, **cfg_H_MAX** eklendi.
2. **Engine çıktısı:** **worst_H**, **worst_J** eklendi; packet’te **mdm["worst_H"]**, **mdm["worst_J"]**; CSV’de **mdm_worst_H**, **mdm_worst_J**.
3. **wiki_calibrated profili:** **H_CRITICAL=0.95**, **H_MAX=0.55** (constraint kutusu gevşetildi).
4. **SSE:** `run_live_loop` içinde `for msg in events` try/except ile sarıldı; `ConnectionError` → LIVE_STATUS["error"], LIVE_STATUS["connected"]=False.

### 5.6) Sonraki koşuda beklenen

- **cfg_H_CRIT=0.95**, **cfg_H_MAX=0.55** CSV’de görünür.
- **mdm_worst_H** ile “H_critical neden?” (worst_H > 0.95?) anında okunur.
- L2 oranı düşmeli; **APPLY (L0)** ve **APPLY_CLAMPED (L1)** artmalı. Hâlâ çoğunluk L2 ise bir sonraki adım: constraint_violation oranı ve gerekirse wiki_calibrated’ta constraint escalation’ı tamamen kapatacak bir bayrak (ileride eklenebilir).

---

## 6) Uygulama gerçeklik payı (tavsiyeleri uygulasak)

Tavsiyelerin **mantığı ve gerçeklik payı** yüksek; aşağıda **uygulama gerçekliği** — nereye gireceği, efor, bağımlılık ve risk — özetleniyor.

### 6.1) Madde madde

| # | Tavsiye | Nereye girer | Efor | Bağımlılık | Gerçeklik payı (uygulama) |
|---|--------|---------------|------|------------|---------------------------|
| **1** | Input quality / Evidence consistency | `state_encoder`: mask + quality vector; `engine`: confidence/CUS’a penalty; `audit_spec`: `input_quality`, `evidence_consistency` kolonları | Orta | **Adapter/domain:** Eksik alan oranı, kaynak güveni, cross-source uyuşmazlık adapter veya raw_state metadata’dan gelmeli | **Yüksek.** Core tarafı net: `encode_state` genişletilir, çıktıya `missing_mask` / `input_quality` eklenir; `compute_confidence` veya `compute_uncertainty` girişine quality penalty eklenir. Adapter’ın bu metrikleri üretmesi (Wiki: ORES vs internal vs diff) domain’e özgü ama arayüz tek: `raw_state` veya `context` ile verilir. |
| **2** | Coarse-to-fine (adaptif aday) | `action_generator`: grid → top-k → yerel refine (örn. 0.25 adım); engine sadece `generate_actions` çağrısını kullanır | Düşük–Orta | Yok (tamamen core) | **Yüksek.** Grid sabit; `generate_actions` içinde önce mevcut grid ile aday üret, skorla (moral_evaluator engine’de zaten var), en iyi 3–5’in çevresinde yeni noktalar ekle, tekrar skorla ve birleştir. Mevcut pipeline’ı bozmaz. |
| **3** | Pareto + tie-break | `action_selector`: Pareto front hesapla → domine edilmeyen adaylar → lexicographic tie-break (constraint margin → H min → J max → W/C); `uncertainty` veya ayrı sinyal: `frontier_size`, `pareto_gap` | Orta | Yok (core) | **Yüksek.** `select_action` girişi zaten `(candidates, fail_safe_result, weights)`; Pareto filtresi + tie-break burada. MoralScores (W,J,H,C) ve constraint_margin mevcut. Yeni sinyaller engine çıktısına ve audit_spec’e eklenir. |
| **4** | Sensitivity / robustness testi | State’i ±ε perturbe et → aynı aksiyon/level mi? Değilse CUS artır veya L1. Engine’de opsiyonel bir “post-step” veya ayrı `sensitivity_check()` | Düşük | Yok (core) | **Yüksek.** `encode_state` deterministik; `raw_state` değerlerine ±0.02 ekleyip tekrar `moral_decision_engine` çağırıp sonucu karşılaştırmak basit. İstersen sadece telemetri (flip: true/false), istersen CUS/level düzeltmesi. |
| **5** | Risk budget / soft penalty | `constraint_validator` veya `soft_override`: H_high → L1 (soft), H_critical → L2 (mevcut fail_safe). Fail_safe hard eşiği aynen kalır; önce “soft band” ceza ile skora katılır | Orta | Yok (core) | **Yüksek.** Mevcut `fail_safe` ve `validate_constraints` net. Ara katman: constraint margin veya H’ye göre penalty terimi `action_selector` skoruna eklenir; veya `compute_escalation_decision` öncesi H_high/H_critical ayrımı. |
| **6** | Drift: driver dağılımı | Son N kararda `escalation_driver` histogramı; bir driver’ın oranı ani sıçrarsa (örn. constraint_violation %5→%70) drift alarmı. `context["cus_history"]` benzeri `driver_history` veya audit/telemetri tarafında | Düşük | Yok (engine + audit/telemetri) | **Yüksek.** Engine zaten `escalation_drivers` listesini döndürüyor. Son N pakette driver sayıları tutulur (context veya ayrı servis); eşik aşımı alarm. CSV/dashboard’ta “driver dağılımı zaman serisi” eklenebilir. |

### 6.2) Bağımlılık özeti

- **Sadece core:** 2 (coarse-to-fine), 3 (Pareto), 4 (sensitivity), 5 (risk budget), 6 (driver dağılımı) — adapter’a ihtiyaç yok; mevcut `raw_state` ve `context` yeterli.
- **Adapter/domain girdisi isteyen:** 1 (input_quality, evidence_consistency). Bu metrikleri Wiki adapter’ı (örn. ORES vs FLAG, diff vs meta) üretebilir; core sadece `raw_state`/`context`’ten okuyup confidence/CUS’a yansıtır.

### 6.3) Önerilen uygulama sırası

1. **1 (Input quality)** — En kritik; adapter ile sözleşme netleştirilip core’da mask + penalty eklenir.  
2. **2 (Coarse-to-fine)** — Hızlı kazanım, as_norm_missing/tie azalır.  
3. **3 (Pareto + tie-break)** — Karar kalitesi ve denetlenebilirlik.  
4. **6 (Driver dağılımı)** — Telemetri/audit; drift “neden?” sorusuna cevap.  
5. **4 (Sensitivity)** — Opsiyonel modül; gürültüye dayanıklılık sinyali.  
6. **5 (Risk budget)** — İsteğe bağlı; fail_safe hard kalır, soft band eklenir.

### 6.4) Sonuç

**Uygulama gerçeklik payı yüksek.**

---

## 7) Uygulama sonuçları (yapılan kod değişiklikleri)

Tavsiyeler kodda uygulandı. Özet:

- **§1 Input quality:** `core/state_encoder.py` — `compute_input_quality(raw_state)`, `InputQualityResult`. Engine: `effective_confidence *= input_quality`. Çıktı + CSV: `input_quality`, `evidence_consistency`.
- **§2 Coarse-to-fine:** `core/action_generator.py` — `refine_actions_around(actions, step=0.25)`. Engine: grid → top 5 → refine → merge/dedupe.
- **§3 Pareto + tie-break:** `core/action_selector.py` — `select_action(..., config=co, use_pareto=True)`, `frontier_size`, `pareto_gap`. Çıktı + CSV: `frontier_size`, `pareto_gap`.
- **§4 Sensitivity:** `mdm_engine/engine.py` — `run_sensitivity_check(raw_state, ...)` (opsiyonel). Dönüş: `stable`, `flip_count`, `level_flip_count`.
- **§5 Risk budget:** `core/soft_override.py` — `h_high` (H_MAX); `H >= h_high` → L1. Engine: `h_high=h_max` geçirildi.
- **§6 Driver drift:** Engine: `context["driver_history"]` (son 50), `drift_driver_alarm`. Çıktı + CSV: `driver_history_len`, `drift_driver_alarm`.

Test: `tests/test_uncertainty_as_norm_none.py` geçiyor. Pareto açıkken `reason="pareto_tiebreak"`, `frontier_size`/`pareto_gap` dolu.

**Uygulama gerçeklik payı yüksek.** Hepsi mevcut mimariye (state_encoder → action_generator → moral_evaluator → constraint_validator → fail_safe → action_selector → confidence → uncertainty → soft_override → temporal_drift) eklenebilir; hiçbiri “core’u baştan yaz” gerektirmez. Tek gerçek bağımlılık: (1) için adapter’ın input_quality ve evidence_consistency metriklerini sağlaması; bu da domain’e göre (Wiki, sosyal medya, vb.) tek seferlik sözleşme.
