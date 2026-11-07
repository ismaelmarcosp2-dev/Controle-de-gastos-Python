import json
import os
import tkinter as tk

from datetime import date
from tkinter import ttk, messagebox, colorchooser


# 1. CONFIGURAÇÕES DO PROGRAMA#

ARQUIVO_DADOS = "gastos.json"
mes_atual = date.today().strftime("%Y-%m")

gastos = []
proximo_id = 1

orcamentos = {}

#2. SALVAR E CARREGAR DADOS#

    
def carregar_dados():
    global gastos, proximo_id, orcamentos

    if not os.path.exists(ARQUIVO_DADOS):
        return

    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

            gastos = dados.get("gastos", [])
            proximo_id = dados.get("proximo_id", 1)
            orcamentos = dados.get("orcamentos", {})

    except (json.JSONDecodeError, OSError) as erro:
        messagebox.showerror(
            "Erro",
            f"Não foi possível carregar os dados: {erro}"
        )

def salvar_dados():
    dados = {
        "gastos": gastos,
        "proximo_id": proximo_id,
        "orcamentos": orcamentos
    }

    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)


# 3. FUNÇÕES AUXILIARES #

def dinheiro(valor):
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "x")
    texto = texto.replace(".", ",")
    texto = texto.replace("x", ".")
    return f"R$ {texto}"

def gastos_do_mes():
    return [
        gasto for gasto in gastos
        if gasto["data"][:7] == campo_mes.get()
    ]

def atualizar_tela():
    for item in tabela.get_children():
        tabela.delete(item)

    lista = sorted(
        gastos_do_mes(),
        key=lambda gasto: (gasto["data"], gasto["id"])
        )

    for gasto in lista:
        tabela.insert("", "end",
             iid=str(gasto["id"]), 
             values=(
                 gasto["data"],
                 gasto["nome"],
                 gasto["categoria"],
                 dinheiro(gasto["valor"]),              
                 gasto["cor"]
             ),
            tags=(gasto["cor"],)
         )
            
        tabela.tag_configure(
             gasto["cor"],
            background=gasto["cor"]
         )

    total = sum(gasto["valor"] for gasto in lista) 
    mes= campo_mes.get()
    orcamento = orcamentos.get(mes, 0.0)
    restante = orcamento - total
    texto_total.config(text=f"Total gasto: {dinheiro(total)}")

    texto_orcamento.config(
        text=f"Orçamento: {dinheiro(orcamento)}"
    )
    texto_restante.config(
        text=f"Saldo: {dinheiro(restante)}"
    )

    campo_orcamento.delete(0, tk.END)
    campo_orcamento.insert(0, str(orcamento).replace(".", ","))



    
# 4. ADICIONAR OU EDITAR GASTO

