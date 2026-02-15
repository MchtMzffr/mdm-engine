# GitHub Repoyu Silip Yeni / Temiz Yükleme

Bu dosya, repoyu GitHub’ta silip **sıfırdan temiz** yüklemen veya **mevcut repoyu temiz commit ile güncellemen** için adımları listeler.

---

## Seçenek 1: Mevcut repoyu temiz tutup sadece push (en basit)

Tüm değişiklikler zaten MDM-only; history’de eski AMI commit’leri kalır ama **şu anki dal tam temiz**.

1. Lokal temizlik (isteğe bağlı):
   ```bash
   # Gereksiz dosyaları temizle (zaten .gitignore’da olanlar takip edilmiyor)
   git status
   git add -A
   git commit -m "MDM-only: schema v2, no AMI trace, CI gate"
   ```

2. GitHub’a gönder:
   ```bash
   git push origin main
   ```
   Gerekirse `git push origin main --force` (sadece dalı yeniden yazdıysan).

---

## Seçenek 2: GitHub’ta repoyu silip sıfırdan yeni repo + ilk push

**“Tarihçe istemiyorum, tek temiz commit ile başlasın”** diyorsan:

### Adım 1: GitHub’ta mevcut repoyu sil

1. GitHub’ta repoya git: `https://github.com/<org>/<repo>`
2. **Settings** → en alta in → **Danger Zone** → **Delete this repository**
3. Repo adını yazıp sil (gerekirse org sahibi yetkisi gerekir).

### Adım 2: Yeni repo oluştur

1. GitHub’ta **New repository**
2. Aynı isimle (veya yeni isimle) oluştur; **README / .gitignore / license ekleme** (lokal zaten var).

### Adım 3: Lokal’de .git’i koruyup remote’u yeni repoya bağla

Lokal proje klasöründe:

```bash
cd c:\Users\tsgal\Desktop\ami-engine

# Mevcut remote’u kontrol et
git remote -v

# Eski remote’u kaldır (genelde origin)
git remote remove origin

# Yeni boş repoyu ekle (URL’i kendi reponla değiştir)
git remote add origin https://github.com/<org>/<repo>.git
# veya SSH:
# git remote add origin git@github.com:<org>/<repo>.git
```

### Adım 4: (İsteğe bağlı) Tek temiz commit ile başlamak — history’yi at

Tüm geçmişi silip **şu anki dosyaları tek commit** yapmak istersen:

```bash
# Yeni yetim dal: mevcut dosyalar, commit geçmişi yok
git checkout --orphan clean-main

# Hepsinı stage’le
git add -A

# İlk ve tek commit
git commit -m "Initial commit: MDM (Model Oversight Engine) — schema v2, no AMI trace"

# Eski main’i sil, bu dalı main yap
git branch -D main
git branch -m main

# Yeni repoya push (repo boş olmalı)
git push -u origin main
```

**Dikkat:** Bu işlem lokal’deki tüm eski commit’leri siler; geri almak zor.

### Adım 4 alternatif: History’yi koru, sadece yeni repoya push et

History’yi silmek istemiyorsan:

```bash
git push -u origin main
```

---

## Seçenek 3: Lokal’de tamamen sıfırdan .git (en radikal)

Proje klasöründe **.git hariç her şey** kalsın, repo sıfırdan başlasın:

```bash
cd c:\Users\tsgal\Desktop\ami-engine

# .git’i sil (tüm lokal history gider)
Remove-Item -Recurse -Force .git   # PowerShell
# veya: rmdir /s /q .git            # CMD

# Yeni repo
git init
git add -A
git commit -m "Initial commit: MDM (Model Oversight Engine) — schema v2, no AMI trace"

# GitHub’da yeni boş repo oluşturduktan sonra:
git remote add origin https://github.com/<org>/<repo>.git
git branch -M main
git push -u origin main
```

---

## Özet

| Hedef | Yöntem |
|--------|--------|
| Sadece son hali gönder, history kalsın | Seçenek 1 |
| GitHub’ta repo silinsin, yeni repo + tek temiz commit | Seçenek 2 + Adım 4 (orphan) |
| GitHub’ta repo silinsin, history aynen gitsin | Seçenek 2 + Adım 4 alternatif |
| Lokal’de de sıfır, tek commit | Seçenek 3 |

GitHub’ta silme ve yeni repo oluşturma **sadece senin hesabında** yapılır; bu adımlar lokal komutlar ve senin GitHub üzerinde yapacakların için rehberdir.
