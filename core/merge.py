from pypdf import PdfReader, PdfWriter


def juntar(paths: list[str], destino: str) -> int:
    writer = PdfWriter()
    total = 0
    for path in paths:
        try:
            reader = PdfReader(path)
        except Exception:
            continue
        for pagina in reader.pages:
            writer.add_page(pagina)
            total += 1
    with open(destino, "wb") as f:
        writer.write(f)
    return total