def abrir_formulario(gasto_existente=None):
    global proximo_id

    # Criar a janela do formulário
    janela = tk.Toplevel(root)
    janela.title(
        "Editar gasto" if gasto_existente else "Novo gasto"
    )
    janela.geometry("380x460")
    janela.resizable(False, False)
    janela.transient(root)
    janela.grab_set()

    # Valores iniciais do formulário
    valores = gasto_existente or {
        "nome": "",
        "valor": 0.0,
        "data": date.today().isoformat(),
        "categoria": "Outros",
        "cor": "#D9EAF7"
    }

    # Campo: nome
    tk.Label(janela, text="Nome do gasto").pack(pady=(12, 2))
    campo_nome = tk.Entry(janela, width=35)
    campo_nome.pack()
    campo_nome.insert(0, valores["nome"])

    # Campo: valor
    tk.Label(janela, text="Valor (R$)").pack(pady=(10, 2))
    campo_valor = tk.Entry(janela, width=35)
    campo_valor.pack()
    campo_valor.insert(0, str(valores["valor"]))

    # Campo: data
    tk.Label(janela, text="Data (AAAA-MM-DD)").pack(pady=(10, 2))
    campo_data = tk.Entry(janela, width=35)
    campo_data.pack()
    campo_data.insert(0, valores["data"])

    # Campo: categoria
    tk.Label(janela, text="Categoria").pack(pady=(10, 2))

    campo_categoria = ttk.Combobox(
        janela,
        values=[
            "Moradia", "Alimentação", "Transporte",
            "Contas", "Saúde", "Lazer", "Outros"
        ],
        state="readonly",
        width=32
    )
    campo_categoria.pack()
    campo_categoria.set(valores["categoria"])

    # Campo: cor
    cor_escolhida = tk.StringVar(value=valores["cor"])

    tk.Label(janela, text="Cor do gasto").pack(pady=(10, 2))

    amostra_cor = tk.Label(
        janela,
        text="Cor selecionada",
        bg=cor_escolhida.get(),
        width=20
    )
    amostra_cor.pack()

    def escolher_cor():
     cor = colorchooser.askcolor(
        color=cor_escolhida.get(),
        parent=janela,
        title="Escolha uma cor"
    )

     if cor[1]:
        cor_escolhida.set(cor[1])
        amostra_cor.config(bg=cor[1])


    tk.Button(
    janela,
    text="Escolher cor",
    command=escolher_cor
    ).pack(pady=5)

    # Função para salvar o gasto

    def salva_gasto():
        global proximo_id

        nome = campo_nome.get().strip()
        valor_texto = campo_valor.get().strip()
        data_texto = campo_data.get().strip()
        categoria = campo_categoria.get()

        # Validar nome
        if not nome:
            messagebox.showwarning(
                "Atenção",
                "Informe o nome do gasto.",
                parent=janela
            )
            return

        # Validar valor
        try:
            valor = float(
                valor_texto.replace(".", "").replace(",", ".")
            )

            if valor <= 0:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Atenção",
                "Informe um valor válido maior que zero.",
                parent=janela
            )
            return

        # Validar data
        try:
            data_validada = date.fromisoformat(data_texto)

        except ValueError:
            messagebox.showwarning(
                "Atenção",
                "Informe uma data válida no formato AAAA-MM-DD.",
                parent=janela
            )
            return

        # Validar categoria
        if not categoria:
            messagebox.showwarning(
                "Atenção",
                "Selecione uma categoria.",
                parent=janela
            )
            return

        # Editar um gasto existente
        if gasto_existente:
            gasto_existente.update({
                "nome": nome,
                "valor": valor,
                "data": data_validada.isoformat(),
                "categoria": categoria,
                "cor": cor_escolhida.get()
            })

        # Adicionar um gasto novo
        else:
            gastos.append({
                "id": proximo_id,
                "nome": nome,
                "valor": valor,
                "data": data_validada.isoformat(),
                "categoria": categoria,
                "cor": cor_escolhida.get()
            })

            proximo_id += 1

        # Salvar, atualizar a tela e fechar o formulário
        salvar_dados()
        atualizar_tela()
        janela.destroy()

    # O botão fica dentro de abrir_formulario,
    # mas fora da função salva_gasto.
    tk.Button(
        janela,
        text="Salvar gasto",
        command=salva_gasto
    ).pack(pady=12)

# EDITAR E EXCLUIR#


def obter_gasto_selecionado():
    selecao = tabela.selection()

    if not selecao:
        messagebox.showwarning(
            "Atenção", "Selecione um gasto na tabela."
        )
        return None
    
    identificador = int(selecao[0])

    for gasto in gastos:
        if gasto["id"] == identificador:
            return gasto
    return None
    
def editar_gasto():
    gasto = obter_gasto_selecionado()

    if gasto:
        abrir_formulario(gasto)

