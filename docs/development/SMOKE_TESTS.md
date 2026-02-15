# Smoke tests (yayınlamadan önce)

Aşağıdaki 3 test, dağıtım öncesi “kırmadan geçiş” ve paketlemenin doğru olduğunu doğrular.

---

## 1. Editable install + CLI

```bash
cd /path/to/mdm-engine
pip install -e .
mdm --help
```

**Beklenen:** `mdm` CLI yardımı görünür (dashboard, realtime, tests, demo).

**Ek:** `python -c "import mdm_engine; import mdm_engine.config_profiles; print('OK')"` → `OK` (config_profiles wheel içinde geliyor).

---

## 2. Wheel’den kurulum (temiz ortam)

```bash
pip install build twine
python -m build
# Yeni bir venv’de veya --ignore-installed ile:
pip install dist/*.whl
python -c "from mdm_engine import decide; print(decide({'risk':0.5,'severity':0.6,'physical':0.5,'social':0.5,'context':0.4,'compassion':0.5,'justice':0.9,'harm_sens':0.5,'responsibility':0.7,'empathy':0.6}, profile='scenario_test')['escalation'])"
```

**Beklenen:** Kurulum hatasız; `decide()` çağrısı bir escalation değeri (0/1/2) döner.

---

## 3. Dashboard extras

```bash
pip install "mdm-engine[dashboard]"
mdm dashboard
```

**Beklenen:** Streamlit dashboard başlar (tarayıcıda açılır). Çıkmak için Ctrl+C.

---

## Backward compatibility

- **Compat kaldırıldı:** Eski paket/CLI yok. Sadece `mdm_engine` ve `mdm` kullanın.
- **Doğrulama:** `python -c "from mdm_engine import decide; print(decide({'risk':0.5}, profile='scenario_test')['escalation'])"` → 0/1/2.

- **CLI:** `mdm --help`, `mdm dashboard`.

---

*Son güncelleme: 2026-02-15*
