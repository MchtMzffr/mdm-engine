# Canlı veri ve gerçek yaşam pilotu

## Üç canlı senaryo türü

| Script | Amaç | Çıktı |
|--------|------|--------|
| **tools/realtime_smoke.py** | Rastgele state, sürekli akış; motor + latency doğrulama | traces_live.jsonl |
| **tools/realtime_pilot.py** | Fazlı hikaye: rutin → stres → toparlanma | traces_live.jsonl |
| **tools/realtime_demos.py** | **3 demo (insan anlatımı):** Rutin Hayat → Gri Alan → Kriz | traces_live.jsonl |

### realtime_demos.py — Aynı model, üç davranış

- **A) Rutin Hayat** — state: `easy` (J yüksek, H düşük, risk düşük), config: `scenario_test`, 70 adım.  
  Beklenen: L0 ağırlıklı, CUS daha düşük, soft clamp az. *“Sistem normalde karar veriyor.”*

- **B) Gri Alan** — state: `medium` (J/H orta), config: `scenario_test`, 70 adım.  
  Beklenen: L1 belirgin, soft clamp görünür, action drift bariz. *“Emin değilken yumuşatıyor.”*

- **C) Kriz** — state: `chaos`, config: `production_safe`, 70 adım.  
  Beklenen: L2 ağırlıklı, human escalation. *“Riskliyse duruyor.”*

Her trace’e `phase` alanı yazılır (`rutin` | `gri` | `kriz`); ileride filtre için kullanılabilir.

## Pilot akışı (realtime_pilot.py)

1. **Rutin (dengeli gün)** — state: `balanced`, config: `scenario_test`, 50 adım  
   L0/L1/L2 karışık; “normal gün” hissi.

2. **Stres (dikkat / sıkı kurallar)** — state: `safe`, config: `production_safe`, 40 adım  
   Daha temkinli; L2 ağırlığı artar.

3. **Toparlanma (dengeli)** — state: `balanced`, config: `scenario_test`, 50 adım  
   Tekrar karışık seviyeler; “olay sonrası normale dönüş”.

Toplam ~140 kayıt; dashboard’da CUS timeline, action drift ve latency bu hikâyeyi adım adım gösterir.

## Nasıl izlenir?

1. **Terminal 1:**  
   `python tools/realtime_pilot.py`  
   (İstersen: `python tools/realtime_pilot.py` — varsayılan `traces_live.jsonl`)

2. **Terminal 2:**  
   `streamlit run visualization/dashboard.py`

3. **Dashboard:**  
   - Veri kaynağı = **JSONL dosya**  
   - Dosya = **traces_live.jsonl**  
   - **Otomatik yenile (30 s)** = açık  

Rutin → stres → toparlanma geçişleri grafiklerde (özellikle CUS, L0/L1/L2 dağılımı, action drift) izlenebilir.
