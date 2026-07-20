from pypdf import PdfReader, PdfWriter


def juntar(paths: list[str], destino: str) -> int:
    writer = PdfWriter()
    total = 0
    for path in paths:
        try:
            reader = PdfReader(path)
            for pagina in reader.pages:
                writer.add_page(pagina)
                total += 1
        except Exception:
            continue
    with open(destino, "wb") as f:
        writer.write(f)
    return total
