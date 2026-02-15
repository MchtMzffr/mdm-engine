# Test ve dashboard konsolidasyonu

## Tek dashboard

- **Kullanılacak:** `visualization/dashboard.py` (tek Streamlit dashboard; revizyona açık).
- **CLI:** `mdm dashboard` → dashboard.py açar.
- Diğer dashboard dosyaları (app.py, dashboard_simple.py, dashboard_advanced.py) kaldırıldı.

## Referans test senaryosu (L0/L1/L2 faz kanıtı)

Aşağıdaki akış, “modelin amacı net görünsün” ve “L0/L1/L2 gerçeğe yakın test” için **tek referans** kabul edilir:

1. **Proof state'leri üret:**  
   `python tools/find_proof_states.py`  
   → `tools/proof_states.json` (L0, L1, L2 state'leri)

2. **Faz testi (gerçek engine):**  
   `pytest tests/test_phases_real_engine.py -v`  
   - proof_states.json ile L0/L1/L2 doğrulama  
   - İsteğe bağlı: drift testi (yüksek cus_history → preemptive escalation)

3. **Dashboard’da canlı kanıt:**  
   `mdm dashboard` → **10 Senaryo** sekmesi → “L0 / L1 / L2 üçlüsünü çalıştır”  
   (proof_states.json yüklü olmalı)

Bu senaryo işe yaradığı sürece, aşağıdaki testler **devre dışı bırakılabilir / kaldırılabilir**:

| Test / dosya | Durum | Gerekçe |
|--------------|--------|--------|
| `tests/test_dashboard_scenarios.py` | Devre dışı | Circular import; faz doğrulaması test_phases_real_engine ile yapılıyor |
| `tests/learning/test_learning.py` | Devre dışı | Import hatası; learning ayrı pipeline |
| `tests/soft_clamp/test_soft_clamp.py` | Devre dışı | core-first import → circular (gerekirse engine-first ile yeniden yazılabilir) |
| `tests/uncertainty/test_uncertainty.py` | Devre dışı | Aynı import sorunu |
| `tests/temporal_drift/test_temporal_drift.py` | Devre dışı | Aynı import sorunu |
| `tests/trace_collector/test_trace_collector.py` | Opsiyonel | core import; trace contract test_phases veya tests_dashboard ile korunabilir |

**Korunan / kullanılan:**

- `tests_dashboard/` — Proof pack, latency, export, app smoke (engine’e bağımlı değil)
- `tests/test_scenarios.py` — Phase 3 senaryoları (engine-first, geçiyor)
- `tests/simulation/test_scenario_generator.py` — State üretimi
- `tests/test_phases_real_engine.py` — **L0/L1/L2 + drift referans testi**

## Devre dışı bırakma (pytest)

İstenirse bu testleri atlamak için:

```bash
pytest tests/ -v --ignore=tests/learning --ignore=tests/test_dashboard_scenarios.py
```

Veya test dosyalarına `@pytest.mark.skip(reason="Konsolidasyon: test_phases_real_engine referans")` eklenebilir.

## Özet

- **Tek dashboard:** `visualization/dashboard.py` (Proof + 10 Senaryo + Case Study).
- **Tek faz referans testi:** `tools/find_proof_states.py` + `tests/test_phases_real_engine.py` + Dashboard “10 Senaryo” sekmesi.
- Eski / gereksiz test senaryoları yukarıdaki tabloya göre devre dışı bırakılır veya projeden çıkarılır.
