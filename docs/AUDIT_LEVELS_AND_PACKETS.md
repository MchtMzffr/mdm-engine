# L0/L1/L2 Denetim Sözlüğü ve Decision Packet

Bu belge, hangi sisteme bağlanırsa bağlansın aynı mantıkla çalışacak **denetim seviyeleri** ve **Decision Packet** şemasını tanımlar.

## 1) L0 / L1 / L2: Sistemin ne yapacağı

| Seviye | Anlam | Sistemin yapacağı | Dashboard |
|--------|--------|-------------------|-----------|
| **L0** | Güvenli, otomatik karar uygulanabilir | Kararı uygula; Decision Packet kaydet; isteğe bağlı %1–5 sampling review | ✅ L0: OK + explain + "Open details" |
| **L1** | Sınırda, yumuşak müdahale | Kararı uygula ama kısıtla (throttle/limit); opsiyonel L1 review kuyruğu | ⚠️ L1: Clamp Applied + sebep + "Promote to L2" |
| **L2** | Dur / İnsan incelemesi zorunlu | Otomatik etki 0; Review Queue'ya düşür; Approve/Reject/Kategori+Not | 🛑 L2: Human required + içerik/diff + aksiyonlar |

Kod: `mdm_engine.audit_spec.LEVEL_SPEC` ve `get_level_spec(level)`.

## 2) Decision Packet (tek standart çıktı)

Her seviyede (L0/L1/L2) aynı JSON yapısı kullanılır. Kaynak: canlı akış, simülasyon veya başka adapter.

```json
{
  "run_id": "...",
  "ts": 1739...,
  "source": "wikimedia_recentchange",
  "entity_id": "user:Foo",
  "external": {
    "decision": "FLAG",
    "p_damaging": 0.82,
    "p_goodfaith": 0.11,
    "model": "ores damaging|goodfaith"
  },
  "input": {
    "title": "...",
    "user": "...",
    "revid": 123,
    "comment": "...",
    "evidence": { "diff": "...", "links": ["..."] }
  },
  "mdm": {
    "level": 2,
    "reason": "fail_safe",
    "soft_clamp": false,
    "signals": { "cus": 0.91, "cus_mean": 0.88, "divergence": 0.42, "constraint_margin": -0.05 },
    "explain": "İnsan incelemesi gerekli: ...",
    "human_escalation": true
  },
  "review": {
    "status": "pending|resolved",
    "decision": "approve|reject",
    "category": "false_positive|irony|...",
    "note": "..."
  }
}
```

- **L0** da aynı paketi üretir; `review` boş veya yok.
- **L2** olunca `review.status: "pending"`; insan kararı sonrası `resolved`, `decision`, `category`, `note`.

Oluşturma: `mdm_engine.audit_spec.build_decision_packet(...)`.

### Tek kaynak (SSOT) ve CSV

* **SSOT = Decision Packet JSONL** — Tam delil tek kaynaktır; canlı akış veya export JSONL olarak saklanır.
* **CSV = audit_full (analitik)** — Filtre ve teşhis için flatten görünüm; “tam teşhis” için yeterli kolonlar.

### CSV export kolonları (audit_full)

Dashboard’dan **Download CSV (full)** ile indirilen CSV aşağıdaki kolonları içerir. **Kararı ORES mi mapping mi belirliyor?** sorusu için `mdm_input_risk` ile `ores_p_damaging` yan yana kullanılır.

| Kolon | Açıklama |
|-------|----------|
| `time`, `latency_ms`, `run_id`, `title`, `user`, `revid`, `comment` | Kimlik ve gecikme |
| **ORES** | `ores_decision`, `ores_p_damaging`, `ores_p_goodfaith`, `ores_threshold`, `ores_model` |
| **MDM input (kritik)** | `mdm_input_risk` — MDM’ye giden risk (mapping çıktısı); ORES `p_damaging` ile karşılaştır |
| **Final action** | `final_action`: APPLY / APPLY_CLAMPED / HOLD_REVIEW |
| **Frenleme** | `clamp_applied`, `clamp_types`, `clamp_count`, `mdm_soft_clamp` + confidence, cus, divergence, delta_cus, preemptive_escalation, delta_confidence |
| **Aksiyon / skor** | `mdm_action_*`, `mdm_J`, `mdm_H` |
| **Uncertainty** | `unc_*` |
| **Evidence / review** | `diff_available`, `review_status`, `review_decision`, `review_category`, `review_note` |

**ORES kontrolü:** `ores_decision` + `ores_p_damaging` (dış karar) vs `mdm_input_risk` (MDM’ye giren) vs `mdm_level` / `final_action` (MDM çıktısı) aynı satırda; mapping ve eşikleri böyle doğrularsın.

