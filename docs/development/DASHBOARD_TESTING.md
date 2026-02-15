# Dashboard Testleri ve Proof Mode

## Paket kurulumu (PyPI) vs geliştirme

- **Paket kurulumunda:** Dashboard yalnızca `mdm_engine` public API kullanır; repo-root (`core/`, `simulation/`) import yok.
- **Geliştirme:** `MDM_ENGINE_DEV=1` ortam değişkeni verildiğinde repo-root fallback açılır (örn. `core.trace_collector`, `simulation.scenario_generator`).
- CI ve yerel testlerde `MDM_ENGINE_DEV=1` ile veya `pip install -e ".[dev]"` ile çalıştırın.

## Mimari

- **dashboard.py**: Tek Streamlit dashboard (UI + servisler). `sys.path` repo root ekler; motor/trace erişimi servisler üzerinden.
- **visualization/services**: EngineService, ScenarioService, TraceService. Testte Fake ile değiştirilebilir.
- **visualization/domain**: Pure hesaplar (metrics, proof pack). Birim testleri kolay.
- **visualization/components**: Kart ve grafik bileşenleri (sadece render).

## Proof Mode vs Production Mode

| Mod | Amaç | Config | L0/L1/L2 |
|-----|------|--------|----------|
| **Proof** | Sunum/demo: L0, L1, L2 hepsini göstermek | scenario_test | Run until coverage ile hedefe kadar koşar |
| **Production** | Kurumsal gerçekçilik | production_safe | L2 ağırlıklı olabilir; "L0 yok" hata değil, policy choice |

Proof Mode'da **"Run until L0/L1/L2 coverage"** butonu: L0, L1 ve L2 hepsinde en az 1 örnek görene kadar (veya max adım) state üretir ve engine koşturur. Böylece "L0 hiç görünmüyor" itirazı giderilir: "Bak, L0 mümkün; production profili bilerek sıkı."

## Proof Pack: Offline vs Online

- **Offline (traces üzerinden, engine yok):** Clamp, Escalation Coverage, Rate+Health (p95/p99, schema tip/aralık), Export Contract. Her run sonrası otomatik.
- **Online (engine gerekir):** Determinism (aynı seed 2 run karşılaştır), Replay (1 state decide + replay_trace). Dashboard’da **"Run Online Proof"** butonu ile tetiklenir. CI’da domain testleri her zaman; app smoke ve online proof opsiyonel (ubuntu+py3.10).

## Testler (tests_dashboard/)

- **test_app_smoke.py**: Streamlit `AppTest` ile app yüklenir (sidebar). CI’da **sadece ubuntu-latest + py3.10** (Streamlit/OS hassasiyeti).
- **test_proof_pack.py**: Domain metrics ve offline/online proof (FakeEngine / FakeTraceSvc ile). Tüm matrix’te koşar.
- **test_export_contract.py**: CSV tek kaynak (tools.csv_export); TraceService `traces_to_csv_string` oradan kullanır; header + satır sayısı.

Çalıştırma (repo root):

```bash
export MDM_ENGINE_DEV=1   # veya set MDM_ENGINE_DEV=1 (Windows)
pip install -e ".[dev,dashboard]"
pytest tests_dashboard/ -v
```

## Çalıştırma

```bash
mdm dashboard
# veya
streamlit run visualization/dashboard.py
```
