# Adapter’dan Gelen Veri — Sorunların Kök Nedeni mi?

**Soru:** Bütün bu sorunların (L0 çıkmaması, H_high, şema karışıklığı vb.) temelinde **adapter’dan gelen verinin az olması** mı yatıyor?

**Kısa cevap:** **Hayır.** Kök neden tek başına “veri azlığı” değil. Ama adapter’ın verdiği **bilgi zenginliği** L0/H_high konusunda **yardımcı faktör** olabilir.

---

## 1) Hangi sorunlar var, kök nedenleri ne?

| Sorun | Kök neden | Adapter verisi ile ilişki |
|--------|-----------|----------------------------|
| **Hep L1, H_high** | Escalation kararında **worst_H** kullanılıyor (grid’deki en kötü H). Seçilen aksiyon güvenli olsa bile L1. | **Dolaylı.** Veri zengin değilse state belirsiz → grid’de birçok aksiyon yüksek H alabilir → worst_H yüksek. Ama asıl sebep **mantık**: seçilen H yerine worst_H kullanmak. |
| **Eski prefix / mdm_* karışıklığı** | Rebrand sonrası şema/kolon isimleri. | **Yok.** |
| **Compat / env** | Eski isimlerin kaldırılması, env önceliği. | **Yok.** |

Yani: **Tüm sorunların** ortak kök nedeni “adapter’dan veri az” **değil**. L0/H_high’ın **birincil** nedeni escalation mantığı (worst_H); adapter verisi **ikincil/aggravating** olabilir.

---

## 2) Wiki adapter gerçekten “az veri” mi gönderiyor?

Doğru çerçeve: **“az veri” değil; “az bağımsız sinyal / tekdüze sinyal”**.

**Alan sayısı (9/9 dolu):** Wiki adapter state’i **9 alanla** dolduruyor:  
`physical`, `social`, `context`, `risk`, `compassion`, `justice`, `harm_sens`, `responsibility`, `empathy`.  
Engine’in beklediği `STATE_KEYS` tamamı var → **missing_ratio = 0** görünür. Ama imputing / türetim yapıyorsan alanlar “dolu” olsa bile **missing_ratio = 0 tek başına anlamlı değil**; asıl soru bağımsız sinyal sayısı.

**Bilgi zenginliği (bağımsız sinyal sayısı):** Bu 9 alanın çoğu **1–2 kaynaktan** (örn. ORES `p_damaging`) türetilmiş:

- `risk = p_damaging`
- `harm_sens = 0.4 + 0.4 * risk`
- `justice = 0.9`, `compassion = 0.5`, `empathy = 0.5`, `responsibility = 0.6` (sabit/heuristic)
- `physical = 0.5`, `social = 0.3/0.6` (anon/bot’a göre)

Yani gerçek “veri” ağırlıklı olarak **1–2 sayı** (p_damaging, belki p_goodfaith + anon/bot). Diğerleri bu sayılardan veya sabitlerden türetilmiş. Bu anlamda **bilgi zenginliği düşük**: state çok sayıda alan içeriyor ama **az bağımsız sinyal / tekdüze sinyal**.

---

## 3) “Veri az” neyi tetikleyebilir?

- **Eksik alan (missing_fields):** Wiki’de yok; adapter tüm alanları dolduruyor.
- **Düşük bilgi zenginliği:** State büyük ölçüde 1–2 sayıya dayanıyor → encoder çıktısı “kaba” → aksiyon grid’inde birçok aksiyon benzer/yüksek H alabilir → **worst_H** kolayca yüksek kalır → H_high tetiklenir.  
  Bu, “adapter’dan gelen veri **az**” değil, “gelen veri **tekdüze / türetilmiş**” demek; yine de **escalation’ın worst_H’a bakması** asıl nedendir.

---

## 4) Sonuç ve tavsiye

- **Kök neden:** Tüm bu sorunların temelinde **tek başına** “adapter’dan gelen verinin az olması” **yatmayor**.  
  - L0/H_high için kök neden: **escalation’da worst_H kullanımı** (seçilen aksiyonun H’i kullanılmıyor).  
  - Şema/compat/env sorunları: isimlendirme ve mimari kararlar.

- **Adapter’ın rolü:**  
  - Adapter **alan sayısı** anlamında “az veri” göndermiyor (9/9 dolu).  
  - Adapter **bilgi zenginliği** anlamında sınırlı: çoğu alan tek kaynaktan türetilmiş. Bu, worst_H’ın sık yüksek kalmasını **kolaylaştırabilir**; yani **yardımcı faktör**.

- **Ne yapılmalı?**  
  1. **Öncelik:** Escalation’ı **seçilen aksiyonun H’ine** bağla (`docs/ESCALATION_H_HIGH_PLAN.md`). Bu, “veri az” olsa bile L0’ı açabilir.  
  2. **İsteğe bağlı:** Uzun vadede adapter’dan daha zengin sinyaller (ek ORES/context, gerçek evidence) eklenirse state daha ayırt edici olur; bu da L0/L1 dağılımını iyileştirir ama **kökte** “veri azlığı” değil, “worst_H ile escalation” vardı.
