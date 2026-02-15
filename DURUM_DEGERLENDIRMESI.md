# MDM (Model Oversight Engine) — Mevcut Durum Değerlendirmesi

**Tarih:** 15 Şubat 2026  
**Versiyon:** 1.0.0 (pyproject.toml)

---

## 1. Kısa Özet

Proje **etik karar motoru** (L0/L1/L2 escalation, soft clamp, audit) olarak tanımlı; paket yapısı ve public API yerinde. **Test altyapısında büyük bir sadeleştirme yapılmış**: eski kapsamlı test suite kaldırılmış, yerine az sayıda odaklı test ve “canlı deneme = dashboard” yaklaşımı benimsenmiş. CI smoke testler ve build çalışıyor; yerel `run_tests.bat` ise **silinmiş** `run_all_tests.py` dosyasına bağlı olduğu için **kırık**.

---

## 2. Proje Kimliği

| Alan | Değer |
|------|--------|
| **Amaç** | Etik AI karar desteği: deterministik, denetlenebilir, L0/L1/L2 escalation |
| **Public API** | `decide()`, `replay_trace()` |
| **CLI** | `mdm dashboard`, `realtime`, `tests`, `demo` |
| **Python** | 3.8–3.12 |
| **Lisans** | Apache-2.0 |

---

## 3. Test Durumu (Kritik)

### 3.1 Ne Değişti?

- **Eski yapı (silindi):**
  - `run_all_tests.py` — merkezi test runner (**D**)
  - `tests/` altında birçok modül: adversarial, chaos, learning, monte_carlo, simulation, soft_clamp, soft_override, temporal_drift, trace_collector, uncertainty vb. (**D**)
  - PROJECT_REPORT.md’deki “16/16 test geçti” bu eski yapıya aitti.

- **Şu anki yapı:**
  - **pyproject.toml:** `testpaths = []` → pytest varsayılan olarak hiçbir test klasörü taramıyor.
  - **CLI `mdm tests`:** “Test suite kaldırıldı. Canlı deneme için: mdm dashboard” mesajı verip çıkıyor (fail etmiyor).
  - **Kalan test dosyaları (4 adet, repo’da untracked):**
    - `tests/test_invariants.py` — karar invariants (fail_safe, L0/L1/L2, clamp kuralları)
    - `tests/test_export_invariants.py`
    - `tests/test_live_audit_flow.py`
    - `tests/test_uncertainty_as_norm_none.py`

### 3.2 Yerel Test Çalıştırma

- **run_tests.bat:** `run_all_tests.py` çağırıyor → bu dosya artık yok → **batch dosyası kırık**.
- Bu 4 testi elle çalıştırmak için örnek:
  - `python -m pytest tests/ -v` (proje root’ta; `testpaths` boş olduğu için `tests/` klasörünü açık vermek gerekir).

### 3.3 CI’daki Testler

- **.github/workflows/ci.yml:**
  - Lint (ruff, black)
  - Basit API testi: `decide(...)` import ve çağrı
  - `tools/realtime_ci.py` ile trace üretimi (yalnızca ubuntu + py3.10)
  - Build + twine check + wheel kurulum testi
- **.github/workflows/nightly.yml:** Sadece API smoke; “test yapısı kaldırıldı” notu var.

**Sonuç:** CI, silinen test suite’e bağımlı değil; smoke ve build **çalışıyor**. Ancak proje içi “bir komutla tüm testler” deneyimi yerelde **yok** ve dokümantasyon (CONTRIBUTING, REPOSITORY_STRUCTURE, RUN_TESTS.md vb.) hâlâ `run_all_tests.py` üzerinden test çalıştırmayı anlatıyor.

---

## 4. Kod ve Dokümantasyon Tutarlılığı

- **Değiştirilmiş (M) dosyalar:**  
  `mdm_engine/` (cli, config, engine), `core/` (action_generator, action_selector, soft_override, state_encoder, temporal_drift, uncertainty), `config_profiles/`, `visualization/`, `tools/csv_export.py`, `tools/run_offline_learning.py`, CI, README, .gitignore vb.  
  → Aktif geliştirme; motor ve dashboard tarafında güncellemeler var.

- **Yeni (??) öğeler:**  
  `mdm_engine/audit_spec.py`, `invariants.py`, `operasyon_metrics.py`, `config_profiles/wiki_calibrated.py`, `visualization/components/`, `domain/`, `services/`, `docs/` altında yeni/plan dokümanları, birkaç jsonl/csv test çıktısı.

