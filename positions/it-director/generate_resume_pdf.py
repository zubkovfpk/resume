#!/usr/bin/env python3
"""
Генерация PDF-резюме: Зубков С.А. — IT-директор / CTO
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
MT = 10*mm                   # верхний (уменьшен для компактности)
MB = 12*mm                   # нижний
CONTENT_W = PAGE_W - ML - MR # 559 pt ≈ 197 mm

# ─── Стили текста ─────────────────────────────────────────────────────────────
def S(name, **kw):
    base = kw.pop("parent", None)
    return ParagraphStyle(name, parent=base, **kw)

# Базовый
BASE = S("Base", fontName="Inter", fontSize=8, leading=11.5,
         textColor=MID, spaceAfter=0, spaceBefore=0)

# Имя
NAME_STYLE = S("Name", parent=BASE, fontName="Inter-Bold",
               fontSize=20, leading=24, textColor=DARK)

# Должность
TITLE_STYLE = S("Title", parent=BASE, fontName="Inter-Semi",
                fontSize=10, leading=13, textColor=GREEN, spaceAfter=3)

# Контакты
CONTACT_STYLE = S("Contact", parent=BASE, fontSize=8, leading=11, textColor=GREY)

# Заголовок секции
SECTION_TITLE = S("SecTitle", parent=BASE, fontName="Inter-Bold",
                  fontSize=10, leading=12.5, textColor=GREEN,
                  spaceBefore=5, spaceAfter=2)

# Тело
BODY = S("Body", parent=BASE, fontSize=8, leading=11.5,
         textColor=MID, spaceAfter=3)

# Подзаголовок опыта
EXP_TITLE = S("ExpTitle", parent=BASE, fontName="Inter-Bold",
              fontSize=9, leading=11.5, textColor=DARK)

# Компания
EXP_COMPANY = S("ExpCompany", parent=BASE, fontName="Inter-Semi",
                fontSize=8, leading=10.5, textColor=GREEN, spaceAfter=2)

# Суброль
EXP_ROLE = S("ExpRole", parent=BASE, fontSize=8, leading=11, textColor=GREY)

# Буллет
BULLET = S("Bullet", parent=BASE, fontSize=8, leading=11.5,
           leftIndent=10, firstLineIndent=-10, textColor=MID, spaceAfter=1.5)

# Маленький
SMALL = S("Small", parent=BASE, fontSize=7.5, leading=10.5, textColor=GREY)

# KPI-значение
KPI_VAL = S("KPIVal", parent=BASE, fontName="Inter-Bold",
            fontSize=9, leading=11.5, textColor=GREEN, alignment=TA_CENTER)

# KPI-подпись
KPI_NAME = S("KPIName", parent=BASE, fontSize=7, leading=9.5,
             textColor=GREY, alignment=TA_CENTER)

# KPI-статус
KPI_STATUS = S("KPIStatus", parent=BASE, fontSize=7, leading=9.5,
               textColor=GREY, alignment=TA_CENTER)

# Стек
STACK = S("Stack", parent=BASE, fontSize=7.5, leading=11, textColor=MID)

# Мотивационная плашка
MOTIVE = S("Motive", parent=BASE, fontSize=8, leading=11.5,
           textColor=DARK, leftIndent=8)


# ─── Вспомогательные классы ───────────────────────────────────────────────────

class GreenLeftBar(Flowable):
    """Вертикальная зелёная полоса слева у skill-карточки."""
    def __init__(self, width, height):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def draw(self):
        self.canv.setFillColor(GREEN)
        self.canv.rect(0, 0, 3, self.height, stroke=0, fill=1)


def colored_rule():
    return HRFlowable(width="100%", thickness=1.5, color=GREEN_LIGHT,
                      spaceAfter=4, spaceBefore=0)


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
    role_p  = Paragraph(role,   EXP_TITLE)
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
    """items = [(value, name, status), ...]"""
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
    """Рамка с заголовком + KPI-таблица — полная ширина без смещения."""
    PAD = 6  # горизонтальный padding ячейки
    inner_w = CONTENT_W - PAD * 2  # ширина внутренней KPI-таблицы

    title_p = Paragraph(title, S("KPIBoxTitle", parent=BASE, fontName="Inter-Bold",
                                  fontSize=8.5, textColor=GREEN, alignment=TA_CENTER))
    kpi_t = kpi_table(items, inner_w=inner_w)

    # Единая таблица: заголовок + KPI-строка
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
    """cards = [(title, body), ...] — 3 колонки, выровненные по высоте строки"""
    col_w = (CONTENT_W - 4) / 3  # 4pt зазор суммарно

    def card(title, body):
        title_p = Paragraph(title, S("SkTitle", parent=BASE, fontName="Inter-Bold",
                                      fontSize=8.5, textColor=DARK, spaceAfter=2))
        body_p  = Paragraph(body,  S("SkBody",  parent=BASE, fontSize=7.5,
                                      textColor=HexColor("#444444"), leading=11))
        return [title_p, body_p]

    # Разбиваем карточки на строки по 3
    rows_data = []
    for i in range(0, len(cards), 3):
        row_cards = cards[i:i+3]
        while len(row_cards) < 3:
            row_cards.append(("", ""))
        rows_data.append(row_cards)

    # Строим таблицу: каждая строка = одна строка таблицы с тремя ячейками
    # Каждая ячейка содержит заголовок + тело (вертикально)
    all_rows = []
    for row_cards in rows_data:
        # Строка заголовков
        title_row = [
            Paragraph(t, S(f"SkT{i}", parent=BASE, fontName="Inter-Bold",
                           fontSize=8.5, textColor=DARK, spaceAfter=1))
            for i, (t, _) in enumerate(row_cards)
        ]
        # Строка тел
        body_row = [
            Paragraph(b, S(f"SkB{i}", parent=BASE, fontSize=7.5,
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
        # Фон строк (каждые 2 строки = одна карточка)
    ]

    # Фон и левая полоска для каждой пары строк (заголовок + тело)
    num_card_rows = len(rows_data)
    for ri in range(num_card_rows):
        r0 = ri * 2       # строка заголовков
        r1 = ri * 2 + 1   # строка тел
        style_cmds += [
            ("BACKGROUND",  (0,r0), (-1,r1), SKILL_BG),
            ("SPAN",        (0,r0), (0,r1)),   # не спан, а визуальное объединение через padding
        ]
        # Полоска слева для каждой колонки
        for ci in range(3):
            style_cmds.append(("LINEBEFORE", (ci,r0), (ci,r1), 3, GREEN))
        # Нижний отступ между карточками (после строки тела)
        if ri < num_card_rows - 1:
            style_cmds.append(("BOTTOMPADDING", (0,r1), (-1,r1), 5))

    # Убираем SPAN — вместо него увеличим toppadding заголовков
    style_cmds_clean = [c for c in style_cmds if c[0] != "SPAN"]

    # Заголовки: больший верхний отступ
    for ri in range(num_card_rows):
        r0 = ri * 2
        style_cmds_clean.append(("TOPPADDING", (0,r0), (-1,r0), 5))
        style_cmds_clean.append(("BOTTOMPADDING", (0,r0), (-1,r0), 1))

    t.setStyle(TableStyle(style_cmds_clean))
    return t


# ─── Метрики-бейджи ───────────────────────────────────────────────────────────
def metrics_row(items: list) -> Table:
    """items = [(value, label), ...]"""
    col_w = CONTENT_W / len(items)
    cells = []
    for val, lbl in items:
        v = Paragraph(val, S("MVal", parent=BASE, fontName="Inter-Bold",
                              fontSize=12, textColor=GREEN, alignment=TA_CENTER))
        l = Paragraph(lbl.upper(), S("MLbl", parent=BASE, fontSize=6.5,
                                      textColor=GREY, alignment=TA_CENTER,
                                      leading=9))
        cells.append([v, l])

    # Транспонируем: одна строка с ячейками
    row_vals  = [c[0] for c in cells]
    row_lbls  = [c[1] for c in cells]
    t = Table([row_vals, row_lbls], colWidths=[col_w]*len(items))
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), GREEN_LIGHT),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
        ("INNERGRID",     (0,0),(-1,-1), 0.5, white),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), [3,3,3,3]),
    ]))
    return t


# ─── Теги в строку (без фона, цветным текстом) ────────────────────────────────
def tag_line(labels: list) -> Paragraph:
    """Компактные теги без фона — цветной текст через · разделитель."""
    parts = [f'<font color="#21a038" name="Inter-Semi">{lbl}</font>' for lbl in labels]
    joined = ' <font color="#aaaaaa">·</font> '.join(parts)
    return Paragraph(joined, S("TagLine", parent=BASE, fontSize=7.5, leading=11,
                               textColor=GREEN, spaceAfter=3))


# ─── Строка опыта с тегами ────────────────────────────────────────────────────
def exp_header_with_tags(role: str, period: str, company: str, tags: list) -> list:
    """Заголовок роли + теги в одну строку, компания отдельно."""
    role_p = Paragraph(role, EXP_TITLE)
    period_p = Paragraph(period, S("Period2", parent=BASE, fontSize=8,
                                    textColor=GREY, alignment=TA_RIGHT))
    header_t = Table([[role_p, period_p]],
                     colWidths=[CONTENT_W * 0.72, CONTENT_W * 0.28])
    header_t.setStyle(TableStyle([
        ("VALIGN",  (0,0), (-1,-1), "BOTTOM"),
        ("PADDING", (0,0), (-1,-1), 0),
    ]))
    company_p = Paragraph(company, EXP_COMPANY)
    tags_p = tag_line(tags)
    return [header_t, company_p, tags_p]


# ─── Двухколоночная таблица ───────────────────────────────────────────────────
def two_col_table(left_items, right_items, left_title, right_title) -> Table:
    half = (CONTENT_W - 4*mm) / 2

    def col_content(title, items):
        parts = [Paragraph(bold(title), S("ColTitle", parent=BASE, fontName="Inter-Bold",
                                           fontSize=8.5, textColor=DARK, spaceAfter=3))]
        for item in items:
            parts.append(bullet(item))
        return parts

    left  = col_content(left_title,  left_items)
    right = col_content(right_title, right_items)

    # Упаковываем в ячейки
    def wrap(parts):
        t = Table([[p] for p in parts], colWidths=[half])
        t.setStyle(TableStyle([
            ("LEFTPADDING",  (0,0),(-1,-1), 0),
            ("RIGHTPADDING", (0,0),(-1,-1), 0),
            ("TOPPADDING",   (0,0),(-1,-1), 0),
            ("BOTTOMPADDING",(0,0),(-1,-1), 1),
        ]))
        return t

    outer = Table([[wrap(left), wrap(right)]], colWidths=[half, half])
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

    # Строка с именем и должностью
    name_p  = Paragraph("Зубков Сергей Андреевич", NAME_STYLE)
    title_p = Paragraph("IT-директор / CTO / Chief AI Officer",
                         TITLE_STYLE)

    contacts_line1 = Paragraph(
        "Москва &nbsp;·&nbsp; +7 (926) 276-61-43 &nbsp;·&nbsp; "
        '<a href="mailto:zubkovfpk@yandex.ru" color="#555555">zubkovfpk@yandex.ru</a>'
        " &nbsp;·&nbsp; Telegram: @SergeyAZubkov &nbsp;·&nbsp; "
        '<a href="https://www.linkedin.com/in/sergey-a-zubkov" color="#21a038">LinkedIn</a>',
        CONTACT_STYLE
    )
    contacts_line2 = Paragraph(
        "Желаемая позиция: IT Директор &nbsp;·&nbsp; Зарплата: от 700 000 ₽ net "
        "&nbsp;·&nbsp; Формат: любой &nbsp;·&nbsp; Командировки: да, в т.ч. международные "
        "&nbsp;·&nbsp; Релокация: с осени 2027",
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


# ─── ОСНОВНОЕ СОДЕРЖИМОЕ ──────────────────────────────────────────────────────
def build_story() -> list:
    story = []

    # === ШАПКА ===
    story += build_header()

    # === ПРОФИЛЬ ===
    story += section_header("Профиль")
    story.append(Paragraph(
        "20+ лет опыта в ИТ, ГИС и цифровой трансформации. Co-Founder и CTO компании ВИЗАРД "
        "(продукт VIZARD — в реестре отечественного ПО). Выстраиваю ИТ-стратегию под цели бизнеса, "
        "управляю ИТ-инфраструктурой и портфелем проектов цифровой трансформации, встраиваю контур "
        "информационной безопасности, отвечаю за бюджет направления и отчётность перед собственниками "
        "и руководством. Руководил командами 50+ человек, проектами от 10 млн до ~900 млн руб. "
        "Сохраняю hands-on экспертизу в современных стеках (Python, СУБД, ML, CI/CD, multi-agent AI).",
        BODY
    ))
    story.append(Spacer(1, 3))

    # Метрики
    story.append(metrics_row([
        ("20+",        "лет в ИТ / ГИС"),
        ("50+",        "пик команды"),
        ("~900 млн ₽", "масштаб портфелей"),
        ("2 распоряжения",  "Правительства РФ"),
    ]))
    story.append(Spacer(1, 5))

    # === КЛЮЧЕВЫЕ КОМПЕТЕНЦИИ ===
    story += section_header("Ключевые компетенции")
    skill_cards = [
        ("ИТ-стратегия и архитектура",
         "Формирование и реализация ИТ-стратегии, Enterprise / Solution Architecture, "
         "архитектурные решения и ADR. TOGAF, COBIT, PRINCE2, IPMA."),
        ("Цифровая трансформация",
         "Программы и портфели проектов «от концепции до эксплуатации», управление изменениями. "
         "Опыт в госсекторе и корпорациях."),
        ("GenAI и AI-продукты",
         "LLM, Agentic RAG, GraphRAG, multi-agent workflows. Hands-on: модуль метеобюллетеня, "
         "ML-детекция по БПЛА (mAP@0.5 ≥ 80%)."),
        ("ИТ-инфраструктура и DevOps",
         "Серверная, сетевая, БД и облачная составляющие. Observability, CI/CD, Docker, Git/GitHub. "
         "Работа в условиях импортозамещения."),
        ("ИБ и риск-менеджмент",
         "Встраивание контура ИБ в цифровые продукты и процессы. "
         "ISO 31000, FMEA, SORA. Взаимодействие с ИБ-подразделениями заказчиков."),
        ("Команды и бюджет",
         "Управление кросс-функциональными командами (пик 50+, 20+ прямого подчинения). "
         "Формирование и защита ИТ-бюджета, отчётность перед собственниками."),
        ("ГИС / Urban AI / ДЗЗ",
         "ArcGIS, QGIS, PostGIS. NetCDF, GeoTIFF, GRIB2. "
         "Метеоданные: GFS, CMEMS, ERA5. Пространственные БД, картография, ДЗЗ."),
        ("Данные и интеграции",
         "СУБД (PostgreSQL, Oracle), DWH, интеграционные шины. Python, SQL. "
         "API-платформы, корпоративные интеграции."),
        ("Госзакупки / контрактинг",
         "44-ФЗ / 223-ФЗ: организация закупок по ЕГИП (сторона заказчика) "
         "и 10+ конкурсов (сторона участника)."),
    ]
    story.append(skills_grid(skill_cards))
    story.append(Spacer(1, 5))

    # === ОПЫТ РАБОТЫ ===
    story += section_header("Опыт работы")

    # --- ВИЗАРД ---
    # Шапка + KPI сразу (KeepTogether), потом детали
    vizard_kpi = kpi_box(
        "VIZARD — ключевые результаты платформы",
        [
            ("120 → 200 сут.", "Эффект для буровых операций", "период эксплуатации ПБУ;\nснижение расходов до 35%"),
            ("+17% / +350 K $", "Ускорение СМП", "ускорение прохода основного плеча;\nэффект на проход"),
            ("1 млрд ₽+", "Совокупная экономия клиентов", "за 5+ лет на рынке;\n400+ суток применения в море"),
        ]
    )
    story.append(KeepTogether(
        exp_header_with_tags(
            "Co-Founder / CTO / SBA / Product Owner AI & Data",
            "2017 — н.в.",
            "ВИЗАРД (VIZARD) — коммерческая платформа для морской логистики и мониторинга судоходства",
            ["ИТ-стратегия", "ML", "Product Owner / SBA"]
        ) + [Spacer(1, 2)] + vizard_kpi
    ))

    vizard_bullets = [
        (highlight("Общее техническое руководство:") +
         " ИТ-стратегия, архитектура платформы, продуктовая линейка, AI-направление. "
         "Управление портфелем проектов «от концепции до эксплуатации»; бюджет направления; "
         "отчётность перед собственниками."),
        (highlight("Команда и масштаб:") +
         " рост команды с 3 до 17 человек (2020–2023); "
         "взаимодействие с клиентами B2G / B2B / B2B2C — нефтегаз, морские перевозки, страхование, рыболовство."),
        (highlight("AI-направление:") +
         " запуск и развитие: ML-продукты (CV/YOLO/DETR, детекция, классификация), LLM, Agentic RAG / GraphRAG, multi-agent workflows, AI-product management. "
         "Переход на локальную инфраструктуру в условиях санкций без потери ценности для клиента."),
        (highlight("Результаты:") +
         " продукт VIZARD в реестре отечественного ПО; ВИЗАРД в реестрах ИТ-компаний, МТК, "
         "инновационных компаний Москвы."),
        (highlight("Hands-on (метеобюллетень):") +
         " лично спроектировал и развиваю AI-driven модуль подготовки гидрометеорологических бюллетеней "
         "(Python, NetCDF/GRIB2, GFS/CMEMS, multi-agent AI, CI/CD). Репозиторий GitHub — по запросу."),
        (highlight("Hands-on (ML / БПЛА):") +
         " ML-пайплайн детекции сорных растений для Россельхознадзора по данным БПЛА "
         "(YOLO/EfficientDet/DETR/RT-DETR; mAP@0.5 ≥ 80%, IoU ≥ 0.75, F1 ≥ 0.8). MVP сдан заказчику."),
    ]
    for b in vizard_bullets:
        story.append(bullet(b))
    story.append(Spacer(1, 4))

    # --- ЕГИП ---
    # Шапка + KPI сразу (KeepTogether), потом детали
    egip_kpi = kpi_box(
        "ЕГИП Москвы — ключевые результаты программы",
        [
            ("60+ / 37", "Консолидация данных\nи стейкхолдеров", "органов власти /\nинтегрированных систем"),
            ("6,3× / 0,5 млрд ₽", "Экономический\nэффект для города", "снижение TCO /\nежегодная экономия"),
            ("200+ / 30 мин", "Сервис для жителей\nи бизнеса", "публичных слоёв /\nобновление данных"),
        ]
    )
    story.append(KeepTogether(
        exp_header_with_tags(
            "Chief Architect / Scenario Business Architect (B2G / B2B / B2C)",
            "2012 — 2016",
            "Единое геоинформационное пространство Москвы (ЕГИП) — Департамент информационных технологий г. Москвы",
            ["Цифровая трансформация", "Госсектор", "Urban AI"]
        ) + [Spacer(1, 2)] + egip_kpi
    ))

    egip_bullets = [
        (highlight("Масштаб программы:") +
         " 60+ органов исполнительной власти г. Москвы, 37 интегрированных корпоративных "
         "и ведомственных систем, 100+ наборов пространственных данных; срок реализации — 3 года."),
        (highlight("ИТ-архитектура:") +
         " единая платформа пространственных данных (B2G / B2C / B2B), 3D + LiDAR, стереофото, "
         "CAD/BIM; интеграция через корпоративные шины; реляционные и пространственные БД."),
        (highlight("Регуляторика:") +
         " фактически сформировал Подкомиссию по вопросам пространственных данных Правкомиссии по ИКТ; "
         "авторство проектов двух утверждённых Распоряжений Правительства РФ."),
        (highlight("Закупочная деятельность:") +
         " организация всей закупочной деятельности по программе ЕГИП "
         "со стороны государственного заказчика (44-ФЗ / 223-ФЗ)."),
        (highlight("Результаты:") +
         " снижение TCO в 6,3×; экономия бюджета >0,5 млрд руб./год; "
         "200+ публичных картослоёв; обновление официальных данных в течение 30 минут."),
    ]
    for b in egip_bullets:
        story.append(bullet(b))
    story.append(Spacer(1, 3))

    # --- Ранний период ---
    story.append(KeepTogether([
        exp_header(
            "Инженер / Аналитик / ГИС-специалист → И.о. начальника управления",
            "2004 — 2012"
        ),
        Paragraph(
            "Коммерческие ИТ/ГИС-организации: РЖД, CSoft, Прайм груп, Эверпоинт",
            EXP_COMPANY
        ),
        Spacer(1, 2),
    ]))
    story.append(bullet(
        "Последовательный карьерный рост от инженера/аналитика/ГИС-специалиста "
        "до и.о. начальника управления."
    ))
    story.append(bullet(
        "Hands-on работа с корпоративными ГИС и БД: Oracle Database 10g, ArcGIS; "
        "DWH / data-платформы; участие в проектах CAD/BIM."
    ))
    story.append(Spacer(1, 4))

    # === ТЕХНОЛОГИЧЕСКИЙ СТЕК ===
    story += section_header("Технологический стек")
    story.append(Paragraph(
        f"{bold('AI/ML:')} LLM, Agentic RAG, GraphRAG, multi-agent workflows, CV/YOLO/DETR/ViT, SAHI, Raster Vision &nbsp;·&nbsp; "
        f"{bold('Languages:')} Python (pytest, asyncio, APScheduler), SQL &nbsp;·&nbsp; "
        f"{bold('DB:')} PostgreSQL/PostGIS, Oracle &nbsp;·&nbsp; "
        f"{bold('GIS/RS:')} ArcGIS, QGIS, NetCDF, GRIB2, GeoTIFF &nbsp;·&nbsp; "
        f"{bold('Метеоданные:')} GFS, CMEMS, ERA5, NOAA &nbsp;·&nbsp; "
        f"{bold('DevOps:')} Docker, CI/CD, Git/GitHub &nbsp;·&nbsp; "
        f"{bold('Методологии:')} TOGAF, COBIT, PRINCE2, IPMA, ISO 31000, FMEA, SORA &nbsp;·&nbsp; "
        f"{bold('Tools:')} Cursor, Windsurf, Perplexity, Notion, PlantUML",
        STACK
    ))
    story.append(Spacer(1, 4))

    # === ОБРАЗОВАНИЕ ===
    story += section_header("Образование и сертификации")

    # Компактный формат: организация · факультет · год — всё в одну строку
    edu_items = [
        ("Дипломатическая академия МИД России", "Факультет «Международные отношения»", "2011"),
        ("МИИГАиК", "Факультет «Прикладная космонавтика» / Проектирование и внедрение ИС", "2006"),
        ("IPMA", "Сертификат управления проектами · № D0861", "2009"),
    ]

    edu_rows = []
    for org, fac, year in edu_items:
        left = Paragraph(
            f'{bold(org)} <font color="#888888" size="7.5">· {fac}</font>',
            S("EduLine", parent=BASE, fontSize=8, leading=11.5, textColor=MID)
        )
        right = Paragraph(year, S("EduYear", parent=BASE, fontSize=8,
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

    # === ПУБЛИЧНАЯ АКТИВНОСТЬ И НАГРАДЫ ===
    story += section_header("Публичная активность и награды")
    story.append(two_col_table(
        left_title="Спикер конференций",
        left_items=[
            "RAO‑CIS (Санкт-Петербург) — регулярно с 2018 г.",
            "AI IN, Казань, 2023",
            "Saudi Maritime Congress, Даммам, 2024",
            "Digital Innopolis Days, Казань, 2025",
        ],
        right_title="Награды и признание",
        right_items=[
            "Благодарность Мэра Москвы, 2015",
            "III GIS-Forum — лучшее интеграционное решение, 2015",
            "2х победитель «АРКТЕК ИНЖИНИРИНГ», 2023",
            "Лауреат Российско-Китайского конкурса инноваций, 2023",
            "Член жюри AI & Business Hackathon и 2ГИС Hackathon",
            "Член экспертного совета ИНТЦ МГУ «Воробьёвы горы»",
        ]
    ))
    story.append(Spacer(1, 4))

    # === МОТИВАЦИОННАЯ ПЛАШКА ===
    motive_text = (
        f"{bold('Почему я — для роли IT-директора / CTO:')} совмещаю стратегическое управление "
        "(ИТ-стратегия, бюджет, команды 50+, программы цифровой трансформации в госсекторе и бизнесе) "
        "с подтверждённой hands-on экспертизой в современных стеках — Python, multi-agent AI, ML, CI/CD. "
        "Умею говорить на языке бизнеса и на языке технологий одновременно: от формирования "
        "архитектурных решений и ADR до защиты ИТ-бюджета перед собственниками. "
        "Продукт VIZARD в реестре отечественного ПО, два Распоряжения Правительства РФ "
        "и >1 млрд ₽ экономии клиентов VIZARD — подтверждения масштаба и результативности."
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
    canvas_obj.drawString(ML, y, "С.А. Зубков  ·  Москва  ·  2026")
    canvas_obj.drawRightString(PAGE_W - MR, y, f"Стр. {doc.page}")
    # Линия
    canvas_obj.setStrokeColor(GREY_LIGHT)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(ML, y + 3*mm, PAGE_W - MR, y + 3*mm)
    canvas_obj.restoreState()


# ─── СБОРКА ───────────────────────────────────────────────────────────────────
def main():
    out_path = "/home/user/workspace/Zubkov_SA_Resume_IT-Director.pdf"

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=ML,
        rightMargin=MR,
        topMargin=MT,
        bottomMargin=MB,
        title="Зубков С.А. — IT-директор / CTO — Резюме 2026",
        author="Perplexity Computer",
    )

    story = build_story()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"✓ PDF сохранён: {out_path}")
    size = os.path.getsize(out_path)
    print(f"  Размер: {size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
