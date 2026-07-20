"""Gera holerites ficticios (Recibo de Pagamento de Salario) para teste."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

MESES = ["JANEIRO", "FEVEREIRO", "MARCO", "ABRIL", "MAIO", "JUNHO",
         "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]


def gerar_holerite(path, ano, mes, pagamento, admissao,
                   comp_style="num", nome="MARIA S. OLIVEIRA"):
    c = canvas.Canvas(path, pagesize=A4)
    w, h = A4
    y = h - 25 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20 * mm, y, "NITATORI ADVOGADOS ASSOCIADOS")
    c.setFont("Helvetica", 8)
    c.drawString(20 * mm, y - 5 * mm, "CNPJ: 12.345.678/0001-90")
    c.drawRightString(w - 20 * mm, y, "Recibo de Pagamento de Salario")

    y -= 18 * mm
    c.setFont("Helvetica", 9)
    if comp_style == "num":
        comp_txt = f"Competencia: {mes:02d}/{ano}"
    elif comp_style == "mesnome":
        comp_txt = f"Referencia: {MESES[mes - 1]}/{ano}"
    else:
        comp_txt = f"Mes/Ano: {MESES[mes - 1].capitalize()} de {ano}"
    c.drawString(20 * mm, y, comp_txt)

    y -= 10 * mm
    c.drawString(20 * mm, y, f"Nome: {nome}")
    c.drawString(120 * mm, y, "CPF: 123.456.789-00")
    y -= 6 * mm
    c.drawString(20 * mm, y, "Cargo: Assistente Juridico")
    c.drawString(120 * mm, y, f"Admissao: {admissao}")

    y -= 12 * mm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(20 * mm, y, "Descricao")
    c.drawString(120 * mm, y, "Vencimentos")
    c.setFont("Helvetica", 9)
    for desc, v in [("Salario base", "3.500,00"), ("INSS", ""), ("IRRF", "")]:
        y -= 6 * mm
        c.drawString(20 * mm, y, desc)
        if v:
            c.drawString(120 * mm, y, v)

    y -= 12 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "Liquido a Receber: R$ 3.017,50")

    y -= 20 * mm
    c.setFont("Helvetica", 9)
    c.drawString(20 * mm, y, f"Sao Paulo, {pagamento}")
    c.save()
