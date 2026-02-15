# H_high / worst_H Escalation Plan — L0 Oranını Açma

**Amaç:** "Grid'de kötü aksiyon var" tek başına L1 sebebi olmasın; H_high/H_critical tetikleyicileri **seçilen aksiyonun H'si** veya **state-risk** üzerinden çalışsın.

---

## 1) Mevcut Davranış (Neden Hep L1?)

| Bileşen | Şu an ne kullanıyor? | Sonuç |
|--------|----------------------|--------|
| `fail_safe()` | `worst_J`, `worst_H` (tüm grid) | Grid'de tek bir aksiyon J/H kriterini aşarsa → override, safe_action |
| `compute_escalation_decision()` / `compute_escalation_level()` | **`worst_H`** (engine.py 251–265) | `worst_H >= h_high` → L1 (H_high); `worst_H > h_crit` → L2 (H_critical) |

Yani:
- **Seçilen aksiyon** güvenli olabilir (`mdm_H = 0`).
- Ama grid'de başka aksiyonların H'si yüksek (`worst_H ~ 0.86–0.92`).
- `worst_H >= H_MAX` (örn. 0.55) → **H_high** → L1.
- Sonuç: CSV'de satırların tamamı L1, escalation_driver çoğunlukla `H_high`.

**CSV kanıtı:** Son koşularda tipik durum: seçilen aksiyonun H’si ~0 (güvenli), worst_H ~0.86–0.92; cfg_H_CRIT=0.95 olduğu için L2 değil ama **H_high** yüzünden hep L1 / APPLY_CLAMPED. Yani L1’i tetikleyen “seçtiğin kararın zararı” değil, **aksiyon uzayında çok zararlı bir adayın var olması**. Grid’de yüksek severity gibi uç aksiyonlar üretildiği için harm monotonsa worst_H’ın sürekli yüksek çıkması normal; bu yüzden worst_H ile escalation L0’ı kolayca kilitler.

Bu bir **tasarım tercihi** (grid risk’e göre escalation); hedef **seçilen aksiyonun riski** (ve opsiyonel plausible set + belirsizlik) ile L0/L1 ayrımı.

---

## 2) Tavsiye Değerlendirmesi

Önerin:

> H_high (ve H_critical) tetikleyicileri **ya seçilen aksiyonun H'si** üzerinden, **ya da aksiyondan bağımsız state-risk** (state.risk, external p_damaging, evidence quality) üzerinden çalışmalı.  
> "Grid'de bir yerde kötü aksiyon var" → **tek başına** L1 sebebi olmamalı.

**Değerlendirme: Doğru.**

- **Seçilen aksiyonun H'si:** Mantıklı. Uyguladığımız aksiyon güvenliyse (H düşük) L0/L1’e çıkış “bu aksiyon riskli” demek olmaz; L1’i grid’deki başka aksiyonlara bağlamak kafa karıştırır ve L0 oranını kapatır.
- **State-risk (aksiyondan bağımsız):** Alternatif/ek kanal. Örn. `state.risk`, `external p_damaging`, evidence quality — bunlar “durum ne kadar belirsiz/riskli” diye L1 tetikleyebilir; grid’deki kötü aksiyon sayısından bağımsız.
- **worst_H’ı tamamen atmak zorunda değiliz:** Fail-safe (hiç geçerli aksiyon yok, safe_action’a düşme) için grid’e bakmak anlamlı. Sadece **H_high / H_critical → L1/L2 kararı** seçilen H (veya state-risk) ile verilmeli.

Özet: Tavsiye hem doğru hem uygulanabilir.

---

## 3) Hedef Davranış — Önerilen Kural Seti

**Ana fikir:** “worst_H yanlış” değil; **worst_H’ın kapsamı yanlış (tüm grid)**. Doğru kullanım: **seçilen aksiyon** ile L1/L2; worst_H yalnızca **plausible set** üstünde veya **belirsizlik yüksekken** devreye girmeli.

| Tetikleyici | Şu an | Önerilen kural |
|-------------|--------|------------------|
| **H_critical → L2** | `worst_H > h_crit` | **H_selected > H_crit** → L2 (sadece seçilen aksiyon) |
| **H_high → L1** | `worst_H >= h_high` | **H_selected >= h_high** → L1 (sadece seçilen aksiyon) |
| **fail_safe** (override, safe_action) | `worst_J`/`worst_H` | **Aynen kalsın** (grid’de geçerli aksiyon yoksa override doğru) |
| **worst_H’ın rolü** | Tüm escalation’da (tüm grid) | Yalnızca **gerçek belirsizlik** varsa: **H_plausible_worst** (top-k / pareto-front / constraint-valid adaylarda max H); uncertainty yüksek **ve** H_plausible_worst > H_high → L1 (örn. ayrı driver: `H_high_alt`) |

