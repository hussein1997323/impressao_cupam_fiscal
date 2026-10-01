import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

import serial
from serial.tools import list_ports


ESC = b"\x1b"
GS = b"\x1d"


def portas_disponiveis() -> list[str]:
    portas = [porta.device for porta in list_ports.comports()]
    return sorted(portas, key=lambda nome: int(nome[3:]) if nome[3:].isdigit() else 9999)


def montar_cupom(texto: str) -> bytes:
    conteudo = texto.replace("\n", "\r\n").encode("cp850", errors="replace")
    return (
        ESC + b"@"              # Reinicia a impressora
        + ESC + b"a\x01"        # Centraliza
        + ESC + b"E\x01"        # Negrito ligado
        + b"BEMATECH MP-4200 HS\r\n"
        + ESC + b"E\x00"        # Negrito desligado
        + b"TESTE DE IMPRESSAO\r\n"
        + b"================================\r\n"
        + ESC + b"a\x00"        # Alinha à esquerda
        + conteudo
        + b"\r\n================================\r\n"
        + ESC + b"a\x01"
        + b"TESTE CONCLUIDO\r\n\r\n\r\n"
        + GS + b"V\x00"         # Corte total
    )


class Aplicativo(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Teste Bematech MP-4200 HS")
        self.geometry("650x520")
        self.minsize(580, 460)

        self.porta = tk.StringVar(value="COM12")
        self.velocidade = tk.StringVar(value="9600")
        self.status = tk.StringVar(value="Pronto para testar")

        self._montar_tela()
        self.atualizar_portas()

    def _montar_tela(self) -> None:
        principal = ttk.Frame(self, padding=22)
        principal.pack(fill="both", expand=True)

        ttk.Label(
            principal,
            text="Bematech MP-4200 HS",
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            principal,
            text="Impressão direta pela porta serial, sem usar a fila do Windows.",
        ).pack(anchor="w", pady=(2, 18))

        configuracao = ttk.LabelFrame(principal, text="Conexão", padding=14)
        configuracao.pack(fill="x")

        ttk.Label(configuracao, text="Porta:").grid(row=0, column=0, sticky="w")
        self.combo_porta = ttk.Combobox(
            configuracao, textvariable=self.porta, width=15, state="normal"
        )
        self.combo_porta.grid(row=1, column=0, padx=(0, 14), sticky="ew")

        ttk.Label(configuracao, text="Velocidade:").grid(row=0, column=1, sticky="w")
        ttk.Combobox(
            configuracao,
            textvariable=self.velocidade,
            values=("9600", "19200", "38400", "57600", "115200"),
            width=15,
            state="readonly",
        ).grid(row=1, column=1, padx=(0, 14), sticky="ew")

        ttk.Button(configuracao, text="Atualizar portas", command=self.atualizar_portas).grid(
            row=1, column=2, sticky="ew"
        )
        configuracao.columnconfigure(0, weight=1)
        configuracao.columnconfigure(1, weight=1)

        ttk.Label(principal, text="Texto do teste:").pack(anchor="w", pady=(18, 6))
        self.texto = tk.Text(principal, height=12, font=("Consolas", 11), wrap="word")
        self.texto.pack(fill="both", expand=True)
        self.texto.insert(
            "1.0",
            "Impressora funcionando corretamente.\n"
            "Porta configurada: COM12\n"
            f"Data: {datetime.now():%d/%m/%Y %H:%M}\n\n"
            "Produto                 Valor\n"
            "Cafe                    5,00\n"
            "Pao de queijo           7,00\n"
            "TOTAL                   12,00",
        )

        botoes = ttk.Frame(principal)
        botoes.pack(fill="x", pady=(16, 8))
        ttk.Button(botoes, text="Testar conexão", command=self.testar_conexao).pack(
            side="left"
        )
        ttk.Button(botoes, text="Imprimir teste", command=self.imprimir).pack(
            side="right"
        )

        ttk.Separator(principal).pack(fill="x", pady=6)
        ttk.Label(principal, textvariable=self.status).pack(anchor="w")

    def atualizar_portas(self) -> None:
        portas = portas_disponiveis()
        self.combo_porta["values"] = portas
        if not self.porta.get() and portas:
            self.porta.set(portas[0])
        self.status.set(
            "Portas encontradas: " + ", ".join(portas)
            if portas
            else "Nenhuma porta serial encontrada"
        )

    def _abrir_porta(self) -> serial.Serial:
        nome = self.porta.get().strip().upper()
        if not nome:
            raise ValueError("Informe a porta, por exemplo COM12.")
        return serial.Serial(
            port=nome,
            baudrate=int(self.velocidade.get()),
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=2,
            write_timeout=3,
        )

    def _porta_nao_configuravel(self, erro: Exception) -> bool:
        return isinstance(erro, serial.SerialException) and "configure port" in str(erro)

    def _abrir_direto(self):
        # COM virtual USB que rejeita SetCommState: grava sem configurar a porta.
        return open("\\\\.\\" + self.porta.get().strip().upper(), "wb", buffering=0)

    def _enviar(self, dados: bytes) -> None:
        try:
            with self._abrir_porta() as impressora:
                impressora.write(dados)
                impressora.flush()
        except serial.SerialException as erro:
            if not self._porta_nao_configuravel(erro):
                raise
            with self._abrir_direto() as impressora:
                impressora.write(dados)

    def testar_conexao(self) -> None:
        try:
            try:
                with self._abrir_porta():
                    pass
            except serial.SerialException as erro:
                if not self._porta_nao_configuravel(erro):
                    raise
                with self._abrir_direto():
                    pass
            self.status.set(f"Conexão realizada com sucesso em {self.porta.get()}.")
            messagebox.showinfo("Conexão", "A porta foi aberta com sucesso.")
        except Exception as erro:
            self._mostrar_erro(erro)

    def imprimir(self) -> None:
        try:
            dados = montar_cupom(self.texto.get("1.0", "end").strip())
            self._enviar(dados)
            self.status.set(f"Teste enviado para {self.porta.get()} ({len(dados)} bytes).")
            messagebox.showinfo("Impressão", "Teste enviado com sucesso.")
        except Exception as erro:
            self._mostrar_erro(erro)

    def _mostrar_erro(self, erro: Exception) -> None:
        mensagem = str(erro)
        if "PermissionError" in type(erro).__name__ or "Access is denied" in mensagem:
            mensagem = (
                f"A porta {self.porta.get()} está ocupada. Feche programas de impressão "
                "e filas que estejam usando essa porta e tente novamente."
            )
        self.status.set("Erro: " + mensagem)
        messagebox.showerror("Não foi possível imprimir", mensagem)


if __name__ == "__main__":
    Aplicativo().mainloop()

