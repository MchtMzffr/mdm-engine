# MDM — Marka ve Metin Rehberi

Tek kaynak: ürün adı, tagline ve kritik mesajlar (TR/EN). Repo/paket/CLI yeniden markalaşmasında bu metinler kullanılacak.

---

## Ürün adı

| Dil   | Metin |
|-------|--------|
| **TR** | Model Denetim Motoru (MDM) |
| **EN** | Model Oversight Engine |

*“Karar veren değil denetleyen” — audit + escalation + human review + clamp hepsi oversight çatısı altında.*

---

## Tagline (alt başlık)

| Dil   | Metin |
|-------|--------|
| **TR** | *L0/L1/L2 denetim, clamp, insan incelemesi ve uçtan uca audit/telemetri.* |
| **EN** | *L0/L1/L2 oversight, clamps, human-in-the-loop review, and end-to-end audit telemetry.* |

---

## README kritik ilk cümle (en üstte kullanılacak)

**TR:**

> MDM, modellerin verdiği kararları L0/L1/L2 seviyelerinde denetleyen; gerektiğinde frenleyen (clamp) ve insan incelemesine yükselten (L2) bir oversight motorudur.

**EN:**

> MDM is an oversight engine that monitors model decisions at L0/L1/L2, applies clamps when needed, and escalates to human review at L2.

---

## Teknik isimler (hedeflenen standart)

| Öğe        | Hedef      | Not |
|------------|------------|-----|
| Repo       | `mdm-engine` | Kısa, global kullanım |
| PyPI       | `mdm-engine` | `pip install mdm-engine` |
| Modül      | `mdm_engine` | `from mdm_engine import decide` |
| CLI        | `mdm`        | Örn. `mdm dashboard`, `mdm audit` |

**Not:** “MDM” bazı bağlamlarda Mobile Device Management anlamına gelir; genelde çakışma olmaz. Çakışma olursa alternatif kısa isimler: `mdo`, `moden`, `oversight` / `moe`.

---

## Dil varsayılanı

- **Varsayılan:** İngilizce (README, API docs, CLI mesajları).
- **Türkçe:** Tagline ve kritik mesajlarda TR+EN birlikte; isteğe bağlı README_TR veya docs/tr/.

---

*Son güncelleme: 2026-02-15*
