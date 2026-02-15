# Reason / Driver terminolojisi (SSOT)

Dashboard, CSV ve dokümanda tutarlı isimlendirme için üç alan net ayrılır.

---

## 1. `final_action_reason` — **policy-facing** (SSOT, UI başlık)

- **Anlam:** İnsana gösterilen “bu karar neden böyle?” — policy katmanı dahil.
- **Kullanım:** UI başlık, kuyruk tablosu, CSV `reason`/`mdm_reason`, grafik “Reason breakdown”.
- **Örnekler:** `wiki:ores_flag_disagree`, `confidence_low`, `fail_safe`, `none`, `constraint_violation`, `temporal_drift:delta`.
- **Kaynak:** Packet’te `final_action_reason`; wiki override varsa `wiki:ores_flag_disagree`, yoksa engine’in escalation_driver’ı (veya mdm.reason fallback).

---

## 2. `mdm.engine_reason` — **core / engine driver**

- **Anlam:** Motorun “çekirdek teşhis”i; policy override öncesi escalation nedeni.
- **Kullanım:** Debug, Decision Detail “Engine reason” satırı, mühendis teşhisi.
- **Örnekler:** `fail_safe`, `confidence_low`, `constraint_violation`, `as_norm_low`, `none`.
- **Kaynak:** Engine çıktısı `escalation_driver` veya `reason`; policy katmanı bunu değiştirmez, sadece `mdm.reason` (policy-facing) override edilebilir.

---

## 3. `mdm.selection_reason` — **optimizer / action_selector gerekçesi**

- **Anlam:** Aksiyon seçiminin nedenini açıklar (Pareto tiebreak, max_score, fail_safe, no_valid_fallback).
- **Kullanım:** Detail “Selection reason”, CSV `selection_reason`, regresyon/export invariant testleri.
- **Örnekler:** `pareto_tiebreak:margin>H>J>W>C`, `max_score`, `fail_safe`, `no_valid_fallback`.
- **Kaynak:** Sadece action_selector; flatten/CSV path’leri bu alanı override etmemeli.

---

## Kısa özet

| Alan | Rol | UI/CSV önceliği |
|------|-----|------------------|
| `final_action_reason` | Policy-facing SSOT | Başlık, tablo, CSV reason |
| `mdm.engine_reason` | Core teşhis | Detail “Engine reason”, debug |
| `mdm.selection_reason` | Seçim gerekçesi | Detail, CSV selection_reason |

Export invariant’lar: `reason`/`mdm_reason` = `final_action_reason`; `selection_reason` sadece action_selector’dan; HOLD_REVIEW dışında `selection_reason` ∈ {fail_safe, no_valid_fallback} olamaz.
