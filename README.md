# Зубков С.А. — Резюме и мастер-профиль

Приватный репозиторий. Содержит мастер-профиль и актуальные версии резюме.

## Структура

| Файл | Описание |
|------|----------|
| `master_profile_ru.md` | Мастер-профиль — источник истины для всех версий резюме |
| `Zubkov_SA_Resume_IT-Director.html` | Резюме IT-директор / CTO / Chief AI Officer (HTML) |
| `Zubkov_SA_Resume_IT-Director.pdf` | Резюме IT-директор / CTO / Chief AI Officer (PDF, A4) |
| `generate_resume_pdf.py` | Скрипт генерации PDF (ReportLab + Inter) |
| `foto_zsa.jpg` | Фото профиля |

## Генерация PDF

```bash
# Требуется: Python 3.10+, reportlab, шрифты Inter в /tmp/fonts/
pip install reportlab
python generate_resume_pdf.py
```

## Версии

Актуальная версия: **v1.5** (2026-04-23)

История изменений — см. [CHANGELOG.md](CHANGELOG.md).
