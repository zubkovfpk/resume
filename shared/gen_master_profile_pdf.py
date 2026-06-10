#!/usr/bin/env python3
"""Мастер-профиль Зубкова С.А. — генерация PDF."""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable

# ─── Шрифты ───────────────────────────────────────────────────────────────────
FONTS_DIR = "/home/user/workspace/fonts_vk"
OUT_PATH  = "/home/user/workspace/Zubkov_MasterProfile_v17.pdf"

for name, fname in {
    "Inter":          "Inter-Regular.ttf",
    "Inter-Bold":     "Inter-Bold.ttf",
    "Inter-SemiBold": "Inter-SemiBold.ttf",
}.items():
    fp = os.path.join(FONTS_DIR, fname)
    if os.path.exists(fp):
        pdfmetrics.registerFont(TTFont(name, fp))

# ─── Палитра ──────────────────────────────────────────────────────────────────
NAVY      = colors.HexColor("#0C2D48")
TEAL      = colors.HexColor("#01696F")
TEAL_DARK = colors.HexColor("#0C4E54")
AMBER     = colors.HexColor("#964219")
AMBER_BG  = colors.HexColor("#FFF8EC")
AMBER_BAR = colors.HexColor("#C87922")
GREEN_BG  = colors.HexColor("#EBF5F5")
MUTED_BG  = colors.HexColor("#F0EEE9")
BORDER    = colors.HexColor("#D4D1CA")
BG        = colors.HexColor("#F7F6F2")
TEXT      = colors.HexColor("#28251D")
MUTED     = colors.HexColor("#7A7974")
WHITE     = colors.white
RED_SOFT  = colors.HexColor("#8B0000")
RED_BG    = colors.HexColor("#FFF0F0")

W, H = A4
MARGIN_L = 16 * mm
MARGIN_R = 14 * mm
MARGIN_T = 14 * mm
MARGIN_B = 14 * mm
CONTENT_W = W - MARGIN_L - MARGIN_R

# ─── Стили ────────────────────────────────────────────────────────────────────
def S(name, **kw):
    return ParagraphStyle(name, **kw)

BODY    = S("body",    fontName="Inter",          fontSize=8.5,  textColor=TEXT,  leading=12.5, spaceAfter=2)
BODY_B  = S("body_b",  fontName="Inter-Bold",     fontSize=8.5,  textColor=TEXT,  leading=12.5, spaceAfter=2)
SMALL   = S("small",   fontName="Inter",          fontSize=7.5,  textColor=TEXT,  leading=11,   spaceAfter=1)
SMALL_B = S("small_b", fontName="Inter-SemiBold", fontSize=7.5,  textColor=TEAL_DARK, leading=11, spaceAfter=1)
NOTE    = S("note",    fontName="Inter",          fontSize=7.5,  textColor=MUTED, leading=11,   spaceAfter=2, leftIndent=8)

# Заголовок документа
H1 = S("h1", fontName="Inter-Bold", fontSize=15, textColor=WHITE, leading=19, spaceAfter=0)
H1_SUB = S("h1sub", fontName="Inter", fontSize=8, textColor=colors.HexColor("#A0C4C8"), leading=11, spaceAfter=0)

# Секционные заголовки (цветная полоса)
H2 = S("h2", fontName="Inter-Bold", fontSize=9.5, textColor=WHITE, leading=12, spaceAfter=0)
# Подзаголовок внутри секции
H3 = S("h3", fontName="Inter-SemiBold", fontSize=8.5, textColor=TEAL_DARK, leading=12, spaceBefore=6, spaceAfter=2)
H3_NAVY = S("h3navy", fontName="Inter-SemiBold", fontSize=8.5, textColor=NAVY, leading=12, spaceBefore=5, spaceAfter=2)

TAG = S("tag", fontName="Inter-SemiBold", fontSize=7, textColor=TEAL_DARK, leading=10, spaceAfter=1)

LEAD_L = S("lead_l", fontName="Inter-Bold",     fontSize=7.5, textColor=TEAL_DARK, leading=10, spaceAfter=0)
LEAD_G = S("lead_g", fontName="Inter-SemiBold", fontSize=7.5, textColor=colors.HexColor("#5A3E00"), leading=10, spaceAfter=0)

# ─── Вспомогательные ──────────────────────────────────────────────────────────
def sp(n=1): return Spacer(1, n * 3)
def rule(col=BORDER, thick=0.5): return HRFlowable(width="100%", thickness=thick, color=col, spaceAfter=3, spaceBefore=3)

def sec_header(title, color=NAVY):
    tbl = Table([[Paragraph(title, H2)]], colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), color),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    return tbl

def subsec_header(title, color=TEAL):
    tbl = Table([[Paragraph(title, H2)]], colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), color),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    return tbl

def kv_table(rows, col1=90, gap=6):
    """Двухколоночная таблица ключ-значение."""
    col2 = CONTENT_W - col1
    data = [[Paragraph(f"<b>{k}</b>", SMALL_B), Paragraph(v, BODY)] for k,v in rows]
    tbl = Table(data, colWidths=[col1, col2])
    tbl.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("LEFTPADDING",   (1,0), (1,-1),  gap),
        ("LINEBELOW",     (0,0), (-1,-2), 0.3, BORDER),
    ]))
    return tbl