Böylece:
- “Uç bir aday var diye” sistem gereksiz yere L1’e kilitlenmez.
- “Karar gerçekten belirsizken tehlikeli alternatifler de yakınsa” yine temkinli davranır.
- worst_H telemetri/CSV’de kalır; escalation **kararı** seçilen H (ve opsiyonel plausible-worst + uncertainty) ile verilir.

---

## 4) Uygulama Planı

### Adım 1: Engine — escalation’a seçilen H’i ver

**Dosya:** `mdm_engine/engine.py`

- `compute_escalation_decision` ve `compute_escalation_level` çağrılarına şu an **`worst_H`** gidiyor (satır 251–265).
- **Yapılacak:** Seçilen aksiyonun H’ini kullan. `selected_scores` zaten var; `selected_scores.H`’i bir değişkene al (örn. `selected_H`).  
  - `selected_scores is None` ise (fail_safe / no_valid_fallback): o zaman **worst_H** kullanmak mantıklı (çünkü “güvenli” aksiyon yok, safe_action’a düşüyoruz).
- Yani:
  - `H_for_escalation = selected_scores.H if selected_scores is not None else worst_H`
  - `compute_escalation_decision(..., H_for_escalation, ...)` ve `compute_escalation_level(..., H_for_escalation, ...)`.

Bu tek değişiklikle H_high/H_critical seçilen aksiyonun H’ine göre tetiklenir; L0 oranı açılır.

### Adım 2: (Opsiyonel) State-risk kanalı

- İleride L1’i “state ne kadar riskli” ile de tetiklemek istersen:
  - `state.risk`, `external.p_damaging`, `input_quality` vb. ile bir **state_risk** skoru türet.
  - `compute_escalation_decision` / `compute_escalation_level` imzasına ek parametre (örn. `state_risk: Optional[float]`) eklenebilir; profil eşiği ile state_risk > eşik → L1.
- Bu planın zorunlu parçası değil; önce **selected_H** geçişi yeterli.

### Adım 3: (İsteğe bağlı) worst_H → plausible set + belirsizlik

- **H_plausible_worst:** Tüm grid yerine **top-k / pareto-front / constraint-valid** adaylarda max H.
- Eğer **uncertainty yüksek** (örn. CUS, as_norm veya confidence düşük) **ve** H_plausible_worst > H_high → L1 tetiklenebilir (örn. driver: `H_high_alt`). Bu sayede “gerçek belirsizlik varken tehlikeli alternatifler yakınsa” temkinli davranılır; “sadece grid’de uç aday var” tek başına L1 sebebi olmaz.

### Adım 4: Telemetri / CSV

- **worst_H** (ve ileride H_plausible_worst) çıktıda kalsın. Analiz ve “grid / plausible set ne kadar sert” görmek için faydalı.
- CSV’de `mdm_H` (seçilen) vs `mdm_worst_H` ayrımı; davranış değişince “H_high tetiklenen satırlarda mdm_H yüksek” beklenir.

### Adım 5: Test ve kalibrasyon

- **test_invariants.py:** Fail_safe / H_critical senaryoları seçilen aksiyon yokken (no valid candidates) hâlâ worst_H veya override mantığına dayanıyor olabilir; testlerin hâlâ geçtiğini kontrol et.
- **wiki_calibrated / canlı koşu:** Bir koşu atıp CSV’de L0 satırlarının artıp artmadığını ve escalation_driver dağılımının (H_high’ın seçilen H yüksek satırlarda kalması) beklendiği gibi olduğunu doğrula.

---

## 5) Kısa Checklist

- [ ] `engine.py`: `H_for_escalation = selected_scores.H if selected_scores is not None else worst_H` ve bu değerin `compute_escalation_decision` / `compute_escalation_level`’a gitmesi.
- [ ] `worst_H` çıktıda ve CSV’de aynen kalıyor (telemetri).
- [ ] `pytest tests/` yeşil.
- [ ] Canlı veya demo koşu → CSV’de L0 görülüyor; H_high tetiklenen satırlarda `mdm_H` yüksek.

---

## 6) Özet

- **Tavsiye doğru:** H_high/H_critical’ı seçilen aksiyonun H’ine bağlamak; “grid’de kötü aksiyon var” tek başına L1 sebebi olmasın. CSV kanıtı: seçilen H ~0, worst_H ~0.86–0.92 → H_high ile hep L1.
- **Nüans:** “worst_H yanlış” değil; **worst_H’ın kapsamı yanlış (tüm grid)**. Doğru kullanım: L1/L2 için **H_selected**; worst_H ise **plausible set** (top-k / pareto / constraint-valid) üstünden ve **sadece belirsizlik yüksekken** (örn. H_high_alt driver).
- **En küçük değişiklik:** Escalation kararında `worst_H` → `selected_H` (seçilen yoksa `worst_H`); fail_safe aynen. İsteğe bağlı: H_plausible_worst + uncertainty → L1.
- **Sonuç:** L0 oranı artar; “mdm_H=0 ama L1” tutarsızlığı kalkar.