def excluir_gasto():
    gasto = obter_gasto_selecionado()

    if not gasto:
        return

    confirmar = messagebox.askyesno(
        "Confirmar exclusão",
        f"Deseja excluir o gasto '{gasto['nome']}'?"
    )

    if confirmar:
        gastos.remove(gasto)
        salvar_dados()
        atualizar_tela()


        # 6. CONFIGURAR O ORÇAMENTO MENSAL #
        #

def definir_orcamento():
    mes = campo_mes.get()

    try:
        data_mes = date.fromisoformat(mes + "-01")
    except ValueError:
        messagebox.showwarning(
            "Atenção",
            "informe o mês no formato AAAA-MM"
        )
        return

    texto = campo_orcamento.get().strip()

    try:
        valor = float(
            texto.replace(".", "").replace(",", ".")
        )

        if valor < 0:
            raise ValueError

    except ValueError:
        messagebox.showwarning(
            "Atenção", "Informe um orçamento válido."
        )
        return

    orcamentos[data_mes.strftime("%Y-%m")] = valor

    salvar_dados()
    atualizar_tela()


# 7. MONTAR INTERFACE###

carregar_dados()

root = tk.Tk()
root.title("Meu Controle de Gastos")
root.geometry("950x600")
root.minsize(760, 500)

titulo = tk.Label(
    root,
    text="MEU CONTROLE DE GASTOS",
    font=("Arial", 18, "bold")
)
titulo.pack(pady=12)

painel_mes = tk.Frame(root)
painel_mes.pack(pady=5)

tk.Label(
    painel_mes,
    text="Mês (AAAA-MM):"
).pack(side="left", padx=5)

campo_mes = tk.Entry(painel_mes, width=10)
campo_mes.pack(side="left", padx=5)
campo_mes.insert(0, mes_atual)

tk.Label(
    painel_mes,
    text="Orçamento mensal (R$):"
).pack(side="left", padx=5)

campo_orcamento = tk.Entry(painel_mes, width=12)
campo_orcamento.pack(side="left", padx=5)

botao_orcamento = tk.Button(
    painel_mes,
    text="Definir orçamento",
    command=definir_orcamento
)
botao_orcamento.pack(side="left", padx=5)

colunas =("data", "nome", "categoria", "valor", "cor")

tabela = ttk.Treeview(
    root,
    columns=colunas,
    show="headings",
    height=15
)

tabela.heading("data", text="Data")
tabela.heading("nome", text="Gasto")
tabela.heading("categoria", text="categoria")
tabela.heading("valor", text="valor")
tabela.heading("cor", text="cor")

tabela.column("data", width=110, anchor="center")
tabela.column("nome", width=250)
tabela.column("categoria", width=150)
tabela.column("valor", width=130, anchor="e")
tabela.column("cor", width=120, anchor="center")

tabela.pack(fill="both", expand=True, padx=15, pady=10)

painel_botoes = tk.Frame(root)
painel_botoes.pack(pady=5)

tk.Button(
    painel_botoes,
    text="Adicionar gasto",
    command=lambda: abrir_formulario()
).pack(side="left", padx=5)

tk.Button(
    painel_botoes,
    text="Editar selecionado",
    command=editar_gasto
).pack(side="left", padx=5)

tk.Button(
    painel_botoes,
    text="Excluir selecionado",
    command=excluir_gasto
).pack(side="left", padx=5)

painel_resumo = tk.Frame(root)
painel_resumo.pack(pady=10)

texto_total = tk.Label(
    painel_resumo,
    text="Total gasto: R$ 0,00", font=("Arial", 12, "bold")
)
texto_total.pack(side="left", padx=15)

texto_orcamento = tk.Label(
    painel_resumo,
    text="Orçamento: R$ 0,00"
)
texto_orcamento.pack(side="left", padx=15)

texto_restante = tk.Label(
    painel_resumo,
    text="saldo: R$ 0,00"
)
texto_restante.pack(side="left", padx=15)

atualizar_tela()

# MANTÉM A JANELA ABERTA E RESPONDE AOS CLIQUES 
root.mainloop()