**CSV sayı alanları:** Analiz araçları (pandas, Excel) için sayı olmayan değerler **null/boş** olmalı; metin placeholder (“—”) kullanılmamalı. Eksik sayılar CSV’de boş hücre veya NaN; string “—” sadece gerçekten metin kolonlarında.

---

### Konumlama: ORES vs MDM

* **ORES “öneriyi” belirler** → `ores_decision` (FLAG/ALLOW)
* **MDM “uygulamayı” belirler** → `final_action` (APPLY | APPLY_CLAMPED | HOLD_REVIEW) + `final_action_reason`

Tek kolonda operasyonel gerçeklik: `final_action`. Mismatch = ORES ALLOW ama MDM L1/L2, veya ORES FLAG ama MDM L0 → `mismatch=1` (dashboard’da filtre: “Sadece uyumsuzlar”).

---

### Kontrol listesi (doğrulama)

* `mdm_cus` ile `unc_cus` aynı kaynaktan (uncertainty); ikisi de CSV’de → drift/bug kontrolü.
* `temporal_drift.cus_mean` = `mdm_cus_mean` (signals, drift’ten).
* `soft_safe_applied` ↔ `mdm_soft_clamp` aynı (engine çıktısı).
* Action boyutları (severity, intervention, compassion, delay) = karar vektörü; clamp = fren (liste: `clamps`, `clamp_types`, `clamp_strength`).

---

### Review kalıcılığı

L2’de Onayla/Red + kategori + not → `review_log.jsonl` dosyasına append (env: `MDM_REVIEW_LOG`). Dashboard **Kalite** sekmesi: L2 override rate, kategori dağılımı, reason→override (hangi `mdm_reason` çok Red üretiyor).

### Şema sürümü ve canlı izleme alanları (v1.1)

Packet ve CSV’de aşağıdaki alanlar bulunur; eski kayıtlarda yoksa boş/default kabul edilir.

| Alan | Açıklama |
|------|----------|
| `schema_version` | Örn. `"1.1"` — dashboard uyumluluk |
| `adapter_version` | Örn. `"wiki-ores-1.0"` |
| `source_event_id` | EventStreams `meta.id` veya composite; **dedupe** (tekrarlı SSE/rerun önleme) |
| `config_profile`, `git_commit`, `host`, `session_id` | Koşu bağlamı (“neden dün farklıydı?”) |
| `mdm_latency_ms`, `sse_wait_ms` | Gecikme parçalama (ORES sonrası MDM süresi; SSE bekleme) |
| `ores_cache_hit`, `ores_retry_count`, `ores_backoff_ms` | ORES cache (revid) ve 429/timeout retry görünürlüğü |
| L2 **diff** | `fetch_wiki_diff(from_revid, to_revid)` — MediaWiki API `action=compare` ile doldurulur |

Kalite ekranı: **Kalite** sekmesinde L2 override rate (Reject %), kategori dağılımı, **escalation_driver** (veya final_action_reason) → Approve/Reject bar grafiği.

### Kalite ↔ ground truth

* **L2 review** = zorunlu ground truth kaynağı (insan Onayla/Red + kategori).
* **L0 sampling review** = kaçırılan hataları görmek için şart (örn. her 100 L0’dan 1’i inceleme).
* “YZ kalitesi” metrikleri: L2 override rate; kategori dağılımı; **driver → override** (hangi escalation_driver yanlış pozitif üretiyor). MDM denetlerken aslında YZ’nin kalitesi de ölçülür.

## 3) Explain (anlaşılır açıklama)

Dashboard’da sadece metrik değil, **insan dilinde tek paragraf** gösterilir:

- **L2:** "İnsan incelemesi gerekli: {reason_human}. Dış skor: {p}. Sinyaller: CUS=..., margin=..., divergence=..."
- **L1:** "Sınırda karar: clamp uygulandı. Sebep: {top1}. Dış karar: {external}. Öneri: gerekirse L2'ye yükselt."
- **L0:** "Güvenli: belirsizlik düşük, kanıt tutarlı. Dış karar: {external}."

Üretim: `mdm_engine.audit_spec.explain_for_level(level, reason, signals, external_decision)`.

## 4) Engine çıktısından sinyaller

`decide()` çıktısında şunlar **kesin** var:

- `escalation`, `reason`, `soft_safe_applied`
- `uncertainty` (içinde `cus`, `divergence`)
- `constraint_margin`
- `temporal_drift` (içinde `cus_mean`)

