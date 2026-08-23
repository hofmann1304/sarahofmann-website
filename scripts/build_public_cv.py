from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "cv" / "CV_SaraHofmann.pdf"

ARIAL_REGULAR = Path(r"C:\Windows\Fonts\arial.ttf")
ARIAL_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")
if not ARIAL_REGULAR.exists() or not ARIAL_BOLD.exists():
    raise FileNotFoundError("Für den CV-Build werden Arial und Arial Bold aus C:\\Windows\\Fonts benötigt.")
pdfmetrics.registerFont(TTFont("Arial", str(ARIAL_REGULAR)))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(ARIAL_BOLD)))

NAVY = colors.HexColor("#253551")
BLUE = colors.HexColor("#31588A")
LIGHT_BLUE = colors.HexColor("#E8EEF4")
FOG = colors.HexColor("#F2F4F3")
TEXT = colors.HexColor("#20252C")
MUTED = colors.HexColor("#5B6470")
WHITE = colors.white

styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="BodyCV",
        parent=styles["BodyText"],
        fontName="Arial",
        fontSize=9.2,
        leading=12.3,
        textColor=TEXT,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        name="SectionCV",
        parent=styles["Heading2"],
        fontName="Arial-Bold",
        fontSize=12.5,
        leading=15,
        textColor=NAVY,
        spaceBefore=8,
        spaceAfter=6,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="RoleCV",
        parent=styles["Heading3"],
        fontName="Arial-Bold",
        fontSize=10.2,
        leading=12.5,
        textColor=TEXT,
        spaceAfter=1,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="MetaCV",
        parent=styles["BodyText"],
        fontName="Arial",
        fontSize=8.5,
        leading=10.5,
        textColor=MUTED,
        spaceAfter=3,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="SmallCV",
        parent=styles["BodyText"],
        fontName="Arial",
        fontSize=8.4,
        leading=11,
        textColor=TEXT,
    )
)
styles.add(
    ParagraphStyle(
        name="BulletMarkCV",
        parent=styles["BodyText"],
        fontName="Arial",
        fontSize=9.2,
        leading=12.3,
        textColor=BLUE,
        alignment=TA_CENTER,
    )
)
styles.add(
    ParagraphStyle(
        name="ContactCV",
        parent=styles["BodyText"],
        fontName="Arial",
        fontSize=9,
        leading=12,
        textColor=TEXT,
        alignment=TA_LEFT,
    )
)


def section(title: str):
    return Paragraph(title, styles["SectionCV"])


