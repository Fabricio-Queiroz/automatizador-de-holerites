from pypdf import PdfReader, PdfWriter


def juntar(paths: list[str], destino: str) -> int:
    writer = PdfWriter()
    total = 0
    readers = []
    for path in paths:
        try:
            reader = PdfReader(path)
            readers.append(reader)
            for pagina in reader.pages:
                writer.add_page(pagina)
                total += 1
        except Exception:
            continue
    with open(destino, "wb") as f:
        writer.write(f)
    for reader in readers:
        try:
            reader.stream.close()
        except Exception:
            pass
    return total