Dashboard’daki "Explain + Top Signals" bu alanlarla doldurulur.  
Sinyalleri toplamak: `mdm_engine.audit_spec.extract_mdm_signals(engine_result)`.

## 5) Dashboard’da 5 bölüm

| Bölüm | Amaç |
|-------|------|
| **A) Live Monitor** | Events/min, L0/L1/L2 oranı, son 200 event tablosu, filtreler (level, FLAG/ALLOW). Satıra tıklayınca detay. |
| **B) Decision Detail** | Seçili packet: özet, explain, dış karar, sinyaller, içerik/diff, L2 ise Approve/Reject + kategori + not. |
| **C) Review Queue** | Sadece L2 + status=pending. Liste, detay aç, Onayla/Red. |
| **D) Search & Audit** | Tarih/user/title/level filtre, L0 sampling (örn. her 100 L0’dan 1’i), sonuçtan detay aç. |
| **E) Kalite** | review_log.jsonl: L2 override rate (Reject %), kategori dağılımı, reason→override (hangi mdm_reason Red üretiyor). |

Veri: Decision Packet JSONL yüklenir (`tools/live_wiki_audit.py --jsonl dosya.jsonl` ile üretilir).

### Veriyi hemen görmek (canlı akış butonu tetiklenmiyorsa)

1. **Terminalde** (repo kökünde):  
   `python tools/live_wiki_audit.py --sample-every 5 --jsonl mdm_live.jsonl`  
   Birkaç paket gelene kadar bekleyin (ör. 20–30 sn), Ctrl+C ile durdurun.  
   Varsayılan config profili **wiki_calibrated** (CUS_MEAN_THRESHOLD, AS_SOFT_THRESHOLD kalibre). Farklı profil için `MDM_CONFIG_PROFILE=scenario_test` gibi ortam değişkeni kullanın.

2. **Dashboard:**  
   `streamlit run visualization/dashboard.py` → tarayıcıda açın.

3. **Sidebar:** "JSONL dosya yolundan yükle" alanına `mdm_live.jsonl` yazın, **Dosyadan yükle** butonuna tıklayın.

4. Canlı İzleme sekmesinde paketler görünür; tablo, grafikler ve CSV indir kullanılabilir.

## 6) Farklı kaynağa geçiş — Adapter sözleşmesi (checklist)

Sadece **adapter** değişir; çekirdek ve dashboard aynı kalır. **Yeni adapter eklemek** için pakette aşağıdaki minimumlar üretilmelidir.

### Adapter minimum checklist

| Alan / grup | Zorunluluk | Açıklama |
|-------------|------------|----------|
| `external.*` | Zorunlu | `decision`, score (örn. `p_damaging`), `threshold`, `model`, `http_status`, `latency_ms`, `error` |
| `input.*` | Zorunlu | `entity_id` / id, timestamp, actor (user), içerik/evidence referansı |
| `mdm_input_risk` + `state_snapshot` + `mdm_input_state_hash` | Zorunlu | MDM’ye giren risk ve state; mapping doğrulama |
| `source_event_id` | Zorunlu | Dedupe (tekrarlı olay önleme) |
| `final_action`, `clamps` | Zorunlu | Operasyonel gerçek: APPLY / APPLY_CLAMPED / HOLD_REVIEW + clamp listesi |
| `final_action_reason` (= escalation_driver) | Zorunlu | Denetim nedeni (Reason breakdown, kalite) |
| L2: `evidence_status`, diff/thread/sensor_window | L2’de | İnceleme için kanıt; OK / MISSING / ERROR |
| `schema_version`, `adapter_version` | Önerilen | SSOT uyumluluk |

Bu liste ile “yeni kaynak 1 günde” hedefi pratikte sağlanır. Evidence kaynağa göre: Wiki → MediaWiki API diff; sosyal medya → yorum + thread; SCADA → ilgili metrik penceresi.

---

## 7) Kalibrasyon ve “sistem düzgün” kriterleri

**Omurga vs kalibrasyon:** Export/format doğru, run context tutarlı, ORES sağlıklı, mapping doğru (`mdm_input_risk == ores_p_damaging`) → **telemetri/omurga** sağlam demektir. Bu, **MDM’nin davranışının kalibre olduğu** anlamına gelmez.

### “Sistem düzgün çalışıyor” için minimum 2 koşul

Bu CSV/akış “düzgün” sayılabilmek için şunları göstermeli:

1. **L0 da üretiliyor** — En azından bir kısım olay L0 (otomasyon verimliliği).
2. **L1 sadece gerçekten sınırdaki bölgede** — Örn. `p_damaging` orta bant (0.1–0.6); düşük riskte L0, yüksek riskte L2 ara sıra.

