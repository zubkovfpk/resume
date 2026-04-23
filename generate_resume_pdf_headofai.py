#!/usr/bin/env python3
"""
Генерация PDF-резюме: Зубков С.А. — Head of AI / AI Lead / Product Owner AI
Адаптировано под вакансию Melon Fashion Group / Zarina
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus.flowables import Flowable
import os

# ─── Шрифты ───────────────────────────────────────────────────────────────────
FONT_DIR = "/tmp/fonts"
pdfmetrics.registerFont(TTFont("Inter",         f"{FONT_DIR}/Inter-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Bold",    f"{FONT_DIR}/Inter-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Semi",    f"{FONT_DIR}/Inter-SemiBold.ttf"))
pdfmetrics.registerFontFamily("Inter", normal="Inter", bold="Inter-Bold")

# ─── Цвета (фирменный стиль VIZARD) ───────────────────────────────────────────
GREEN       = HexColor("#21a038")
GREEN_LIGHT = HexColor("#e8f5e9")
GREEN_FAINT = HexColor("#f0faf2")
BLUE_FAINT  = HexColor("#f0f8ff")
DARK        = HexColor("#1a1a1a")
MID         = HexColor("#333333")
GREY        = HexColor("#555555")
GREY_LIGHT  = HexColor("#e0e0e0")
SKILL_BG    = HexColor("#f5f5f5")
SKILL_BG2   = HexColor("#e8e8e8")
HIGHLIGHT   = HexColor("#fff3cd")
KPI_BORDER  = GREEN

# ─── Размеры страницы A4 ──────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4          # 595 x 842 pt
ML = 18*mm                   # левый отступ
MR = 18*mm                   # правый отступ
MT = 10*mm                   # верхний
MB = 12*mm                   # нижний
CONTENT_W = PAGE_W - ML - MR # ~559 pt

# ─── Стили текста ─────────────────────────────────────────────────────────────
def S(name, **kw):
    base = kw.pop("parent", None)
    return ParagraphStyle(name, parent=base, **kw)

BASE = S("Base", fontName="Inter", fontSize=8, leading=11.5,
         textColor=MID, spaceAfter=0, spaceBefore=0)

NAME_STYLE = S("Name", parent=BASE, fontName="Inter-Bold",
               fontSize=20, leading=24, textColor=DARK)

TITLE_STYLE = S("Title", parent=BASE, fontName="Inter-Semi",
                fontSize=10, leading=13, textColor=GREEN, spaceAfter=3)

CONTACT_STYLE = S("Contact", parent=BASE, fontSize=8, leading=11, textColor=GREY)

SECTION_TITLE = S("SecTitle", parent=BASE, fontName="Inter-Bold",
                  fontSize=10, leading=12.5, textColor=GREEN,
                  spaceBefore=5, spaceAfter=2)

BODY = S("Body", parent=BASE, fontSize=8, leading=11.5, textColor=MID, spaceAfter=3)

EXP_TITLE = S("ExpTitle", parent=BASE, fontName="Inter-Bold",
              fontSize=9, leading=11.5, textColor=DARK)

EXP_COMPANY = S("ExpCompany", parent=BASE, fontName="Inter-Semi",
                fontSize=8, leading=10.5, textColor=GREEN, spaceAfter=2)

BULLET = S("Bullet", parent=BASE, fontSize=8, leading=11.5,
           leftIndent=10, firstLineIndent=-10, textColor=MID, spaceAfter=1.5)

SMALL = S("Small", parent=BASE, fontSize=7.5, leading=10.5, textColor=GREY)

KPI_VAL = S("KPIVal", parent=BASE, fontName="Inter-Bold",
            fontSize=9, leading=11.5, textColor=GREEN, alignment=TA_CENTER)

KPI_NAME = S("KPIName", parent=BASE, fontSize=7, leading=9.5,
             textColor=GREY, alignment=TA_CENTER)

KPI_STATUS = S("KPIStatus", parent=BASE, fontSize=7, leading=9.5,
               textColor=GREY, alignment=TA_CENTER)

STACK = S("Stack", parent=BASE, fontSize=7.5, leading=11, textColor=MID)

MOTIVE = S("Motive", parent=BASE, fontSize=8, leading=11.5,
           textColor=DARK, leftIndent=8)


# ─── Вспомогательные функции ─────────────────────────────────────────────────

def section_header(title: str) -> list:
    return [
        Paragraph(title.upper(), SECTION_TITLE),
        HRFlowable(width="100%", thickness=1.5, color=GREY_LIGHT,
                   spaceAfter=4, spaceBefore=0),
    ]


def bullet(text: str) -> Paragraph:
    return Paragraph(f"• &nbsp;{text}", BULLET)


def bold(text: str) -> str:
    return f'<font name="Inter-Bold" color="#1a1a1a">{text}</font>'


def green(text: str) -> str:
    return f'<font color="#21a038">{text}</font>'


def highlight(text: str) -> str:
    return f'<font name="Inter-Bold">{text}</font>'


# ─── Строка опыта ─────────────────────────────────────────────────────────────
def exp_header(role: str, period: str) -> Table:
    role_p   = Paragraph(role, EXP_TITLE)
    period_p = Paragraph(period, S("Period", parent=BASE, fontSize=8,
                                   textColor=GREY, alignment=TA_RIGHT))
    t = Table([[role_p, period_p]],
              colWidths=[CONTENT_W * 0.72, CONTENT_W * 0.28])
    t.setStyle(TableStyle([
        ("VALIGN",  (0,0), (-1,-1), "BOTTOM"),
        ("PADDING", (0,0), (-1,-1), 0),
    ]))
    return t


# ─── KPI-таблица ──────────────────────────────────────────────────────────────
def kpi_table(items: list, inner_w: float = None) -> Table:
    w = inner_w if inner_w is not None else CONTENT_W
    col_w = w / len(items)
    cells = []
    for val, name, status in items:
        cell = [
            Paragraph(val,    KPI_VAL),
            Paragraph(name,   KPI_NAME),
            Paragraph(status, KPI_STATUS),
        ]
        cells.append(cell)

    t = Table([cells], colWidths=[col_w]*len(items), hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BOX",        (0,0), (-1,-1), 1,   GREEN),
        ("INNERGRID",  (0,0), (-1,-1), 0.5, GREEN_LIGHT),
        ("BACKGROUND", (0,0), (-1,-1), white),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
        ("RIGHTPADDING",  (0,0),(-1,-1), 5),
        ("VALIGN",     (0,0), (-1,-1), "TOP"),
    ]))
    return t


def kpi_box(title: str, items: list) -> list:
    PAD = 6
    inner_w = CONTENT_W - PAD * 2

    title_p = Paragraph(title, S("KPIBoxTitle", parent=BASE, fontName="Inter-Bold",
                                  fontSize=8.5, textColor=GREEN, alignment=TA_CENTER))
    kpi_t = kpi_table(items, inner_w=inner_w)

    combined = Table(
        [[title_p], [kpi_t]],
        colWidths=[CONTENT_W]
    )
    combined.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), BLUE_FAINT),
        ("BOX",           (0,0),(-1,-1), 1.5, GREEN),
        ("TOPPADDING",    (0,0),(0,0),   5),
        ("BOTTOMPADDING", (0,0),(0,0),   3),
        ("TOPPADDING",    (0,1),(0,1),   0),
        ("BOTTOMPADDING", (0,1),(0,1),   5),
        ("LEFTPADDING",   (0,0),(-1,-1), PAD),
        ("RIGHTPADDING",  (0,0),(-1,-1), PAD),
    ]))
    return [combined, Spacer(1, 5)]


# ─── Сетка компетенций ────────────────────────────────────────────────────────
def skills_grid(cards: list) -> Table:
    col_w = (CONTENT_W - 4) / 3

    rows_data = []
    for i in range(0, len(cards), 3):
        row_cards = cards[i:i+3]
        while len(row_cards) < 3:
            row_cards.append(("", ""))
        rows_data.append(row_cards)

    all_rows = []
    for row_cards in rows_data:
        title_row = [
            Paragraph(t, S(f"SkT_{i}_{len(all_rows)}", parent=BASE, fontName="Inter-Bold",
                           fontSize=8.5, textColor=DARK, spaceAfter=1))
            for i, (t, _) in enumerate(row_cards)
        ]
        body_row = [
            Paragraph(b, S(f"SkB_{i}_{len(all_rows)}", parent=BASE, fontSize=7.5,
                           textColor=HexColor("#444444"), leading=11))
            for i, (_, b) in enumerate(row_cards)
        ]
        all_rows.append(title_row)
        all_rows.append(body_row)

    col_ws = [col_w, col_w, col_w]
    t = Table(all_rows, colWidths=col_ws)

    style_cmds = [
        ("VALIGN",      (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("RIGHTPADDING",(0,0), (-1,-1), 5),
        ("TOPPADDING",  (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
    ]

    num_card_rows = len(rows_data)
    for ri in range(num_card_rows):
        r0 = ri * 2
        r1 = ri * 2 + 1
        style_cmds += [
            ("BACKGROUND", (0,r0), (-1,r1), SKILL_BG),
        ]
        for ci in range(3):
            style_cmds.append(("LINEBEFORE", (ci,r0), (ci,r1), 3, GREEN))
        if ri < num_card_rows - 1:
            style_cmds.append(("BOTTOMPADDING", (0,r1), (-1,r1), 5))

    for ri in range(num_card_rows):
        r0 = ri * 2
        style_cmds.append(("TOPPADDING",    (0,r0), (-1,r0), 5))
        style_cmds.append(("BOTTOMPADDING", (0,r0), (-1,r0), 1))

    t.setStyle(TableStyle(style_cmds))
    return t


# ─── Метрики-бейджи ───────────────────────────────────────────────────────────
def metrics_row(items: list) -> Table:
    col_w = CONTENT_W / len(items)
    row_vals = []
    row_lbls = []
    for val, lbl in items:
        row_vals.append(Paragraph(val, S(f"MVal_{val[:4]}", parent=BASE, fontName="Inter-Bold",
                              fontSize=12, textColor=GREEN, alignment=TA_CENTER)))
        row_lbls.append(Paragraph(lbl.upper(), S(f"MLbl_{val[:4]}", parent=BASE, fontSize=6.5,
                                      textColor=GREY, alignment=TA_CENTER, leading=9)))
    t = Table([row_vals, row_lbls], colWidths=[col_w]*len(items))
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), GREEN_LIGHT),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
        ("INNERGRID",     (0,0),(-1,-1), 0.5, white),
    ]))
    return t


# ─── Теги ─────────────────────────────────────────────────────────────────────
def tag_line(labels: list) -> Paragraph:
    parts = [f'<font color="#21a038" name="Inter-Semi">{lbl}</font>' for lbl in labels]
    joined = ' <font color="#aaaaaa">·</font> '.join(parts)
    return Paragraph(joined, S("TagLine", parent=BASE, fontSize=7.5, leading=11,
                               textColor=GREEN, spaceAfter=3))


# ─── Строка опыта с тегами ────────────────────────────────────────────────────
def exp_header_with_tags(role: str, period: str, company: str, tags: list) -> list:
    role_p   = Paragraph(role, EXP_TITLE)
    period_p = Paragraph(period, S("Period2", parent=BASE, fontSize=8,
                                    textColor=GREY, alignment=TA_RIGHT))
    header_t = Table([[role_p, period_p]],
                     colWidths=[CONTENT_W * 0.72, CONTENT_W * 0.28])
    header_t.setStyle(TableStyle([
        ("VALIGN",  (0,0), (-1,-1), "BOTTOM"),
        ("PADDING", (0,0), (-1,-1), 0),
    ]))
    company_p = Paragraph(company, EXP_COMPANY)
    tags_p    = tag_line(tags)
    return [header_t, company_p, tags_p]


# ─── Двухколоночная таблица ───────────────────────────────────────────────────
def two_col_table(left_items, right_items, left_title, right_title,
                  left_w=None, right_w=None) -> Table:
    half = (CONTENT_W - 4*mm) / 2
    if left_w is None:
        left_w = half
    if right_w is None:
        right_w = half

    def col_content(title, items, col_w):
        parts = [Paragraph(bold(title), S(f"ColT_{title[:6]}", parent=BASE, fontName="Inter-Bold",
                                           fontSize=8.5, textColor=DARK, spaceAfter=3))]
        for item in items:
            parts.append(bullet(item))
        return parts, col_w

    left_parts,  lw = col_content(left_title,  left_items,  left_w)
    right_parts, rw = col_content(right_title, right_items, right_w)

    def wrap(parts, col_w):
        t = Table([[p] for p in parts], colWidths=[col_w])
        t.setStyle(TableStyle([
            ("LEFTPADDING",  (0,0),(-1,-1), 0),
            ("RIGHTPADDING", (0,0),(-1,-1), 0),
            ("TOPPADDING",   (0,0),(-1,-1), 0),
            ("BOTTOMPADDING",(0,0),(-1,-1), 1),
        ]))
        return t

    outer = Table([[wrap(left_parts, lw), wrap(right_parts, rw)]], colWidths=[lw, rw])
    outer.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (1,0),(1,-1),  0),
        ("RIGHTPADDING",  (0,0),(0,-1),  4*mm),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
    ]))
    return outer


# ─── Шапка документа ──────────────────────────────────────────────────────────
def build_header() -> list:
    story = []

    name_p  = Paragraph("Зубков Сергей Андреевич", NAME_STYLE)
    title_p = Paragraph("Head of AI / AI Lead / Product Owner AI", TITLE_STYLE)

    contacts_line1 = Paragraph(
        "Москва &nbsp;·&nbsp; +7 (926) 276-61-43 &nbsp;·&nbsp; "
        '<a href="mailto:zubkovfpk@yandex.ru" color="#555555">zubkovfpk@yandex.ru</a>'
        " &nbsp;·&nbsp; Telegram: @SergeyAZubkov &nbsp;·&nbsp; "
        '<a href="https://www.linkedin.com/in/sergey-a-zubkov" color="#21a038">LinkedIn</a>',
        CONTACT_STYLE
    )
    contacts_line2 = Paragraph(
        "Желаемая позиция: Head of AI / Руководитель AI-направления "
        "&nbsp;·&nbsp; Формат: гибрид (Москва / Санкт-Петербург) "
        "&nbsp;·&nbsp; Командировки: да, включая международные "
        "&nbsp;·&nbsp; Зарплата: от 400 000 ₽ net",
        S("MetaLine", parent=CONTACT_STYLE, fontSize=7.5, textColor=HexColor("#777777"))
    )

    header_inner = Table(
        [[name_p], [title_p], [contacts_line1], [contacts_line2]],
        colWidths=[CONTENT_W]
    )
    header_inner.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 1),
        ("BOTTOMPADDING", (0,0),(-1,-1), 1),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
    ]))

    story.append(header_inner)
    story.append(HRFlowable(width="100%", thickness=3, color=GREEN,
                             spaceAfter=6, spaceBefore=4))
    return story


# ─── ОСНОВНОЕ СОДЕРЖИМОЕ ─────────────────────────────────────────────────────
def build_story() -> list:
    story = []

    # === ШАПКА ===
    story += build_header()

    # === ПРОФИЛЬ ===
    story += section_header("Профиль")
    story.append(Paragraph(
        "20+ лет в ИТ и цифровой трансформации, из них последние 9 лет — фокус на AI/ML-продукты "
        "и стратегию AI-направления. Co-Founder и CTO компании ВИЗАРД: выстроил AI-направление с нуля — "
        "от CustDev и валидации гипотез до запуска ML-продуктов в production и масштабирования "
        "на крупных корпоративных клиентов. Hands-on архитектор и разработчик: LLM, Agentic RAG, GraphRAG, "
        "multi-agent workflows, CV/ML. Умею работать в неопределённости, проектировать customer journey "
        "и переводить AI-возможности в измеримый бизнес-результат. "
        "Открыт к гибридному формату работы в Санкт-Петербурге.",
        BODY
    ))
    story.append(Spacer(1, 3))

    # Метрики
    story.append(metrics_row([
        ("9 лет",      "в AI/ML"),
        ("7",          "AI-продуктов в production"),
        ("100+",       "CustDev-интервью"),
        ("x2",         "доля AI в выручке"),
    ]))
    story.append(Spacer(1, 5))

    # === КЛЮЧЕВЫЕ КОМПЕТЕНЦИИ ===
    story += section_header("Ключевые компетенции")
    skill_cards = [
        ("AI/ML-продукты",
         "LLM, Agentic RAG, GraphRAG, multi-agent workflows. CV: YOLO/DETR/ViT. "
         "AI-product management: от гипотезы до production и масштабирования."),
        ("R&amp;D и валидация гипотез",
         "Исследование AI-рынка, генерация и проверка гипотез, запуск пилотов. "
         "Быстрое прототипирование, A/B-подход, оценка влияния на бизнес-метрики."),
        ("AI-стратегия",
         "Формирование стратегии AI-направления внутри компании. "
         "Дорожная карта, приоритизация, выстраивание AI-культуры в команде."),
        ("Продуктовое мышление",
         "Customer journey, CustDev, работа с гипотезами, CJM, приоритизация бэклога. "
         "Кросс-функциональные команды (продукт, маркетинг, e-commerce, аналитика)."),
        ("ML-инжиниринг (hands-on)",
         "Python, PyTorch, YOLO/EfficientDet/RT-DETR, SAHI, Raster Vision. "
         "CI/CD, Docker, Git/GitHub. Prompt-engineering, Constitutional AI, ADR."),
        ("Данные и интеграции",
         "PostgreSQL, Oracle, DWH. API-интеграции, корпоративные шины. "
         "Работа с неструктурированными и мультимодальными данными."),
    ]
    story.append(skills_grid(skill_cards))
    story.append(Spacer(1, 5))

    # === ОПЫТ РАБОТЫ ===
    story += section_header("Опыт работы")

    # --- РОСКАДАСТР ---
    story.append(KeepTogether(
        exp_header_with_tags(
            "Главный инженер / Enterprise Architect (консалтинговый проект)",
            "апр. 2025 — апр. 2026",
            "ППК «Роскадастр» — федеральный оператор пространственных данных РФ",
            ["Risk Management", "ML", "AI-агенты"]
        ) + [Spacer(1, 2)]
    ))
    roskad_bullets = [
        (highlight("ML и AI-направление:") +
         " ML-алгоритмы выявления изменений на местности по спутниковой съёмке; "
         "модель оценки операционных рисков (ISO 31000, P×S матрица, SORA/ARA); "
         "AI-агенты для планирования геодезических и картографических работ на федеральном уровне."),
        (highlight("Система управления рисками:") +
         " разработал полную архитектуру: quality gate на основе P×S матрицы, "
         "KRI-мониторинг near miss и операционных событий, визуализация risk map / heat map / value stream. "
         "COBIT-домены APO12, BAI01-03, DSS01-06, MEA01-02."),
        (highlight("KRI-результаты:") +
         " интегральный индекс качества пространственных данных >95%; "
         "коэффициент эффективности производственного планирования >90%; "
         "зрелость системы управления рисками — уровень 4 из 5 (продвинутый)."),
    ]
    for b in roskad_bullets:
        story.append(bullet(b))
    story.append(Spacer(1, 5))

    # --- ВИЗАРД ---
    vizard_kpi = kpi_box(
        "AI-результаты платформы VIZARD — измеримый бизнес-эффект",
        [
            ("120 → 200 сут.", "Эффект AI-оптимизации\nбуровых операций", "период эксплуатации ПБУ;\nснижение расходов до 35%"),
            ("+17% / +350 K $", "Ускорение маршрутов\n(СМП)", "ускорение прохода;\nэффект на один рейс"),
            ("1 млрд ₽+", "Совокупный эффект\nдля клиентов", "за 5+ лет;\n400+ суток применения в море"),
        ]
    )
    story.append(KeepTogether(
        exp_header_with_tags(
            "Co-Founder / CTO / Product Owner AI &amp; Data",
            "2017 — н.в.",
            "ВИЗАРД (VIZARD) — коммерческая платформа для морской логистики и мониторинга судоходства",
            ["AI-стратегия", "ML", "Product Owner / SBA"]
        ) + [Spacer(1, 2)] + vizard_kpi
    ))

    vizard_bullets = [
        (highlight("AI-направление с нуля:") +
         " исследовал рынок AI-решений в maritime/нефтегаз, формировал и валидировал гипотезы "
         "по матрице (метрика, инвестиции, вера, сложность, срок проверки, эффект, риск); "
         "запускал R&amp;D-проекты — от идеи до пилота и масштабирования на крупных клиентах "
         "(ПАО «Газпром», ПАО «Совкомфлот», ПАО «НОВАТЭК» и др.). 80+ протестированных гипотез."),
        (highlight("Customer journey и CustDev:") +
         " лично провёл и организовал 100+ интервью с капитанами, логистами, страховыми агентами "
         "(включая ОАЭ, Японию, Турцию, LinkedIn-сообщества). Сформировал текущий и целевой journey, "
         "выявил ключевые боли и точки создания ценности."),
        (highlight("AI-journey:") +
         " спроектировал сценарий, где пользователь формулирует задачу "
         "(«как пройти A→Б с минимальным риском/топливом»), а система на основе AI-аналитики "
         "предлагает оптимальные маршруты и предупреждения в мультимодальном интерфейсе."),
        (highlight("7 AI-продуктов в production:") +
         " модуль классификации льда, детекция для БПЛА (mAP@0.5 ≥ 80%), "
         "определение нефтяных загрязнений и их источника, модуль маршрутных рекомендаций, "
         "агент формирования гидрометеопрогнозов (Python, GFS/CMEMS, multi-agent AI). "
         "Плюс ML-алгоритмы в ЕГИП и Роскадастр."),
        (highlight("Рынок и финмодель:") +
         " выполнил анализ российского и международных рынков (PAM–TAM–SAM–SOM, "
         "сегмент P&amp;I-страхования Великобритании, БРИКС+, КСА); "
         "построил P&amp;L и финансовую модель с горизонтом 5 лет. "
         "Рост выручки x2 за первые 3 года."),
        (highlight("Кросс-функциональная работа:") +
         " команда до 17 человек (разработка, AI/ML, геоаналитика, бизнес-развитие); "
         "B2G / B2B / B2B2C. Переход на локальную инфраструктуру в условиях санкций "
         "без потери ценности для клиента."),
    ]
    for b in vizard_bullets:
        story.append(bullet(b))
    story.append(Spacer(1, 4))

    # --- ЕГИП ---
    story.append(KeepTogether(
        exp_header_with_tags(
            "Chief Architect / Product Owner / Customer Journey Lead",
            "2012 — 2016",
            "Единое геоинформационное пространство Москвы (ЕГИП) — Департамент информационных технологий г. Москвы",
            ["Цифр. трансформация", "Data-платформа", "Urban AI"]
        ) + [Spacer(1, 2)]
    ))
    egip_bullets = [
        (highlight("Customer journey B2G:") +
         " единая точка входа к пространственным данным вместо 30+ разрозненных систем — "
         "планирование рекламы и торговли, управление наследием и природными территориями, "
         "контроль подземных работ, мониторинг транспорта ЖКХ."),
        (highlight("Customer journey B2C:") +
         " Электронный атлас Москвы: где смотреть салют, где жарить шашлыки, какие перекрытия "
         "планируются, как работает медицина в районе. 200+ публичных слоёв, обновление за 30 минут."),
        (highlight("AI-journey и гипотезы:") +
         " 150+ интервью и семинаров с департаментами; проверялись сценарии сокращения выездов "
         "инспекторов (с 4 до 2 в год), онлайн-согласования CAD/BIM вместо флешек, "
         "снижение числа незаконных точек продажи алкоголя несовершеннолетним на 82%. "
         "ML первого поколения: детекция объектов на LiDAR + стереофото."),
        (highlight("Масштаб и экономика:") +
         " 60+ органов власти, 37 интегрированных систем. "
         "Снижение TCO в 6,3×; экономия бюджета >0,5 млрд руб./год. "
         "Лучшее интеграционное решение III Международного GIS-Forum, 2015."),
    ]
    for b in egip_bullets:
        story.append(bullet(b))
    story.append(Spacer(1, 4))

    # --- Ранний период ---
    story.append(KeepTogether([
        exp_header(
            "Инженер / Аналитик → И.о. начальника управления",
            "2004 — 2012"
        ),
        Paragraph(
            "Коммерческие ИТ/ГИС-организации: РЖД, CSoft, Прайм груп, Эверпоинт",
            EXP_COMPANY
        ),
        Spacer(1, 2),
    ]))
    story.append(bullet(
        "Последовательный карьерный рост от инженера до руководителя; "
        "hands-on работа с корпоративными данными, DWH, Oracle, ArcGIS."
    ))
    story.append(Spacer(1, 4))

    # === ТЕХНОЛОГИЧЕСКИЙ СТЕК ===
    story += section_header("Технологический стек")
    story.append(Paragraph(
        f"{bold('AI/ML:')} LLM, Agentic RAG, GraphRAG, multi-agent workflows, CV/YOLO/EfficientDet/DETR/RT-DETR/ViT, SAHI, Raster Vision &nbsp;·&nbsp; "
        f"{bold('Languages:')} Python (pytest, asyncio, APScheduler), SQL &nbsp;·&nbsp; "
        f"{bold('DB:')} PostgreSQL/PostGIS, Oracle &nbsp;·&nbsp; "
        f"{bold('DevOps:')} Docker, CI/CD, Git/GitHub &nbsp;·&nbsp; "
        f"{bold('Tools:')} Cursor, Windsurf, Perplexity, Notion, PlantUML &nbsp;·&nbsp; "
        f"{bold('Методологии:')} Lean Startup, A/B, PRINCE2, IPMA, TOGAF",
        STACK
    ))
    story.append(Spacer(1, 4))

    # === ОБРАЗОВАНИЕ ===
    story += section_header("Образование и сертификации")

    edu_items = [
        ("Дипломатическая академия МИД России", "Международные отношения", "2011"),
        ("МИИГАиК", "Прикладная космонавтика / Проектирование и внедрение ИС", "2006"),
        ("IPMA", "Сертификат управления проектами · № D0861", "2009"),
    ]

    edu_rows = []
    for org, fac, year in edu_items:
        left = Paragraph(
            f'{bold(org)} <font color="#888888" size="7.5">· {fac}</font>',
            S(f"EduLine_{org[:4]}", parent=BASE, fontSize=8, leading=11.5, textColor=MID)
        )
        right = Paragraph(year, S(f"EduYear_{year}", parent=BASE, fontSize=8,
                                   textColor=GREY, alignment=TA_RIGHT))
        edu_rows.append([left, right])

    edu_t = Table(edu_rows, colWidths=[CONTENT_W * 0.84, CONTENT_W * 0.16])
    edu_t.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 2),
        ("BOTTOMPADDING", (0,0),(-1,-1), 2),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story.append(edu_t)
    story.append(Spacer(1, 4))

    # === ПУБЛИЧНАЯ АКТИВНОСТЬ ===
    story += section_header("Публичная активность и признание")
    story.append(two_col_table(
        left_w=CONTENT_W * 0.43, right_w=CONTENT_W * 0.57,
        left_title="Спикер AI/tech-конференций",
        left_items=[
            "AI IN, Казань, 2023 — AI-направление",
            "Digital Innopolis Days, Казань, 2025",
            "Saudi Maritime Congress, Даммам, 2024",
            "RAO-CIS, Санкт-Петербург — регулярно с 2018 г.",
        ],
        right_title="Награды и экспертиза",
        right_items=[
            "2× победитель «АРКТЕК ИНЖИНИРИНГ», 2023",
            "Лауреат Российско-Китайского конкурса инноваций, 2023",
            "Член жюри AI &amp; Business Hackathon и 2ГИС Hackathon",
            "Член экспертного совета ИНТЦ МГУ «Воробьёвы горы»",
        ]
    ))
    story.append(Spacer(1, 4))

    # === МОТИВАЦИОННАЯ ПЛАШКА ===
    motive_text = (
        f"{bold('Почему я — для роли Head of AI:')} строил AI-направление с нуля в условиях реального рынка "
        "и санкционных ограничений — от исследования и гипотез до продуктов в production с измеримым "
        "бизнес-эффектом. Сочетаю стратегическое видение с hands-on экспертизой: сам пишу код, "
        "сам валидирую архитектуру. Умею работать в неопределённости и переводить AI-возможности "
        "на язык бизнес-метрик для любой аудитории — от разработчиков до собственников."
    )
    motive_p = Paragraph(motive_text, MOTIVE)
    motive_wrap = Table([[motive_p]], colWidths=[CONTENT_W])
    motive_wrap.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), BLUE_FAINT),
        ("LINEBEFORE",   (0,0),(0,-1),  4, GREEN),
        ("TOPPADDING",   (0,0),(-1,-1), 7),
        ("BOTTOMPADDING",(0,0),(-1,-1), 7),
        ("LEFTPADDING",  (0,0),(-1,-1), 10),
        ("RIGHTPADDING", (0,0),(-1,-1), 8),
    ]))
    story.append(motive_wrap)

    return story


# ─── КОЛОНТИТУЛ ───────────────────────────────────────────────────────────────
def footer(canvas_obj, doc):
    canvas_obj.saveState()
    canvas_obj.setFont("Inter", 7.5)
    canvas_obj.setFillColor(HexColor("#888888"))
    y = MB - 6*mm
    canvas_obj.drawString(ML, y, "С.А. Зубков  ·  Москва / Санкт-Петербург  ·  2026")
    canvas_obj.drawRightString(PAGE_W - MR, y, f"Стр. {doc.page}")
    canvas_obj.setStrokeColor(GREY_LIGHT)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(ML, y + 3*mm, PAGE_W - MR, y + 3*mm)
    canvas_obj.restoreState()


# ─── СБОРКА ───────────────────────────────────────────────────────────────────
def main():
    out_path = "/home/user/workspace/Zubkov_SA_Resume_HeadOfAI.pdf"

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=ML,
        rightMargin=MR,
        topMargin=MT,
        bottomMargin=MB,
        title="Зубков С.А. — Head of AI / AI Lead — Резюме 2026",
        author="Perplexity Computer",
    )

    story = build_story()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"✓ PDF сохранён: {out_path}")
    size = os.path.getsize(out_path)
    print(f"  Размер: {size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
