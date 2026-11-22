"""Offline PDF report generator for a manually queried public Roblox profile."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from xml.sax.saxutils import escape

from robloxdb_v2 import REPORTS

def write_profile_pdf(data):
    profile=data["profile"]
    user_id=int(profile["id"])
    REPORTS.mkdir(parents=True,exist_ok=True)
    path=REPORTS/f"profile-{user_id}.pdf"
    doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=40,leftMargin=40,topMargin=42,bottomMargin=42)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Brand", parent=styles["Title"],fontName="Helvetica-Bold",fontSize=19,leading=24,textColor=colors.HexColor("#2e45a3"),alignment=TA_LEFT))
    styles.add(ParagraphStyle(name="SmallTextCustom",parent=styles["BodyText"],leading=16,spaceAfter=7,wordWrap="CJK"))
    def text(value):
        return escape(str(value if value is not None else "Não disponível"))
    story=[Paragraph("ROBLOXDB  /  RELATÓRIO PÚBLICO",styles["Brand"]),Spacer(1,12),
           Paragraph("<b>"+text(profile.get("displayName"))+"</b>  @"+text(profile.get("name")),styles["Heading2"]),
           Paragraph("UserId: "+str(user_id),styles["BodyText"]),Spacer(1,12)]
    rows=[["Campo","Valor"],["Nome",profile.get("name")],["DisplayName",profile.get("displayName")],
          ["Criado",profile.get("created")]]
    for label,key in [("Amigos","friends"),("Seguidores","followers"),("Seguindo","following")]:
        rows.append([label,data.get("social_counts",{}).get(key)])
    table=Table([[Paragraph(text(x),styles["SmallTextCustom"]) for x in row] for row in rows],
                colWidths=[150,345],hAlign="LEFT")
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#dce5ff")),
                               ("GRID",(0,0),(-1,-1),.4,colors.HexColor("#cdd4e3")),
                               ("VALIGN",(0,0),(-1,-1),"TOP"),
                               ("LEFTPADDING",(0,0),(-1,-1),10)]))
    story.append(table)
    story.extend([Spacer(1,18),Paragraph("Descrição",styles["Heading2"]),
                  Paragraph(text(profile.get("description") or "Sem descrição pública."),styles["SmallTextCustom"]),
                  Spacer(1,10),Paragraph("Informações",styles["Heading2"])])
    for key,title in [("favorite_games","Favoritos"),("created_games","Jogos criados")]:
        games=data.get(key)
        if isinstance(games,list) and games:
            story.append(Paragraph(text(title)+": "+text(", ".join(str(g.get("name") or "Jogo") for g in games[:20])),styles["SmallTextCustom"]))
    story.extend([Spacer(1,15),
                  Paragraph("Consulta UTC: "+text(data.get("collected_at_utc")),styles["SmallTextCustom"]),
                  Paragraph("Dados públicos disponíveis no momento da coleta. Este relatório não comprova atividades nem identifica servidores privados.",styles["SmallTextCustom"])])
    doc.build(story)
    return path