**Tüm satırlar L1 ise** (örn. 32/32 L1): “Her şeye fren basılıyor” = **degenerate mod**. Eşikler/profil veya drift warmup (aşağıda) gözden geçirilmeli.

### Degenerate mod / operasyon playbook

Aşağıdaki tablo “neden böyle?” sorusunu dokümana bakarak çözmeyi sağlar.

| Belirti | Muhtemel sebep | Kanıt | Çözüm |
|---------|----------------|-------|--------|
| Her şey L1 | `as_norm_low` her yerde | driver dağılımı %80+ as_norm_low; as_norm histogramı 0’a yakın | AS_SOFT_THRESHOLD ↓ veya as_norm_low’u L1 tetikleyicisinden çıkar |
| Erken L1/L2 (drift) | warmup yok / history yanlış | drift_driver=mean ama history_len küçük | DRIFT_MIN_HISTORY ↑ veya history hesabını düzelt |
| L2 var ama inceleme zor | evidence fetch başarısız | evidence_status ERROR/MISSING | lazy fetch + cache + retry |
| Mismatch çok yüksek | threshold/mapping/policy uyumsuz | mismatch filtresi + risk farkı | mapping kontrol; ORES threshold tuning |

### Beklenen dağılım (Wikipedia/ORES demo, şekil)

| p_damaging bandı | Beklenen ağırlık |
|------------------|------------------|
| Düşük (0.0–0.1)  | Çoğunlukla **L0** |
| Orta (0.1–0.6)   | **L1** yoğun |
| Yüksek (0.6+) / mismatch + drift | **L2** ara sıra |

Bu dağılım yoksa sistem çalışıyor ama **kalibrasyon** oturmamış demektir.

### evidence_status: L2 dışı “NA”

L2 olmayan satırlarda diff çekilmediği için `evidence_status=MISSING` yanlış sinyal verir (diff “eksik” değil, ilgili değil). **Öneri:** L2 dışında `evidence_status` = **NA** (veya boş); sadece L2’de OK/MISSING/ERROR.

### Terimlerin tek anlamı (çekirdek sözleşme)

Karışıklığı önlemek için üç alan net ayrılır:

| Terim | Alan | Kullanım |
|-------|------|----------|
| **Denetim nedeni** | `escalation_driver` | L1/L2’yi **neden** tetikledi (kalibrasyon, Reason breakdown, tuning). “Neden L1/L2?” sorusunun cevabı. |
| **Aksiyon seçimi nedeni** | `selection_reason` | Hangi aksiyonun seçildiği (örn. `max_score`); policy/optimizer debug. |
| **Operasyonel sebep** | `final_action_reason` | Uygulamada gösterilen sebep; **escalation_driver ile aynı** (SSOT). Eski paketlerde `mdm.reason` fallback. |

* **escalation_base** — Hysteresis öncesi base level ve driver.
* CSV: `selection_reason`, `escalation_driver`, `final_action_reason`, `drift_driver`, … Dashboard “Reason breakdown” = **escalation_driver**. Kalite ekranında “hangi driver Red üretiyor” = **escalation_driver** (veya final_action_reason, aynı değer).

### Driver taxonomy (ekosistem sözleşmesi)

Çekirdek driver’lar (sabit; kod + doküman senkron):

| Driver | Anlam |
|--------|--------|
| `none` | Escalation yok (L0) |
| `as_norm_low` | AS_norm < AS_SOFT_THRESHOLD (belirsizlik sinyali) |
| `constraint_violation` | constraint_margin < 0 |
| `confidence_low` | confidence < CONFIDENCE_ESCALATION_FORCE → L2 (veya profil ile L1: CONFIDENCE_LOW_ESCALATION_LEVEL=1) |
| `H_critical` | H > h_crit → L2 |
| `divergence_high` | divergence > DIVERGENCE_HARD_THRESHOLD → L2 |
| `temporal_drift:mean` | cus_mean > CUS_MEAN_THRESHOLD (warmup sonrası) |
| `temporal_drift:delta` | delta_cus > DELTA_CUS_THRESHOLD |
| `temporal_drift:delta+mean` | Her ikisi |
| `temporal_drift:warmup` | History < DRIFT_MIN_HISTORY (preemptive kapalı) |
| `fail_safe` | Fail-safe override (conf yok) |

**Adapter’a özel driver:** Farklı entegrasyonlar kendi namespace’ini kullanabilir: `adapter_driver:*` veya domain adı (örn. `wiki:ores_high`). Böylece aynı dashboard’da farklı sistemler karışmaz; çekirdek listesi genişlemez.