- **Dokümantasyon gecikmeleri:**
  - **PROJECT_REPORT.md:** “16/16 test”, “run_all_tests”, eski test kategorileri — **güncel değil**.
  - **TEST_STRATEGY.md:** Yeni strateji (6 çekirdek test, kapsam, nightly) tanımlı; `run_core_tests.py` / `run_all_tests.py` referansları var — bu script’ler repo’da **yok**.
  - **CONTRIBUTING.md, REPOSITORY_STRUCTURE.md, RUN_TESTS.md:** Hâlâ `run_all_tests.py` kullanımını söylüyor.

---

## 5. Güçlü Yönler

- Public API (`decide`, `replay_trace`) ve paket yapısı net.
- CI (lint + API smoke + trace üretimi + build) çalışıyor.
- Dashboard ve canlı deneme (realtime, demo) yolu açık; “test yerine dashboard” kararı net.
- Yeni invariants ve audit odaklı testler (4 dosya) mevcut; commit edilip pytest’e bağlanabilir.
- Dokümantasyon hacmi yüksek (spec’ler, development, raporlar); sadece test/runner kısımları güncellenmeli.

---

## 6. Riskler ve Eksikler

| Risk / Eksik | Önem | Not |
|--------------|------|-----|
| **run_tests.bat kırık** | Yüksek | `run_all_tests.py` silindi; yerel “tek tıkla test” yok. |
| **pytest testpaths=[]** | Orta | Varsayılan pytest çalıştırmada `tests/` bulunmuyor; path vermek veya testpaths’i doldurmak gerekir. |
| **Dokümantasyon eski** | Orta | PROJECT_REPORT, CONTRIBUTING, RUN_TESTS vb. run_all_tests / 16 test anlatıyor. |
| **TEST_STRATEGY ile uyumsuzluk** | Orta | run_core_tests / run_all_tests planlı ama repo’da yok. |
| **4 test dosyası untracked** | Orta | Commit edilmezse kaybolabilir; CI’a eklenmemiş. |

---

## 7. Önerilen Aksiyonlar (Öncelik Sırasıyla)

1. **run_tests.bat’ı güncelle**  
   - `run_all_tests.py` yerine mevcut testleri çalıştıracak komut koy (örn. `python -m pytest tests/ -v`).  
   - Böylece yerel “tek komutla test” tekrar çalışır.

2. **pytest’i tests/ ile eşle**  
   - `pyproject.toml` içinde `testpaths = ["tests"]` yap veya CI’da `pytest tests/` çağır.  
   - 4 test dosyasının otomatik keşfedilmesi sağlanır.

3. **4 test dosyasını commit et ve CI’a ekle**  
   - `tests/test_invariants.py`, `test_export_invariants.py`, `test_live_audit_flow.py`, `test_uncertainty_as_norm_none.py`  
   - CI job’ında (örn. `test` adımında) `pytest tests/ -v` eklenebilir.

4. **Dokümantasyonu senkronize et**  
   - PROJECT_REPORT.md: Mevcut test setini (4 dosya + CI smoke) ve “dashboard ile canlı deneme”yi yansıt.  
   - CONTRIBUTING.md, REPOSITORY_STRUCTURE.md, RUN_TESTS.md: `run_all_tests.py` yerine `pytest tests/` veya güncel run_tests.bat kullanımını yaz.  
   - TEST_STRATEGY.md: run_core_tests/run_all_tests’i “planlanan” olarak işaretle veya mevcut runner’a (pytest + batch) göre güncelle.

5. **İsteğe bağlı:** TEST_STRATEGY’deki 6 çekirdek test ve nightly planına göre ileride `run_core_tests.py` veya minimal bir runner eklenebilir; şu an için mevcut 4 test + CI smoke tutarlılık için yeterli.

---

## 8. Sonuç Cümlesi

**Durum:** Proje işlevsel ve CI/build yeşil; ancak test altyapısı bilinçli olarak sadeleştirilmiş, dokümantasyon ve yerel test runner bu değişimi henüz yansıtmıyor. Yerel test komutu (`run_tests.bat`) kırık, 4 yeni test dosyası repo’da izlenmiyor ve CI’da koşmuyor. Bu adımlar tamamlandığında “mevcut durum” ile dokümantasyon ve araçlar uyumlu hale gelir.

---

*Bu dosya proje kökünde durum özeti olarak tutulabilir; tarih ve versiyon ilerledikçe güncellenebilir.*
