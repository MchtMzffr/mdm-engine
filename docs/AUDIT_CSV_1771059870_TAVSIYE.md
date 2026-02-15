# mdm_audit_1771059870.csv — Doğrulama ve Tavsiyeler

## Senin özetinle uyum

| Madde | Durum | Not |
|-------|--------|-----|
| External confidence | ✅ | 64/64 `confidence_source=external`, `confidence_used==confidence_external` |
| Drift history | ✅ | `drift_history_len` 1→60, ilk 29 warmup sonra mean |
| L0 yok / L1 spam | ⚠️ | 64/64 L1, 64/64 APPLY_CLAMPED, 59/64 mismatch |
| Kök sebep | ✅ | `escalation_driver`: as_norm_low (29) + as_norm_low\|temporal_drift:mean (35); `unc_as_norm` 59/64 = 0.0 |

Yani: **confidence + drift tarafı tamam; L0’ı kesen şey as_norm’un pratikte hep 0 gelmesi.**

---

## Bu koşu hangi kodla alındı?

CSV’de `unc_as_norm` **0.0** yazıyor. Repo’da yapılan fix:

- **core/uncertainty.py:** `<2 aday → as_norm = None` (artık 0 dönmüyor).
- **core/soft_override.py:** `as_norm is None` iken **as_norm_low tetiklenmiyor**.

Bu fix’in **deploy edildiği** bir koşuda:

- Tek aday (veya boş) event’lerde `unc_as_norm` CSV’de **boş veya N/A** olmalı, 0.0 değil.
- Bu event’lerde `escalation_driver` **as_norm_low** olmamalı; L0 çıkabilmeli.

**Sonuç:** Bu CSV büyük ihtimalle **fix öncesi** veya fix’in **audit pipeline’a henüz girmediği** bir koşudan. Önce bunu netleştirmek lazım.

---

## Tavsiye 1 — As_norm “missing ≠ 0” (zaten yapıldı, koşuyu tekrarla)

- **Kod:** `as_norm` hesaplanamıyorsa **None**; `compute_escalation_decision` içinde `as_norm is None` iken as_norm_low **tetiklenmiyor**. Bu repo’da uygulanmış durumda.
- **Yapılacak:** Aynı audit’i **güncel kodla** (fix’li engine ile) tekrar koş. Beklenti:
  - Çoğu satırda `unc_as_norm` boş/N/A, `escalation_driver` as_norm_low değil (none veya confidence_low).
  - L0 sayısı artar, L1 “as_norm_low” spam’i azalır.

İstersen CSV’de “missing”i daha okunur göstermek için audit tarafında `unc_as_norm` None iken hücreyi boş veya `"N/A"` yaz (aşağıda Tavsiye 3).

---

## Tavsiye 2 — Drift: mean sürekli tetikleniyor

- Bu CSV’de `mdm_cus_mean ~ 0.848`, `CUS_MEAN_THRESHOLD` muhtemelen 0.65 → warmup bittikten sonra **mean** hep tetikleniyor (35/64 as_norm_low|temporal_drift:mean).
- **Seçenekler:**
  1. **Wiki profilinde** `CUS_MEAN_THRESHOLD`’u yükselt (örn. 0.85–0.90), böylece sadece gerçekten yüksek CUS baseline’da tetiklensin.
  2. **Delta ağırlıklı:** Preemptive’i daha çok **delta** (trend değişimi) ile tetikle; mean’i sadece destekleyici veya daha yüksek eşikte kullan.
  3. **Quantile:** Warmup sonrası baseline’ın p90 üstüne çıkınca tetikle (ileride implementasyon).

En hızlı ve güvenli: wiki_calibrated (veya kullandığın profil) içinde `CUS_MEAN_THRESHOLD`’u 0.85 gibi bir değere çekmek.

---

## Tavsiye 3 — CSV’de None’ı 0 ile karıştırmayalım

- `unc_as_norm` **None** iken CSV’ye 0 yazılmamalı; “missing” belli olmalı.
- **audit_spec** (veya CSV’yi üreten yer): `unc_as_norm` için `None` ise hücreye `""` veya `"N/A"` yaz. Böylece sonraki analizlerde “0 mı, yoksa sinyal yok mu?” netleşir.

---

## Tavsiye 4 — İleride: preemptive_signal vs preemptive_applied

- Raw sinyal (`mdm_preemptive_escalation`) warmup’ta da True olabilir; “gerçekten escalation’a yansıdı mı?” driver’dan okunuyor.
- İleride iki alan ayrılabilir: `preemptive_signal` (raw), `preemptive_applied` (warmup sonrası escalation’a etki eden). Bu CSV yorumunu değiştirmez; ileride netlik için.

---

## Kısa aksiyon listesi

1. **Audit’i güncel kodla tekrarla** (as_norm None fix’li); L0 / escalation_driver / unc_as_norm dağılımını kontrol et.
2. **Wiki drift:** Profilde `CUS_MEAN_THRESHOLD`’u yükselt (örn. 0.85) veya mean’i delta’ya göre ikincil yap.
3. **CSV:** `unc_as_norm` None iken boş veya "N/A" yaz (opsiyonel ama önerilir).

Bu CSV’ye göre senin “confidence tamam, asıl sorun as_norm, drift mean kalibre edilsin” özeti doğru; bir sonraki adım fix’li koşuyu alıp aynı metrikleri tekrar okumak.