def bullet_list(items, indent=8):
    """Список с буллетами."""
    result = []
    for item in items:
        p = Paragraph(f"• {item}", ParagraphStyle("bl", fontName="Inter",
            fontSize=8.5, textColor=TEXT, leading=12.5, spaceAfter=2,
            leftIndent=indent, firstLineIndent=-6))
        result.append(p)
    return result

def level_badge(level_text, bg, text_col):
    """Бейджик уровня [arch/lead] или [familiar/growing]."""
    style = ParagraphStyle("badge", fontName="Inter-SemiBold", fontSize=7,
        textColor=text_col, leading=10)
    tbl = Table([[Paragraph(level_text, style)]], colWidths=[None])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), bg),
        ("TOPPADDING",    (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
        ("RIGHTPADDING",  (0,0), (-1,-1), 5),
        ("ROUNDEDCORNERS",(0,0), (-1,-1), [2,2,2,2]),
    ]))
    return tbl

def skill_box(title, items, bg, bar_col, label=""):
    """Блок с заголовком, плашкой уровня и буллетами."""
    content = []
    if label:
        badge_style = ParagraphStyle("lbl", fontName="Inter-SemiBold",
            fontSize=7, textColor=WHITE, leading=10)
        badge_tbl = Table([[Paragraph(label, badge_style)]],
                          colWidths=[None])
        badge_bg = bar_col
        badge_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), badge_bg),
            ("TOPPADDING",    (0,0), (-1,-1), 2),
            ("BOTTOMPADDING", (0,0), (-1,-1), 2),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
            ("RIGHTPADDING",  (0,0), (-1,-1), 6),
        ]))
        content.append(badge_tbl)
        content.append(sp(1))
    if title:
        content.append(Paragraph(f"<b>{title}</b>", H3_NAVY))
    for item in items:
        content.append(Paragraph(f"• {item}", ParagraphStyle("sbl",
            fontName="Inter", fontSize=8, textColor=TEXT, leading=12,
            spaceAfter=2, leftIndent=8, firstLineIndent=-6)))

    tbl = Table([[content]], colWidths=[CONTENT_W - 16])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), bg),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LINEAFTER",     (0,0), (0,-1),  3, bar_col),
    ]))
    return tbl

def exp_block(period, title, org, tags, bullets):
    """Блок опыта работы."""
    content = []
    header = Table([[
        Paragraph(f"<b>{title}</b>", ParagraphStyle("eht", fontName="Inter-Bold",
            fontSize=9, textColor=NAVY, leading=12)),
        Paragraph(period, ParagraphStyle("per", fontName="Inter-SemiBold",
            fontSize=8, textColor=MUTED, leading=12, alignment=TA_RIGHT)),
    ]], colWidths=[CONTENT_W * 0.72, CONTENT_W * 0.28])
    header.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    content.append(header)
    content.append(Paragraph(org, ParagraphStyle("org", fontName="Inter-SemiBold",
        fontSize=8, textColor=TEAL, leading=11, spaceAfter=3)))
    if tags:
        content.append(Paragraph(f"Теги: <i>{tags}</i>", TAG))
        content.append(sp(0.5))
    for b in bullets:
        content.append(Paragraph(f"• {b}", ParagraphStyle("ebl",
            fontName="Inter", fontSize=8.5, textColor=TEXT, leading=12.5,
            spaceAfter=2, leftIndent=8, firstLineIndent=-6)))
    return content