### Dashboard’da 3 kalibrasyon grafiği

1. **Escalation driver dağılımı** — %80+ `as_norm_low` ise L1 kilidi net; AS_SOFT_THRESHOLD veya “as_norm_low’u L1’den çıkar” denemesi.
2. **as_norm histogramı** — as_norm sürekli 0–0.02 bandındaysa threshold 0.3 yanlış; profil ile düşür (örn. 0.1).
3. **drift_driver dağılımı** — warmup bitince `mean`/`delta` tetikleniyor mu; gerçek drift mi CUS çok yüksek mi teşhisi.

### Profil / kalibrasyon stratejisi (tek kural)

* Her adapter için **default profile** + **calibrated profile** (örn. scenario_test + wiki_calibrated).
* Kalibrasyon hedefi: düşük risk bandında L0 çoğunluk; orta risk bandında L1 yoğun; yüksek risk/drift/mismatch’te L2 ara sıra.
* Parametre değiştirme öncelik sırası: (1) AS_SOFT_THRESHOLD, (2) CUS_MEAN_THRESHOLD (drift), (3) DIVERGENCE_HARD_THRESHOLD / CONFIDENCE_ESCALATION_FORCE, (4) adapter-driver’lar.

### Confidence: external (domain’e uygun) vs internal

* **Internal confidence:** Engine, seçilen aksiyonun (W,J,H,C) skorlarından hesaplar; wiki/ORES’te sık sık düşük kalıp “hepsi L2” (confidence_low) üretebilir.
* **External confidence (adapter):** Context’te `external_confidence` verilirse engine escalation’da bunu kullanır. **Distance-to-threshold** formülü: `min(1, abs(p_damaging - threshold) / 0.5)` — ORES 0.5’e yakınsa belirsiz (düşük), 0/1’e yakınsa net (yüksek). Wiki adapter bu değeri set eder; böylece confidence_low kör L2’ye itmez.
* **CONFIDENCE_LOW_ESCALATION_LEVEL:** Profilde 1 ise confidence_low → L1 (L2 backlog patlamasın); varsayılan 2.

**Teşhis:** “Hepsi L2, driver=confidence_low” ise (1) confidence hesaplaması sabit/yanlış mı (ores_p_damaging ile mdm_confidence ilişkisi), (2) threshold/kural mı sert (profil ile L1 veya external_confidence) kontrol et.

**Kalibrasyon için 4 alan (CSV/packet):** `confidence_internal`, `confidence_external`, `confidence_used`, `confidence_source` — hangi confidence kullanıldığı; wiki adapter için `confidence_source=external` çoğunlukta olmalı.

### Koşu başına ayrı JSONL / dashboard filtre

* Canlı koşuda `--jsonl mdm_live.jsonl` verilince dosya **profil adıyla** yazılır: `mdm_live_scenario_test.jsonl`, `mdm_live_wiki_calibrated.jsonl`. Karışık dosyada analiz yanıltmasın.
* Dashboard’da **Config profile** filtresi: karışık yüklemede sadece seçili profil(ler) gösterilir; session/run izole edilir.

### Wiki kalibrasyon profili (L0 denemesi)

Profil **wiki_calibrated**: `AS_SOFT_THRESHOLD=0.1`, `CONFIDENCE_LOW_ESCALATION_LEVEL=1`. Adapter `external_confidence` (distance-to-threshold) set ettiği için confidence artık ORES’e uyumlu. Canlı koşuda `MDM_CONFIG_PROFILE=wiki_calibrated` ile L0/L1 dağılımı denemesi.

### Drift / preemptive warmup (uygulandı)

**DRIFT_MIN_HISTORY** (config, varsayılan 30): CUS history bu uzunluğa ulaşmadan `should_preemptively_escalate` **False** döner; preemptive L1 tetiklenmez. `temporal_drift.driver` = `warmup` warmup süresince; sonrasında `mean` | `delta` | `delta+mean` | `none`. CSV’de `drift_driver`, `drift_history_len`, `drift_min_history` ile tek bakışta görülür.

**Drift history persist:** Canlı döngüde (run_live_loop / main) `cus_history` koşu boyunca saklanır ve her event’te context’e enjekte edilir; böylece `drift_history_len` 1’de kalmaz, 2, 3, … diye artar ve warmup sonrası drift tetikleyicileri devreye girebilir.

---

**Özet:** Omurga ve export doğru ✅. “Bu dosya tek başına sistem düzgün çalışıyor için yeterli” → **Hayır** ❌; L0/L1/L2 dağılımı + escalation nedeni + warmup ile **kalibrasyon** ayrıca doğrulanmalı.
