# Dashboard Refactor Planı — Persona Tabanlı UX

Bu belge, [paylaşılan tasarım önerisi](#) ile mevcut `visualization/dashboard.py` yapısını eşleştirir. SSOT (Decision Packet + CSV) korunur; hedef: **denetçi hızlı, mühendis teşhis edilebilir, akademisyen ölçülebilir**.

---

## 1. Mevcut yapı özeti

| Bileşen | Konum | Not |
|--------|--------|-----|
| Header | `main()` ~L1033 | Sadece title + badge; schema/adapter/session yok |
| Sidebar | `main()` ~L1039 | Data source + Live start/stop + JSONL yükle; **Run Filters / View Mode yok** |
| Navigasyon | `st.tabs` ~L1099 | 5 sekme: Monitor, Detail, Review, Search, Quality — **sıra sabit, Inbox default değil** |
| Veri kaynağı | `_audit_packets()` | `session_state["audit_packets"]`; live ise `_sync_live_packets()` |
| Flat/CSV | `decision_packet_to_flat_row`, `decision_packet_to_csv_row` | audit_spec; CSV'de `_csv_val(None)→"—"` (sayısal kolonlar için boş hücre tercih edilmeli) |
| Reason SSOT | Birçok yerde | `final_action_reason` öncelikli yapıldı; tek helper yok |
| LIVE_PACKETS | `tools/live_wiki_audit.py` | `list`; **maxlen yok** (öneri: `deque(maxlen=5000)`) |

---

## 2. Yeni helper'lar (tek yerden SSOT)

### 2.1 `_driver(packet)` — Gösterilecek neden (tek fonksiyon)

**Amaç:** UI/CSV/grafiklerde "neden" hep aynı sırayla: `final_action_reason` → `escalation_driver` → `mdm.reason`.

**Konum:** `dashboard.py` (veya `audit_spec.py` ortak kullanım için).

```python
def _driver(p: Dict) -> str:
    """SSOT: Gösterilecek neden (policy-facing)."""
    return (
        p.get("final_action_reason")
        or (p.get("mdm") or {}).get("escalation_driver")
        or (p.get("mdm") or {}).get("reason")
        or ""
    )
```

**Değiştirilecek yerler:**  
`_reason_breakdown`, `_render_review_queue` (expander başlığı + reason_driver), `_render_decision_detail` (Core vs Policy satırı), `_human_decision_summary` (reason), Quality heatmap (zaten `final_action_reason` kullanıyor).  
Flat row `reason` audit_spec'te; dashboard sadece packet kullanıyorsa `_driver(p)` kullanılabilir.

### 2.2 `_selection_reason(packet)` — Seçim gerekçesi

```python
def _selection_reason(p: Dict) -> str:
    """Action selector gerekçesi (pareto_tiebreak, max_score, fail_safe, no_valid_fallback)."""
    return (p.get("mdm") or {}).get("selection_reason") or ""
```

Detail ve Core signals expander'da kullan; tek kaynak.

### 2.3 `_export_rows(packets, *, format='csv'|'flat')` — Tek export builder

**Amaç:** "Full CSV" ve "tablo flat" aynı kolon haritasından gelsin; kolon listesi tek yerde.

- **Şu an:** `decision_packet_to_flat_row` (az kolon) ve `decision_packet_to_csv_row` (çok kolon) ayrı.
- **Yapılacak:**  
  - CSV için `decision_packet_to_csv_row` tek kaynak kalsın (zaten full).  
  - Tablo kolonları: "Compact" = flat_row’dan bir **kolon preset** (sadece seçili alanlar); "Advanced" = aynı CSV row’dan daha fazla kolon.  
  - Yani `column_presets` (aşağıda) flat/csv’den hangi key’lerin gösterileceğini seçsin; satır verisi hep `decision_packet_to_csv_row(p)` (veya flat için `decision_packet_to_flat_row`) ile üretilsin.  
- **Sonuç:** İndirilen CSV ile tablo aynı `decision_packet_to_csv_row` map’ini kullanır; "yeni kolonlar CSV’de yok" riski kalkar.

### 2.4 Kolon preset’leri: Compact / Advanced

**Compact (Denetçi):**  
`time | title | user | ores_decision | final_action_reason | evidence_status | p_damaging` (+ isteğe bağlı `input_quality`).

**Advanced (Mühendis/Research):**  
Compact + `frontier_size`, `pareto_gap`, `input_quality`, `valid_candidate_count`, `selection_reason`, `state_hash` (kısaltılmış), `config_hash` (kısaltılmış), `latency_ms`, `mdm_latency_ms`.

**Uygulama:**  
- `COLUMN_PRESETS = {"compact": [...], "advanced": [...]}` key listesi.  
- Tabloya verirken: `row = decision_packet_to_csv_row(p)` (veya flat_row); gösterilen kolonlar `COLUMN_PRESETS[view_mode]` ile filtrelenir.  
- Böylece "hangi export yolu geride kaldı?" tek builder ile çözülür.

---

## 3. Inbox-first routing (default landing)

**Kural:** `pending L2 > 0` ise açılış ekranı **Inbox (Review Queue)**.

**Mevcut:** `main()` içinde `st.tabs([Monitor, Detail, Review, Search, Quality])` — ilk sekme her zaman Monitor.

**Yapılacak:**  
- `pending = [p for p in packets if p.get("mdm", {}).get("level") == 2 and (p.get("review") or {}).get("status") == "pending"]`  
- Varsayılan sekme indeksi: `default_tab = 2 if pending else 0` (2 = Review).  
- Streamlit’te `st.tabs(..., default=default_tab)` benzeri doğrudan yok; **workaround:**  
  - `session_state["current_tab"]` ile ilk açılışta `2` (Inbox) set et; tab listesini **[Inbox, Monitor, Detail, Search, Quality]** sırasına çevir (Inbox birinci).  
  - Böylece ilk sekme Inbox olur; pending yoksa yine Inbox açık kalır ama kullanıcı hemen Monitor’e geçer.  
- Alternatif: Tab isimlerini aynı bırakıp sadece sırayı değiştir: **[Review, Monitor, Detail, Search, Quality]** ve `st.tabs(..., key="main_tabs")`; sayfa yüklenince `pending > 0` ise programatik olarak "Review" seçili göstermek Streamlit’te zor olabilir. **Pratik çözüm:** Sekme sırasını **[Inbox (Review), Live Monitor, Decision Detail, Search & Audit, Calibration & Quality]** yapıp, kullanıcıyı alıştırmak. İlk açılışta otomatik Inbox seçimi için `st.session_state` ile tab index’i set edip bir kez `st.tabs(..., key="main_tabs")` kullanıp, `st.tabs`’in seçimini query params veya session_state ile yönlendirmek (Streamlit’te tab seçimi state’i widget key’e bağlı).  
- **Önerilen basit davranış:** Sekmeleri sırayla **[Inbox, Live Monitor, Detail, Search, Calibration]** yap. Varsayılan "açılış"ı Inbox yapmak için: Sayfa ilk yüklendiğinde `if "initial_tab_set" not in st.session_state and pending: st.session_state["main_tab_index"] = 0` (Inbox = 0) ve tab container’da bu index’i kullanmak. Streamlit’te tab’in hangisinin seçili olduğu genelde widget state’inden gelir; bu yüzden "Inbox’ı en sola al + kullanıcıya bilgi ver" en az kodla uygulanabilir.

**Net adım:**  
1. Tab sırasını değiştir: **Inbox, Live Monitor, Decision Detail, Search & Audit, Calibration & Quality**.  
2. (Opsiyonel) Sayfa yüklenince `pending L2` varsa bir `st.info("You have N pending L2 reviews. Use the Inbox tab.")` üstte göster; tab sırası Inbox’ı öne çıkarsın.

---

## 4. Sayfa sayfa yerleşim → mevcut fonksiyon eşlemesi

| Tasarım sayfası | Mevcut | Yapılacak |
|-----------------|--------|-----------|
| **Inbox (Review Queue)** | `_render_review_queue` (tab3) | Inbox’ı ilk sekmeye al. Üstte 3 KPI: Pending L2, Avg decision time, Reject rate. Orta: kuyruk tablosu (Compact kolonlar). Sağ: "Review Workspace" (tek seçili) — 3 blok: Ne oldu? / Kanıt / Karar. Core vs Policy aynı kartta. Alt: kısayol bilgisi (A/R/N/P). |
| **Live Monitor** | `_render_live_monitor` (tab1) | KPI şeridi + grafikler + **Compact tablo** (6–8 kolon); Advanced modda ek kolonlar. Filtreler sidebar’a taşınabilir (Run Filters). |
| **Decision Detail** | `_render_decision_detail` (tab2) | 3 sütun: Sol Summary (badge, final_action, final_action_reason, core_level vs policy, selection_reason, config/schema/hash). Orta Evidence (diff, evidence_status, retry, compare link). Sağ Signals (Core & Quality expander). Alt: Raw packet JSON expander. |
| **Search & Audit** | `_render_search_audit` (tab4) | Filtre paneli (time range, user/title, level, final_action, driver, evidence_status, mismatch). Tablo: Compact/Advanced preset. Export: "current filtered set" JSONL + CSV (tek builder). L0 sampling 1/100. |
| **Calibration & Quality** | `_render_quality_panel` (tab5) | İki alt sekme: **(A) Calibration** (as_norm hist, CUS, drift bandları, reliability, frontier_size dağılımı; degenerate_driver_alarm none hariç, drift_driver_alarm, as_norm_missing). **(B) Quality** (L2 override rate, category dist, Driver→Reject heatmap [SSOT driver = final_action_reason], opsiyonel inter-annotator). |
| **Ops & Health** | Yok | Yeni sayfa veya Calibration altında blok: SSE errors, reconnect, backoff, ORES/MDM latency, cache hit, invariants fail count, replay_pass_rate. |
| **Settings / Help** | Sidebar (dil, tema) | View mode (Compact/Advanced), Column presets, Export format (CSV None: boş hücre), "How to read diff?" link/collapse. |

---

## 5. Üst bar (header) — her sayfada

**Mevcut:**  
`<div class="mdm-header">` içinde sadece title + badge.

**Eklenecek:**  
- Sol: **MDM Live Audit** + `schema_version` + `adapter_version` (packet’lerden alınan ilk değer veya env).  
- Orta: **Run/Session:** `session_id`, `config_profile` (dropdown veya son yüklenen packet’ten).  
- Sağ: **Durum rozetleri:** SSE (Connected/Reconnecting/Error), Packets/min, Pending L2 count, Queue age (en eski L2 kaç dk).

Bunlar için:  
- `schema_version` / `adapter_version`: Son packet’ten veya session’daki "last packet".  
- SSE/Packets/min: `_get_live_module()` + `LIVE_STATUS`.  
- Pending L2 / Queue age: `_audit_packets()` üzerinden hesaplanır.

---

## 6. Sidebar — sadece çalışma bağlamı

**Data Source:**  
- Live (EventStreams) — mevcut start/stop + sample_every.  
- JSONL yükle — mevcut file_uploader + dosya yolu.

**Run Filters (global):**  
- Config profile (multiselect).  
- Date/time range (offline için; packet `ts`).  
- External decision (FLAG/ALLOW).  
- Final action (APPLY / APPLY_CLAMPED / HOLD_REVIEW).  
- Mismatch only.

Bu filtreler şu an Live Monitor ve Search içinde; ortak bir `_filter_packets(packets, session_state)` fonksiyonu ile uygulanıp, hem tablo hem export’a aynı `filtered` listesi kullanılabilir.

**View Mode:**  
- Compact / Advanced (radio); `session_state["view_mode"]`.

**Language, Theme:**  
- Mevcut. Tema: "Sadece görsel accent" veya Settings’e taşı; Streamlit’in kendi temasıyla çakışmayacak şekilde.

---

## 7. CSV export: None = boş hücre

**Mevcut:** `audit_spec._csv_val(v)` → `None` için `"—"` döner; sayısal kolonlar Excel’de metin olur.

**Öneri:** CSV export için `None` → **boş string** `""`.  
- `decision_packet_to_csv_row` dict’i aynen kalsın (değerler `None` olabilir).  
- Export sırasında satırı string’e çevirirken: `_csv_val_export(v)` gibi bir fonksiyon kullan; `v is None` → `""`.  
- Dashboard’daki "indirilen CSV" bu export fonksiyonunu kullansın.  
- (İsteğe bağlı) Settings’te "CSV boş değer: boş hücre / —" seçeneği.

---

## 8. Rerun ve bellek

- **Rerun:** `time.sleep(1.5) + st.rerun()` yerine: Sadece `packets_sent` (veya LIVE_STATUS) değiştiyse rerun; veya `st_autorefresh` ile kontrollü periyot.  
- **LIVE_PACKETS:** `tools/live_wiki_audit.py` içinde `LIVE_PACKETS: list` → `collections.deque(maxlen=5000)` yapılması önerilir.

---

## 9. Evidence yoksa UX (L2)

- **Retry diff fetch** butonu (tek istek).  
- Compare linki (from/to revid) her zaman göster.  
- Decision Detail’da `evidence_status`, `evidence_error`, `http_status` (varsa) kısa göster.

---

## 10. Uygulama öncelik sırası (ROI)

1. **SSOT helper’lar:** `_driver(p)`, `_selection_reason(p)`; tüm reason gösterimlerini buna bağla.  
2. **Inbox sekme sırası:** İlk sekme Inbox (Review) yap.  
3. **Compact/Advanced + column_presets:** Tablolarda preset kolonları kullan; export’ı tek builder (`decision_packet_to_csv_row`) ile.  
4. **CSV None → boş:** Export tarafında `_csv_val_export(None) == ""`.  
5. **Header:** schema_version, adapter_version, Pending L2, SSE durumu.  
6. **Decision Detail 3 blok:** Summary | Evidence | Signals; Evidence’da retry + compare link + status.  
7. **Calibration alt sekme:** Calibration (model) | Quality (review_log); degenerate_driver_alarm none hariç (zaten yapıldı).  
8. **Sidebar Run Filters:** Ortak `_filter_packets`.  
9. **LIVE_PACKETS maxlen=5000.**  
10. **Ops & Health** blok veya sekme; tema notu (Settings’e taşı veya accent olarak bırak).

Bu sırayla ilerlenirse mevcut SSOT bozulmadan dashboard, denetçi/mühendis/akademisyen persona’larına göre netleşir ve "reason/driver SSOT, CSV None, as_norm/drift kalibrasyon, evidence yokken UX" önceki tespitleri de plana gömülmüş olur.

---

## 11. Son kontrol listesi (canlı koşu sonrası)

Bir sonraki canlı koşuda CSV ve UI’dan hızlı doğrula:

| Kontrol | Beklenti |
|--------|----------|
| `reason` kolonu | Her zaman **final_action_reason** ile aynı |
| `selection_reason` | fail_safe **sadece** final_action=HOLD_REVIEW satırlarında |
| Core→Policy UI | core_level ≠ mdm_level olan satırlarda "Core: Lx → Policy: Ly" satırı görünür |
| degenerate_driver_alarm | **none** yüzünden tetiklenmez (none hariç hesaplanıyor) |
| Hash | Aynı raw_state + config → aynı state_hash / config_hash (NaN/inf canonicalize edildi) |
| CSV numeric kolonlar | `p_damaging`, `input_quality`, `latency_ms`, `frontier_size` vb. **boş hücre** (None/NaN → ""); string "—" sayısal kolonlarda kullanılmamalı (pandas/Excel parse) |

Otomatik test: `tests/test_export_invariants.py` (flat row reason = final_action_reason; APPLY’da selection_reason ≠ fail_safe/no_valid_fallback; HOLD_REVIEW’da level=2; CSV mdm_reason = final_action_reason). Terminoloji: `docs/REASON_TERMINOLOGY.md`.

---

## 12. Sonraki sprint — “en iyi 5” (mühendis + akademisyen)

1. **Schema 1.3** — Yapıldı (engine_reason, final_action_reason_primary, core_level, driver priority).
2. **Golden packet fixtures** — `tests/fixtures/golden_packets/`: fail_safe, no_valid, L1 clamp, policy override, drift applied, constraint_violation (en az 6 senaryo); loader + CSV flatten kolon/ default doğrulama.
3. **Export/Display tek mapping** — Flat row / CSV row / UI tablo kolonları tek helper (column_presets) ile türesin; drift azalır.
4. **Slice dashboards** — Override rate ve driver dağılımı için band filtreleri: p_damaging (0–0.1 / 0.1–0.6 / 0.6+), evidence_status (OK vs MISSING/ERROR), config_profile.
5. **Replay panel (debug)** — state_hash / config_hash ile “replay pass/fail” ve diff; akademik determinism kanıtı.
