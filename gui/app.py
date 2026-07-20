import os
import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.pipeline import processar

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class AppHolerites(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Automatizador de Holerites 2.0")
        self.geometry("560x520")
        self.minsize(520, 480)

        self.pasta_origem = None
        self.modo = ctk.StringVar(value="renomear_e_juntar")

        self._montar_ui()

    def _montar_ui(self):
        ctk.CTkLabel(
            self, text="Automatizador de Holerites",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(pady=(24, 4))
        ctk.CTkLabel(
            self, text="Junta e renomeia holerites em ordem cronologica",
            text_color=("gray40", "gray70"),
        ).pack(pady=(0, 16))

        self.area = ctk.CTkFrame(self, height=120, corner_radius=12)
        self.area.pack(fill="x", padx=24, pady=8)
        self.lbl_pasta = ctk.CTkLabel(
            self.area, text="Nenhuma pasta selecionada",
            font=ctk.CTkFont(size=13),
        )
        self.lbl_pasta.pack(expand=True, pady=8)
        ctk.CTkButton(
            self.area, text="Escolher pasta com holerites...",
            command=self._escolher_pasta,
        ).pack(pady=(0, 12))

        seg = ctk.CTkSegmentedButton(
            self, values=["Renomear e Juntar", "Somente Juntar"],
            command=self._trocar_modo,
        )
        seg.set("Renomear e Juntar")
        seg.pack(pady=16)

        self.btn = ctk.CTkButton(
            self, text="Processar", height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._processar,
        )
        self.btn.pack(pady=8, padx=24, fill="x")

        self.progresso = ctk.CTkProgressBar(self)
        self.progresso.set(0)
        self.progresso.pack(pady=8, padx=24, fill="x")

        self.status = ctk.CTkLabel(self, text="", justify="left")
        self.status.pack(pady=8, padx=24, fill="x")

    def _escolher_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta com os holerites")
        if pasta:
            self.pasta_origem = pasta
            self.lbl_pasta.configure(text=pasta)

    def _trocar_modo(self, valor):
        self.modo.set(
            "renomear_e_juntar" if valor == "Renomear e Juntar" else "somente_juntar"
        )

    def _processar(self):
        if not self.pasta_origem:
            messagebox.showwarning("Atencao", "Escolha uma pasta primeiro.")
            return
        self.btn.configure(state="disabled")
        self.progresso.set(0)
        self.status.configure(text="Processando...")
        saida = os.path.join(self.pasta_origem, "HOLERITES ORGANIZADOS")
        threading.Thread(
            target=self._rodar, args=(saida,), daemon=True
        ).start()

    def _rodar(self, saida):
        def cb(atual, total, nome):
            frac = atual / total if total else 0
            self.after(0, lambda: self.progresso.set(frac))

        try:
            rel = processar(self.pasta_origem, saida, self.modo.get(), cb)
        except Exception as e:
            # Capturar a mensagem numa variavel local ANTES de agendar: o Python
            # apaga o nome `e` ao sair do except, e o lambda so roda depois (via
            # self.after), o que causaria NameError.
            msg = str(e)
            self.after(0, lambda: self._erro(msg))
            return
        self.after(0, lambda: self._concluir(rel, saida))

    def _erro(self, msg):
        self.btn.configure(state="normal")
        self.status.configure(text="")
        messagebox.showerror("Erro", msg)

    def _concluir(self, rel, saida):
        self.progresso.set(1)
        self.btn.configure(state="normal")
        if not rel.pdf_final:
            self.progresso.set(0)
            self.status.configure(text="Nenhum PDF encontrado na pasta.")
            messagebox.showinfo(
                "Nada a fazer",
                "Nenhum PDF encontrado na pasta selecionada.",
            )
            return
        resumo = (
            f"Concluido!\n"
            f"{len(rel.organizados)} organizados  |  "
            f"{len(rel.duplicados_ignorados)} duplicados ignorados  |  "
            f"{len(rel.revisar_manualmente)} para revisar"
        )
        self.status.configure(text=resumo)
        if messagebox.askyesno("Sucesso", resumo + "\n\nAbrir a pasta de saida?"):
            os.startfile(saida)