def bullet_list(items):
    table = Table(
        [[Paragraph("-", styles["BulletMarkCV"]), Paragraph(item, styles["BodyCV"])] for item in items],
        colWidths=[5 * mm, 164 * mm],
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return table


def experience(company, location, dates, role, bullets):
    heading = f"{company} - {location}" if location else company
    return KeepTogether(
        [
            Paragraph(heading, styles["RoleCV"]),
            Paragraph(f"{role} | {dates}", styles["MetaCV"]),
            bullet_list(bullets),
            Spacer(1, 3),
        ]
    )


def education(institution, dates, degree, focus):
    return KeepTogether(
        [
            Paragraph(institution, styles["RoleCV"]),
            Paragraph(dates, styles["MetaCV"]),
            Paragraph(f"<b>{degree}</b><br/>{focus}", styles["BodyCV"]),
            Spacer(1, 3),
        ]
    )


class CvDocTemplate(BaseDocTemplate):
    def afterInit(self):
        frame = Frame(
            18 * mm,
            16 * mm,
            A4[0] - 36 * mm,
            A4[1] - 46 * mm,
            id="body",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates(PageTemplate(id="cv", frames=[frame], onPage=draw_page))


def draw_page(canvas, doc):
    width, height = A4
    canvas.saveState()
    canvas.setTitle("Lebenslauf Sara Hofmann - öffentliche Fassung")
    canvas.setAuthor("Sara Hofmann")
    canvas.setSubject("Beruflicher Lebenslauf")
    canvas.setCreator("Sara Hofmann")

    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 26 * mm, width, 26 * mm, fill=1, stroke=0)
    if doc.page == 1:
        canvas.setFillColor(WHITE)
        canvas.setFont("Arial-Bold", 22)
        canvas.drawString(18 * mm, height - 13.5 * mm, "Sara Hofmann")
        canvas.setFont("Arial", 10.5)
        canvas.drawString(
            18 * mm,
            height - 20 * mm,
            "Industrial Engineer | Freelance Engineer & Consultant",
        )
    else:
        canvas.setFillColor(WHITE)
        canvas.setFont("Arial-Bold", 13)
        canvas.drawString(18 * mm, height - 16 * mm, "Sara Hofmann - Lebenslauf")

    canvas.setStrokeColor(LIGHT_BLUE)
    canvas.line(18 * mm, 13 * mm, width - 18 * mm, 13 * mm)
    canvas.setFont("Arial", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 8.5 * mm, "Öffentliche Fassung | Stand: August 2026")
    canvas.drawRightString(width - 18 * mm, 8.5 * mm, f"Seite {doc.page}")
    canvas.restoreState()


def build_story():
    story = []

    story.append(section("Profil"))
    story.append(
        Paragraph(
            "Industrial Engineer mit Schwerpunkt Produktion und Entwicklung sowie Masterstudentin "
            "im Bereich Systems Engineering Mechatronik. Ich verbinde technisches Fachwissen, "
            "Datenanalyse und interdisziplinäres Denken. Meine Schwerpunkte liegen in analytischer "
            "Problemlösung, Prozessoptimierung, technischer Dokumentation und Wissensvermittlung.",
            styles["BodyCV"],
        )
    )
    story.append(Spacer(1, 5))

    contact = Paragraph(
        '<b>Kontakt</b><br/>'
        '<link href="mailto:hofmann1304@gmail.com" color="#31588A">hofmann1304@gmail.com</link><br/>'
        '<link href="https://sarahofmann.de" color="#31588A">sarahofmann.de</link>',
        styles["ContactCV"],
    )
    skills = Paragraph(
        "<b>Fachliche Schwerpunkte</b><br/>"
        "MATLAB und technische Datenanalyse<br/>"
        "Prozessoptimierung und Dokumentation<br/>"
        "Robotik, Automatisierung und 3D-Druck<br/>"
        "Lehrmaterialien und Wissensvermittlung",
        styles["ContactCV"],
    )
    info = Table([[contact, skills]], colWidths=[65 * mm, 104 * mm], hAlign="LEFT")
    info.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), FOG),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D3DBE3")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D3DBE3")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.extend([info, Spacer(1, 7), section("Berufserfahrung")])

    story.append(
        experience(
            "Carl Zeiss Jena GmbH",
            "Oberkochen",
            "04/2024 - heute",
            "Werkstudentin",
            [
                "Durchführung und Auswertung von Datenanalysen mit MATLAB",
                "Dokumentation von Projektergebnissen und Prozessen sowie Optimierung technischer Berichte",
                "Entwicklung und Validierung robotikbezogener Konzepte",
                "3D-Druck mit Bambu Lab einschließlich Druckvorbereitung und Qualitätssicherung",
                "Unterstützung in Automatisierungs- und Additive-Fertigung-Projekten",
            ],
        )
    )
    story.append(
        experience(
            "Beratung Sara Hofmann",
            "",
            "05/2022 - heute",
            "Freelance Engineer & Consultant",
            [
                "Unterstützung bei Prozessoptimierung, Datenanalyse und technischen Lösungen",
                "Interdisziplinäre Bearbeitung technischer und wirtschaftlicher Fragestellungen",
                "Erstellung und Optimierung von Lehr- und Präsentationsmaterialien",
            ],
        )
    )
    story.append(
        experience(
            "Weeber Event GmbH",
            "",
            "09/2019 - 02/2024",
            "Küchen- und Servicepersonal",
            [
                "Betreuung und Bedienung von Gästen sowie Zubereitung und Servieren von Speisen und Getränken",
                "Sicherstellung reibungsloser Abläufe und professioneller Kundenbetreuung",
            ],
        )
    )
    story.append(
        experience(
            "MAPAL Dr. Kress KG",
            "",
            "09/2021 - 02/2022",
            "Praktikantin Ingenieurwesen",
            [
                "Rotations- und 3D-Scans von Werkzeugen",
                "Untersuchung von Kantenverrundung, Frei-, Span- und Keilwinkeln sowie Kerndurchmessern",
                "Verschleiß- und Differenzmessungen an Scan-Dateien",
                "Rauheits- und Oberflächenmessungen mit Zeiss Surfcom und MAPAL Uniscal-M",
            ],
        )
    )

    story.append(PageBreak())
    story.append(section("Berufserfahrung - Fortsetzung"))
    story.append(
        experience(
            "Hochschule Aalen",
            "",
            "09/2020 - 08/2021",
            "Wissenschaftliche Hilfskraft",
            [
                "Einlesen, Bereinigen und Transformieren von Stamm- und Leistungsdaten in MATLAB",
                "Visualisierung mit Methoden der deskriptiven Statistik",
                "Berechnung von Kennzahlen, Zusammenhangsmaßen und statistischen Testverfahren",
                "Dokumentation, Wochenberichte und Präsentation der Ergebnisse",
            ],
        )
    )
    story.append(
        experience(
            "MAPAL Dr. Kress KG",
            "",
            "07/2020 - 08/2020",
            "Praktikantin",
            [
                "Manuelle und maschinelle Bearbeitungsverfahren, Systemwartung und Messtechnik",
                "Bohren, Reiben, Gewindeschneiden, Drehen, Fräsen, Biegen und Hartlöten",
            ],
        )
    )
    story.append(
        experience(
            "MAPAL Dr. Kress KG",
            "",
            "07/2019 - 09/2019 und 08/2018",
            "Ferienbeschäftigung",
            ["Unterstützung in betrieblichen und produktionsnahen Tätigkeiten"],
        )
    )

    story.append(section("Ausbildung"))
    story.append(
        education(
            "Hochschule Aalen",
            "03/2024 - heute",
            "Master of Engineering",
            "Mechatronics, Systems Engineering",
        )
    )
    story.append(
        education(
            "Hochschule Aalen",
            "09/2019 - 08/2023",
            "Bachelor of Engineering",
            "Industrial Engineering - Produktion und Entwicklung",
        )
    )

    return story


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = CvDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        title="Lebenslauf Sara Hofmann - öffentliche Fassung",
        author="Sara Hofmann",
        subject="Beruflicher Lebenslauf",
        creator="Sara Hofmann",
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=30 * mm,
        bottomMargin=16 * mm,
    )
    doc.afterInit()
    doc.build(build_story())
    print(OUTPUT)


if __name__ == "__main__":
    main()