# ─── ГЕНЕРАЦИЯ ────────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUT_PATH, pagesize=A4,
        leftMargin=MARGIN_L, rightMargin=MARGIN_R,
        topMargin=MARGIN_T, bottomMargin=MARGIN_B,
        title="Мастер-профиль Зубков С.А. v1.7.6",
        author="Perplexity Computer",
    )
    story = []

    # ══════════════════════════════════════════════════════════════════════
    # ШАПКА
    # ══════════════════════════════════════════════════════════════════════
    header_tbl = Table([[
        Paragraph("Зубков Сергей Андреевич", H1),
        Paragraph("Мастер-профиль v1.7.6 · 27.05.2026", H1_SUB),
    ]], colWidths=[CONTENT_W * 0.65, CONTENT_W * 0.35])
    header_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), NAVY),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (0,0),   10),
        ("RIGHTPADDING",  (1,0), (1,0),   10),
        ("ALIGN",         (1,0), (1,0),   "RIGHT"),
    ]))
    story.append(header_tbl)

    # Контакты в одну строку
    # Строка контактов: 4 ячейки, размер под каждую группу, неразрывные пробелы ( )
    # Контакты: 4 ячейки;   = неразрывный пробел;
    # в ссылке linkedin заменяем '-' на &#8209; (неразрывный дефис) чтоб не резался
    SMALL_W = ParagraphStyle("small_w", fontName="Inter", fontSize=7,
        textColor=colors.white, leading=10.5, spaceAfter=0,
        wordWrap=None, splitLongWords=0)
    # 4 ячейки с точными pt-ширинами: phone | emails | TG+LI | city+reloc
    # Сумма = 510pt ≈ CONTENT_W (A4, отступы 16mm+14mm)
    # TG+LI в 2 строки: «@SergeyAZubkov ·» / «linkedin.com/in/...»
    SMALL_W2 = ParagraphStyle("small_w2", fontName="Inter", fontSize=7,
        textColor=colors.white, leading=10.5, spaceAfter=0)
    contacts = Table([[
        Paragraph("+7\u00a0(926)\u00a0276\u201161\u201143", SMALL_W),
        Paragraph("zubkovfpk@yandex.ru<br/>zubkovfpk@gmail.com", SMALL_W2),
        Paragraph("@SergeyAZubkov\u00a0·<br/>linkedin.com/in/sergey&#8209;a&#8209;zubkov", SMALL_W2),
        Paragraph("Москва\u00a0·\u00a0релок.\u00a0сен.\u00a02027", SMALL_W),
    ]], colWidths=[74, 172, 164, 100])
    contacts.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), TEAL),
        ("TEXTCOLOR",     (0,0), (-1,-1), colors.white),
        ("FONTNAME",      (0,0), (-1,-1), "Inter"),
        ("FONTSIZE",      (0,0), (-1,-1), 7),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ]))
    story.append(contacts)
    story.append(sp(2))

    # ══════════════════════════════════════════════════════════════════════
    # РАЗДЕЛ 1: ВАРИАНТЫ ПОЗИЦИОНИРОВАНИЯ
    # ══════════════════════════════════════════════════════════════════════
    story.append(sec_header("1. Варианты позиционирования"))
    story.append(sp(1))
    pos_data = [
        ["`ITD / CTO`",      "IT-директор / CTO с фокусом на цифровую трансформацию и GenAI"],
        ["`AI-Lead`",        "SBA / Head of AI / AI Lead (GenAI, Multi-Agent Systems, AI Quality)"],
        ["`GenAI-Arch`",     "Chief Architect / GenAI Architect с экспертизой в ГИС/Urban AI"],
    ]
    rows = [[Paragraph(f"<b>{t}</b>", SMALL_B), Paragraph(v, BODY)] for t,v in pos_data]
    tbl = Table(rows, colWidths=[70, CONTENT_W - 70])
    tbl.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (1,0), (1,-1),  6),
        ("BACKGROUND",    (0,0), (0,-1),  MUTED_BG),
        ("LINEBELOW",     (0,0), (-1,-2), 0.3, BORDER),
    ]))
    story.append(tbl)
    story.append(sp(2))

    # ══════════════════════════════════════════════════════════════════════
    # РАЗДЕЛ 2: SUMMARY
    # ══════════════════════════════════════════════════════════════════════
    story.append(sec_header("2. Summary (варианты)"))
    story.append(sp(1))

    summaries = [
        ("2.1 CTO-гибрид `ITD/CTO`",
         "21+ год опыта в ИТ, ГИС и цифровой трансформации. Co-Founder и CTO компании ВИЗАРД "
         "(продукт VIZARD — в реестре отечественного ПО). Руководил командами 50+ человек "
         "(20+ прямого подчинения), проектами от 10 млн до ~900 млн руб. Автор формирования "
         "Подкомиссии по пространственным данным Правкомиссии по ИКТ; автор проектов двух "
         "Распоряжений Правительства РФ. Спикер конференций, жюри AI/ГИС-хакатонов, автор 10+ РИД."),
        ("2.2 AI-ориентированный `AILead`",
         "Co-Founder и CTO ВИЗАРД, ведущий коммерческий продукт VIZARD (реестр отечественного ПО, "
         "клиенты — крупнейшие нефтегазовые компании РФ, нац. морской перевозчик, СПГ-операторы). "
         "Hands-on архитектор двух AI-направлений: hydromet_bulletin (Python, NetCDF/GRIB2, "
         "multi-agent AI, CI/CD) и ML-детекция сорных растений по БПЛА для Россельхознадзора "
         "(mAP@0.5 > 80%). Член экспертного совета ИНТЦ МГУ, спикер AI IN и Digital Innopolis Days."),
        ("2.3 Digital Transformation / госсектор",
         "Архитектор и руководитель крупных программ цифровой трансформации: Chief Architect ЕГИП "
         "г. Москвы (60+ ОИВ, 37 интегрированных систем, 100+ наборов данных, 3 года внедрения; "
         "лучшее интеграционное решение III Международного GIS-Forum 2015). Формирование "
         "Подкомиссии по пространственным данным Правкомиссии по ИКТ, проекты двух Распоряжений "
         "Правительства РФ. Благодарность Мэра Москвы (2015)."),
        ("2.4 Продуктово-международный",
         "Co-Founder и CTO ВИЗАРД: вывод VIZARD на рынок РФ и международная воронка — кастдев "
         "в Китае, ОАЭ, Великобритании, Чили, Бразилии, Турции, Японии с судовладельцами, "
         "логистикой и страховыми агентами. Новые направления: сервисы мониторинга для страховых "
         "компаний (hydromet_bulletin) и ML-детекция БПЛА для Россельхознадзора (MVP сдан). "
         "Победитель «АРКТЕК ИНЖИНИРИНГ» в двух номинациях, лауреат Российско-Китайского конкурса "
         "индустриальных инноваций 2023."),
    ]
    for title, text in summaries:
        story.append(Paragraph(title, H3))
        box = Table([[Paragraph(text, BODY)]], colWidths=[CONTENT_W - 12])
        box.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), MUTED_BG),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("RIGHTPADDING",  (0,0), (-1,-1), 8),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LINEAFTER",     (0,0), (0,-1),  2, TEAL),
        ]))
        story.append(box)
        story.append(sp(1))
    story.append(sp(1))

    # ══════════════════════════════════════════════════════════════════════
    # РАЗДЕЛ 3: КОМПЕТЕНЦИИ
    # ══════════════════════════════════════════════════════════════════════
    story.append(sec_header("3. Ключевые компетенции"))
    story.append(sp(1))

    # 3.1
    story.append(Paragraph("3.1 Управление и стратегия · `ITD CTO DigitalTransformation`", H3))
    story += bullet_list([
        "Цифровая трансформация, стратегия ИТ, управление портфелем продуктов и проектов.",
        "Кросс-функциональные команды: пик 50+, текущий масштаб 3–10; 20+ прямого подчинения.",
        "Бюджеты: ВИЗАРД до ~150 млн руб.; ЕГИП (ДИТ Москвы) до ~900 млн руб.",
        "TOGAF, COBIT, PRINCE2, IPMA (сертифицирован), ISO 31000, FMEA, SORA.",
        "Управление рисками, комплаенс, импортозамещение, работа с госзаказчиком.",
    ])
    story.append(sp(1))

    # 3.2
    story.append(Paragraph("3.2 AI / GenAI / Data · `AI-Lead GenAI-Arch CTO`", H3))
    story += bullet_list([
        "GenAI, LLM, Agentic RAG, GraphRAG, multi-agent workflows.",
        "Prompt engineering и оркестрация AI-агентов (Cursor, Windsurf, Perplexity).",
        "AI Quality [arch/lead]: Autonomy Boundary Matrix, Constitutional AI (hard guardrails, forbidden action rate 0%), "
        "Evaluation Framework (KRI: ECE, missed escalation rate, source attribution rate), Langfuse self-hosted; "
        "[growing]: Critic loop / LLM-as-judge, Self-RAG, GraphRAG (Apache AGE).",
        "ML первого поколения — детекция объектов на LiDAR + стереофото (ЕГИП, 2014–2016).",
        'Принимаю личное участие в развитии AI-стека.',
        'ESG & Climate GeoAI: мониторинг ПГ (CO\u2082/CH\u2084), NbS-анализ, MRV-технологии.',
        'Edge-инференс на БПЛА и бортовых устройствах (без выделенного GPU).',
    ])
    story.append(sp(1))

    # 3.3, 3.4, 3.5 — компактно
    for h, tag, items in [
        ("3.3 Архитектура и разработка", "`CTO GenAI-Arch GeoAI`", [
            "Enterprise / Solution Architecture, API-платформы, корпоративная интеграция.",
            "Python (pytest, asyncio, APScheduler), SQL, PostgreSQL/PostGIS, Oracle.",
            "CI/CD, Docker, Git/GitHub, DevOps-практики.",
        ]),
        ("3.4 ГИС / Urban AI / ДЗЗ", "`GeoAI CTO DigitalTransformation`", [
            "ArcGIS, QGIS, MapInfo, Bentley, EverGIS; 3D + LiDAR, CAD/BIM.",
            "NetCDF, GeoTIFF, GRIB2, Shapefile, GeoPackage. Метеоданные: GFS, CMEMS, ERA5, NOAA.",
            "Данные БПЛА (RGB), крупноформатные наборы изображений, ML-пайплайн детекции.",
            "Арктические акватории: SAR \u2192 RGB-композиты, классификация льдов, детекция судов и айсбергов; интеграция с AIS и метеоданными (CO\u2082/CH\u2084).",
        ]),
        ("3.5 Продукт и рынок", "`CTO AI-Lead DigitalTransformation`", [
            "Customer journey, AI-journey, product discovery, кастдев.",
            "Международный market research: Китай, ОАЭ, Великобритания, Чили, Бразилия, Турция, Япония.",
            "B2G / B2B / B2C; нефтегаз, морские перевозки, страхование морских рисков, рыболовство.",
        ]),
    ]:
        story.append(Paragraph(f"{h} · {tag}", H3))
        story += bullet_list(items)
        story.append(sp(1))

    story.append(sp(2))

    # ══════════════════════════════════════════════════════════════════════
    # РАЗДЕЛ 4: ОПЫТ РАБОТЫ
    # ══════════════════════════════════════════════════════════════════════
    story.append(sec_header("4. Опыт работы"))
    story.append(sp(1))

    # 4.1
    story.append(Paragraph("4.1 Ранний период", H3))
    story += bullet_list([
        "2004–2012 — РЖД, CSoft, Прайм груп, Эверпоинт: рост от инженера/аналитика до и.о. начальника управления.",
        "Hands-on: корпоративные ГИС, DWH/data-платформы (2007–2009), Oracle Database 10g, ArcGIS.",
    ])
    story.append(sp(1))
    rule()

    # 4.2
    story.append(Paragraph("4.2 ЕГИП г. Москвы", H3))
    for item in exp_block(
        "2012–2016",
        "Chief Architect / Scenario Business Architect — ЕГИП г. Москвы",
        "Департамент информационных технологий города Москвы",
        "ITD, CTO, DigitalTransformation, GeoAI",
        [
            "Архитектор и один из лидеров программы создания единого геоинформационного пространства Москвы.",
            "60+ органов исполнительной власти · 37 интегрированных систем · 100+ наборов пространственных данных · 3 года.",
            "ML первого поколения — детекция объектов на LiDAR + стереофото (без ретроактивных GenAI-приписок).",
            "Формирование Подкомиссии Правкомиссии по ИКТ; подготовка проектов двух Распоряжений Правительства РФ.",
            "Организация закупочной деятельности ЕГИП (44-ФЗ / 223-ФЗ), сторона государственного заказчика.",
            "Лучшее интеграционное решение, III Международный GIS-Forum, 2015. Благодарность Мэра Москвы, 2015.",
        ]
    ): story.append(item)
    story.append(rule())
    story.append(sp(1))

    # 4.3 — переход (одна строка)
    story.append(Paragraph("4.3 Переход ЕГИП → VIZARD / ВИЗАРД", H3))
    story += bullet_list([
        "2017 — старт VIZARD как внутренней продуктовой инициативы; 2019 — создание компании ВИЗАРД.",
    ])
    story.append(rule())
    story.append(sp(1))

    # 4.4 ВИЗАРД
    story.append(Paragraph("4.4 ВИЗАРД", H3))
    for item in exp_block(
        "2017 — н.в.",
        "Co-Founder / CTO / SBA / Product Owner AI & Data — ВИЗАРД",
        "Компания ВИЗАРД · платформа VIZARD (реестр отечественного ПО)",
        "CTO, AI-Lead, GenAI-Arch, DigitalTransformation, GeoAI",
        [
            "Вывод продукта VIZARD на рынок РФ; клиенты — крупнейшие нефтегазовые компании РФ, "
            "нац. морской перевозчик, СПГ-операторы, промысловые компании Дальнего Востока.",
            "Команда on-board: пик 17 чел. (2023), тек. масштаб 4 чел.; суммарно над продуктом 50+ (партнёры + подрядчики).",
            "Бюджет продукта: до ~150 млн руб.",
            "KPI: скорость СМП +17% (~350 тыс. USD/рейс); период эксплуатации буровой 120→200 сут.; -30% потерь снастей.",
            "Международный кастдев: Китай, ОАЭ, Великобритания, Чили, Бразилия, Турция, Япония.",
            "ML: SAR → RGB-композиты GeoTIFF → классификация; U-Net → U-Net++ (Attention Gate) → SegFormer.",
            "SegFormer закрыл проблему граничных классов льда; открыл направление страхования морских рисков.",
            "Переход на SegFormer устранил артефакт влажного снега в SAR (три слоя закрытия: data quality flag "
            "→ confidence score → hard guardrail в БОЦ; до клиента не дошло).",
            "В условиях санкций: переархитектура на локальный мессенджер и доступные источники данных.",
            "Победитель «АРКТЕК ИНЖИНИРИНГ» в двух номинациях; лауреат Российско-Китайского конкурса, 2023.",
            "Октябрь 2025 — новое направление: ML-детекция сорных растений по БПЛА для Россельхознадзора (MVP сдан).",
            "Edge-инференс: модели классификации льдов и детекции айсбергов/судов (EfficientNet, LLaMA-подобные арх.) обучались на ноутбуках GPU, далее функционируют на планшетах наблюдателей БОЦ и БПЛА без выделенного GPU.",
            "M&A: участвую в текущей сделке по продаже компании (детали под NDA).",
        ]
    ): story.append(item)
    story.append(rule())
    story.append(sp(1))

    # 4.5 hydromet_bulletin
    story.append(Paragraph("4.5 Подпроект hydromet_bulletin (в рамках ВИЗАРД)", H3))
    story += bullet_list([
        "Python (pytest, asyncio, APScheduler), PostgreSQL/PostGIS, NetCDF/GRIB2/GeoTIFF/GeoPackage.",
        "Источники: GFS, CMEMS, ERA5, NOAA. Multi-agent AI-оркестрация: Cursor, Windsurf, Perplexity.",
        "CI/CD, Docker, Git/GitHub. Открытый репозиторий GitHub — доступ по запросу; демо на собеседовании.",
    ])
    story.append(sp(1))

    # 4.5б ESG / Climate GeoAI
    story.append(Paragraph("4.5б Подпроект VIZARD · ESG-направление: климатические риски и мониторинг ПГ на СМП (2024 — н.в.)", H3))
    story += bullet_list([
        "По итогам CustDev и Market Research (БРИКС+, 2024–2025) инициировал новое продуктовое направление VIZARD: "
        "цифровой мониторинг климатических рисков и выбросов ПГ для судоходства на СМП; проведён кастдев "
        "с нефтегазовыми компаниями и операторами КНГ.",
        "Спроектировал архитектуру GeoAI-модуля: интеграция ДЗЗ (САР, мультиспектр), AIS-данных "
        "и метеоисточников (GFS, CMEMS, ERA5) для пространственно-временного анализа эмиссий CO\u2082/CH\u2084 "
        "в арктических акваториях; ML-пайплайн валидации по NOAA Arctic Report Card.",
        "Экспертный вклад в исследование по Nature-Based Solutions для российской Арктики "
        "(Sustainability, MDPI, 2025, 17, 10409; авторы — МГУ, ИЭПИ): GIS-поддержка, "
        "пространственный анализ арктических экосистем, картографирование зон NbS "
        "(леса, болота, ревайлдинг, восстановление экосистем).",
    ])
    story.append(rule())
    story.append(sp(1))

    # 4.5a Россельхознадзор
    story.append(Paragraph("4.5a Подпроект «Внедрение ИИ в деятельность Россельхознадзора» (окт. 2025 — н.в.)", H3))
    story += bullet_list([
        "Детекция сорных и карантинных растений по RGB-БПЛА; десятки тысяч изображений, разметка специалистами.",
        "Стек: YOLO, EfficientDet, ResNet, Faster R-CNN; трансформерные ViT, DETR, RT-DETR, SegFormer; SAHI, Raster Vision.",
        "Метрики: mAP@0.5 > 80%; IoU > 0.75; F1 > 0.8; Recall > 0.85. MVP сдан заказчику.",
    ])
    story.append(rule())
    story.append(sp(1))

    # 4.6 Роскадастр
    for item in exp_block(
        "апр. 2025 — н.в.",
        "Главный инженер (советник по ИИ) — ППК «Роскадастр»",
        "ППК «Роскадастр» / филиал «Инфотех» · консалтинговый проект",
        "ITD, CTO, DigitalTransformation, GeoAI",
        [
            "Стек госконтура: GigaChat (Сбер) + YandexGPT · pgvector (on-prem) · Apache AGE (GraphRAG) "
            "· LangChain · Langfuse self-hosted · ruBERT + E5. RAG из реестра РПОиБД. Нуль иностранного SaaS.",
            "Проектировал стандарты поведения LLM-агента: Autonomy Boundary Matrix, Constitutional AI, "
            "Evaluation Framework с KRI и триггерами деградации.",
            "[arch/lead] Autonomy Boundary Matrix: зелёная/жёлтая/красная зоны — внедрил в проектный стандарт.",
            "[arch/lead] Constitutional AI: блокировка юрид. значимых формулировок без верифицированного основания — до рендеринга.",
            "[arch/lead] Evaluation Framework: KRI + quality gate + source attribution rate (<90% → алерт + ревизия KB).",
            "[familiar/growing] Self-RAG + Critic loop, GraphRAG (Apache AGE) — проектный стандарт, не личный production-код.",
        ]
    ): story.append(item)
    story.append(sp(2))

    # ══════════════════════════════════════════════════════════════════════
    # РАЗДЕЛ 5: ВИТРИНА ПРОЕКТОВ
    # ══════════════════════════════════════════════════════════════════════
    story.append(sec_header("5. Витрина проектов"))
    story.append(sp(1))

    projects = [
        ("ЕГИП г. Москвы", "ITD / CTO / DigitalTransformation",
         "60+ ОИВ · 37 интегрированных систем · 100+ наборов данных · 3 года. "
         "Лучшее интеграционное решение III Международного GIS-Forum 2015."),
        ("VIZARD — коммерческая платформа", "CTO / AILead",
         "Рынок РФ + международная воронка. KPI: +17% скорость СМП, 120→200 сут. бурение, -30% потерь снастей. "
         "Победитель «АРКТЕК ИНЖИНИРИНГ» в двух номинациях."),
        ("Страхование морских рисков (новое напр.)", "CTO / AILead",
         "Кастдев в 7 странах → подтверждён интерес рынка → запуск разработки. "
         "Технологическая витрина — hydromet_bulletin."),
        ("hydromet_bulletin (hands-on кейс)", "AILead / GenAIArch",
         "Python / NetCDF / GRIB2 / multi-agent AI / CI/CD. Демо-кейс hands-on компетенций архитектора и разработчика."),
        ("Россельхознадзор — ML на БПЛА", "AILead / GenAIArch",
         "mAP@0.5 > 80%; ~100 видов сорных растений. MVP сдан. SegFormer / DETR / YOLO. Статус: конкурсные процедуры."),
        ("Роскадастр — LLM-агент", "ITD / AILead",
         "Госконтур: GigaChat + YandexGPT + pgvector + Langfuse self-hosted. "
         "AI Quality стандарты: Constitutional AI, Autonomy Boundary Matrix, Evaluation Framework."),
        ("VIZARD · ESG/Climate GeoAI", "CTO / AILead / GeoAI",
         "Цифровой мониторинг ПГ и климатических рисков СМП: GeoAI-модуль, SAR + AIS + ERA5/CMEMS, "
         "анализ CO\u2082/CH\u2084; edge-инференс на БПЛА; NbS-анализ арктических экосистем (Sustainability, 2025)."),
    ]
    proj_rows = []
    for title, tags, desc in projects:
        proj_rows.append([
            Paragraph(f"<b>{title}</b>", SMALL_B),
            Paragraph(f"<i>{tags}</i>", TAG),
            Paragraph(desc, SMALL),
        ])
    proj_tbl = Table(proj_rows, colWidths=[110, 78, CONTENT_W - 188])
    proj_tbl.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (1,0), (2,-1),  5),
        ("BACKGROUND",    (0,0), (0,-1),  MUTED_BG),
        ("LINEBELOW",     (0,0), (-1,-2), 0.3, BORDER),
    ]))
    story.append(proj_tbl)
    story.append(sp(2))

    # ══════════════════════════════════════════════════════════════════════
    # РАЗДЕЛ 6–9: РЕГУЛЯТОРИКА / ПУБЛИЧНАЯ АКТИВНОСТЬ / НАГРАДЫ
    # ══════════════════════════════════════════════════════════════════════
    # KeepTogether: заголовок секции + вся двухколоночная таблица
    sec_69_header = sec_header("6–9. Регуляторика · Публичная активность · Награды")

    # Две колонки
    col_l = [
        Paragraph("Регуляторика и государственная экспертиза", H3),
    ] + bullet_list([
        "Формирование Подкомиссии по пространственным данным Правкомиссии по ИКТ.",
        "Автор проектов двух утверждённых Распоряжений Правительства РФ.",
        "Член рабочей группы ГОСТ Р «Пространственные данные. Качество данных».",
        "Член экспертного совета ИНТЦ МГУ «Воробьёвы горы».",
        "VIZARD включён в реестр отечественного ПО Минцифры РФ.",
        "44-ФЗ / 223-ФЗ: сторона государственного заказчика (ЕГИП) и 10+ конкурсов (сторона участника).",
    ]) + [
        sp(1),
        Paragraph("Награды", H3),
    ] + bullet_list([
        "Благодарность Мэра Москвы, 2015.",
        "ЕГИП — лучшее интеграционное решение, III GIS-Forum, 2015.",
        "Победитель «АРКТЕК ИНЖИНИРИНГ» в двух номинациях.",
        "Лауреат Российско-Китайского конкурса, 2023.",
    ])

    col_r = [
        Paragraph("Публичная активность", H3),
    ] + bullet_list([
        "Спикер: RAO-CIS (с 2018), Saudi Maritime Congress (Даммам, 2024), AI IN (Казань, 2023), Digital Innopolis Days (2025).",
        "Жюри: Портал открытых данных Правительства Москвы, 2ГИС, AI & Business Hackathon.",
        "Преподавание: РАНХиГС (авторский курс), РУДН (семинары), МИИГАиК (член ГАК).",
        "Амбассадор сообщества «Техпросвет» в VK.",
        "5+ публикаций · 10+ РИД.",
    ]) + [
        sp(1),
        Paragraph("Ключевые публикации", H3),
    ] + bullet_list([
        "«Искусство видеть льды» // ПортНьюс, 2024, № 3(51).",
        "«Комплексный ледовый мониторинг на основе продуктов ООО ВИЗАРД» // НГН, 2022.",
        "«Система оперативного мониторинга ледовой обстановки (нейросети, SAR)» // НГН, 2021.",
        "«Методика ледовой разведки с БПЛА» // НГН, 2020.",
        "Эксперт по GIS/GeoAI: \u00abAre Nature-Based Climate Solutions in the Russian Arctic Feasible?\u00bb // Sustainability, MDPI, 2025, 17, 10409. "
        "(авторы: МГУ биофак + геофак, ИЭПИ).",
    ])

    col_w = (CONTENT_W - 8) / 2
    two_col = Table([[col_l, col_r]], colWidths=[col_w, col_w])
    two_col.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",   (0,0), (0,-1),  0),
        ("RIGHTPADDING",  (0,0), (0,-1),  6),
        ("LEFTPADDING",   (1,0), (1,-1),  8),
        ("RIGHTPADDING",  (1,0), (1,-1),  0),
        ("LINEAFTER",     (0,0), (0,-1),  0.5, BORDER),
    ]))
    story.append(KeepTogether([sec_69_header, sp(1), two_col]))
    story.append(sp(2))

    # ══════════════════════════════════════════════════════════════════════
    # РАЗДЕЛ 10: ОБРАЗОВАНИЕ
    # ══════════════════════════════════════════════════════════════════════
    story.append(sec_header("10. Образование и сертификации"))
    story.append(sp(1))
    edu_rows = [
        ("Дипломатическая академия МИД России", "Международные отношения", "2011"),
        ("МИИГАиК", "Прикладная космонавтика", "2006"),
        ("Сертификация IPMA", "№ D0861", "2009"),
        ("Курсы", "Oracle Database 10g (SQL/PL/SQL/Admin/Tuning), ArcGIS 9, UML, Linux", "2004–2008"),
        ("Методологии (без сертификации)", "TOGAF, COBIT, PRINCE2, ISO 31000, FMEA, SORA", "—"),
    ]
    edu_tbl = Table(
        [[Paragraph(f"<b>{r[0]}</b>", SMALL_B), Paragraph(r[1], BODY), Paragraph(r[2], SMALL)]
         for r in edu_rows],
        colWidths=[155, CONTENT_W - 215, 60]
    )
    edu_tbl.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (1,0), (2,-1),  6),
        ("BACKGROUND",    (0,0), (0,-1),  MUTED_BG),
        ("ALIGN",         (2,0), (2,-1),  "CENTER"),
        ("LINEBELOW",     (0,0), (-1,-2), 0.3, BORDER),
    ]))
    story.append(edu_tbl)
    story.append(sp(2))

    # ══════════════════════════════════════════════════════════════════════
    # РАЗДЕЛ 11: ЗАРПЛАТНЫЙ ОРИЕНТИР
    # ══════════════════════════════════════════════════════════════════════
    story.append(sec_header("11. Формат и условия"))
    story.append(sp(1))
    sal_rows = [
        ("Зарплата", "от 500 000 руб."),
        ("Формат", "удалённо, гибрид, офис Москвы"),
        ("Релокация", "готов рассматривать с сентября 2027"),
    ]
    sal_tbl = Table(
        [[Paragraph(f"<b>{k}</b>", SMALL_B), Paragraph(v, BODY)] for k, v in sal_rows],
        colWidths=[120, CONTENT_W - 120]
    )
    sal_tbl.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (1,0), (1,-1),  6),
        ("BACKGROUND",    (0,0), (0,-1),  MUTED_BG),
        ("LINEBELOW",     (0,0), (-1,-2), 0.3, BORDER),
    ]))
    story.append(sal_tbl)
    story.append(sp(2))

    # ══════════════════════════════════════════════════════════════════════
    # РАЗДЕЛ 12: КЛЮЧЕВЫЕ КОМАНДЫ
    # ══════════════════════════════════════════════════════════════════════
    story.append(sec_header("12. Ключевые команды"))
    story.append(sp(1))
    teams_rows = [
        ("ВИЗАРД (2017—н.в.)",
         "он-борд: пик 17 чел. (2023), сейчас 4 чел. | "
         "суммарно над продуктом 50+ (партнёры + подрядчики)"),
        ("ЕГИП ДИТ Москвы (2012—2016)",
         "20+ чел. прямого подчинения | 60+ ОИВ в программе"),
        ("Роскадастр (2025—н.в.)",
         "консалтинговый формат; практика сети партнёров и подрядчиков"),
    ]
    teams_tbl = Table(
        [[Paragraph(f"<b>{k}</b>", SMALL_B), Paragraph(v, BODY)] for k, v in teams_rows],
        colWidths=[145, CONTENT_W - 145]
    )
    teams_tbl.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (1,0), (1,-1),  6),
        ("BACKGROUND",    (0,0), (0,-1),  MUTED_BG),
        ("LINEBELOW",     (0,0), (-1,-2), 0.3, BORDER),
    ]))
    story.append(teams_tbl)
    story.append(sp(2))

    # ══════════════════════════════════════════════════════════════════════
    # РАЗДЕЛ 13: СТЕК
    # ══════════════════════════════════════════════════════════════════════
    story.append(sec_header("13. Инструменты и стек (сводно)"))
    story.append(sp(1))
    stack_rows = [
        ("Языки / скрипты", "Python (pytest, asyncio, APScheduler), SQL, Bash/PowerShell, HTML/CSS, Markdown/PlantUML"),
        ("Данные и ГИС", "PostgreSQL/PostGIS, Oracle · NetCDF, GeoTIFF, GRIB2, Shapefile, GeoPackage · ArcGIS, QGIS, MapInfo, Bentley, EverGIS"),
        ("Метеоданные", "GFS, CMEMS, ERA5, NOAA"),
        ("AI / ML (arch)", "LLM · Agentic RAG (Self-RAG) · GraphRAG · multi-agent orchestration · Constitutional AI · fine-tuning LLM · Evaluation Framework (ABM, quality gate, KRI)"),
        ("Госконтур", "GigaChat · YandexGPT · pgvector · Apache AGE · LangChain · Langfuse self-hosted · ruBERT · E5"),
        ("Computer Vision", "YOLO / EfficientDet / InternImage / ResNet / Faster R-CNN · ViT / DETR / RT-DETR / SegFormer · SAHI · Raster Vision · SAR→GeoTIFF→SegFormer (VIZARD)"),
        ("DevOps / IDE", "Cursor, Windsurf, Perplexity, VS Code, Git/GitHub, Docker, CI/CD, pytest"),
        ("Архитектура", "C4, PlantUML, ADR, Markdown · TOGAF, COBIT, PRINCE2, IPMA, ISO 31000"),
    ]
    stk_tbl = Table(
        [[Paragraph(f"<b>{k}</b>", SMALL_B), Paragraph(v, SMALL)] for k,v in stack_rows],
        colWidths=[80, CONTENT_W - 80]
    )
    stk_tbl.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (1,0), (1,-1),  6),
        ("BACKGROUND",    (0,0), (0,-1),  MUTED_BG),
        ("LINEBELOW",     (0,0), (-1,-2), 0.3, BORDER),
    ]))
    story.append(stk_tbl)
    story.append(sp(2))

    # ══════════════════════════════════════════════════════════════════════
    # ══════════════════════════════════════════════════════════════════════
    # РАЗДЕЛ 15: СЛОВАРЬ ФОРМУЛИРОВОК
    # ══════════════════════════════════════════════════════════════════════
    story.append(sec_header("14. Словарь обобщённых формулировок для резюме"))
    story.append(sp(1))
    vocab = [
        ("Газпром / Роснефть / НОВАТЭК", "крупнейшие нефтегазовые компании РФ"),
        ("Совкомфлот", "национальный морской перевозчик"),
        ("Сахалинская энергия (+ НОВАТЭК)", "оператор крупных СПГ-проектов"),
        ("Промысловые компании ДВ", "добывающие и промысловые компании Дальнего Востока"),
        ("Международный кастдев", "судовладельцы, морские логистические компании и страховые агенты в Азии, Ближнем Востоке, Европе, Латинской Америке"),
        ("ВИЗАРД / VIZARD", "ВИЗАРД (кириллица) = компания · VIZARD (латиница) = продукт/платформа"),
        ("М&А", "участвую в сделке по продаже компании более крупному игроку рынка (детали под NDA)"),
    ]
    voc_tbl = Table(
        [[Paragraph(f"<b>{k}</b>", SMALL_B), Paragraph(v, SMALL)] for k,v in vocab],
        colWidths=[120, CONTENT_W - 120]
    )
    voc_tbl.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (1,0), (1,-1),  6),
        ("BACKGROUND",    (0,0), (0,-1),  MUTED_BG),
        ("LINEBELOW",     (0,0), (-1,-2), 0.3, BORDER),
    ]))
    story.append(voc_tbl)
    story.append(sp(1))

    story.append(sp(2))

    doc.build(story)
    print(f"PDF создан: {OUT_PATH}")

build()
