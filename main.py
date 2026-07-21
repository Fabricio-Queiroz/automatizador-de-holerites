import os
import sys


def _preparar_tkinter_empacotado():
    """Permite importar o tkinter puro incluído pelo build manual do PyInstaller."""
    base = getattr(sys, "_MEIPASS", None)
    if not base:
        return
    pacote = os.path.join(base, "tkinter")
    if os.path.isfile(os.path.join(pacote, "__init__.py")):
        sys.path.insert(0, base)


_preparar_tkinter_empacotado()

from gui.app import AppHolerites


def main():
    app = AppHolerites()
    app.mainloop()


if __name__ == "__main__":
    main()
