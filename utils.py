import flet as ft
import traceback
import math
import time

def getCache(page,chave):
    if page.web:
        return page.session.get(chave)
    else:
        return page.client_storage.get(chave)
    
def setCache(page,chave,valor):
    if page.web:
        return page.session.set(chave,valor)
    else:
        return page.client_storage.set(chave,valor)

def contemCache(page,chave):
    if page.web:
        return page.session.contains_key(chave)
    else:
        return page.client_storage.contains_key(chave)


def gerenciar_clique(e, on_click,cor,texto):
    botao = e.control
    botao.disabled = True
    botao.content.value = "AGUARDE"
    botao.bgcolor = ft.Colors.BLUE  # Muda cor enquanto processa
    botao.update()
    try:
        on_click(e)
    except: print(traceback.format_exc())
    botao.disabled = False
    botao.bgcolor = cor  # Restaura cor original
    botao.content.value = texto
    botao.update()

def criar_form(*controls): #CRIA AS PAGINAS
    return ft.Column(
        controls, alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20
    )

def criar_botao(page,botoesList, texto, on_click, cor=ft.Colors.AMBER_500,tamanho = None,visivel = True):
    tamanho = getCache(page,"largura") * 0.8 if tamanho == None else tamanho
    def rodar(e):
        return gerenciar_clique(e, on_click,cor,texto)
    botao = ft.ElevatedButton(
        content=ft.Text(texto,size=getCache(page,"largura")/15,weight=ft.FontWeight.BOLD),
        on_click=rodar,
        style=ft.ButtonStyle(
            padding=ft.padding.all(20),
            side=ft.BorderSide(2, ft.Colors.RED),
            bgcolor=cor,
            color=ft.Colors.WHITE,
        ),
        visible=visivel
    )
    botoesList.append(botao)
    return botao

def switch_view(page,view):
    global msgRetornoSuperior
    try:
        msgRetornoSuperior.value = ""
        msgRetornoSuperior.visible = False
    except: pass
    page.clean()
    page.add(view)
    page.update()


def arredondar_para_baixo(numero,tratar=False):
    valor = math.floor(numero * 100) / 100
    if not tratar: return valor
    if valor>1000:
        return f"{round(valor/1000,2)}K"
    else:
        return round(valor,1)


def criarAlerta(page,dados): #FECHA MAQUINAS COM TEMPO DISPONIVEL
    def aceitar(e):
        botaoConfirmar.disabled = True
        botaoConfirmar.update()
        dados['aceitar'](page)
        page.close(dialog)
        page.update()
        time.sleep(0.2)
        botaoConfirmar.disabled = False
        if dados.get('swith',False):
            switch_view(page,dados['swith'])
        return 

    def cancelar(e):
        dialog.open = False
        page.update()
        return 

    dialog = ft.AlertDialog(
        title=ft.Text(dados['title'],size=20),
        content=ft.Text(dados['text'], size=20, color="black", weight=ft.FontWeight.BOLD),
        actions=[
            ft.TextButton("Não", on_click=cancelar),
            botaoConfirmar := ft.TextButton("Sim", on_click=aceitar),
        ]
        )
    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def createTable(page,dados,superiorInfo):
    colunas = dados[0].keys()
    TABELA =  ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(x, weight=ft.FontWeight.BOLD)) for x in colunas
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row[coluna], weight=ft.FontWeight.BOLD,no_wrap=False,overflow=ft.TextOverflow.VISIBLE)) for coluna in colunas
                        
                    ]
                ) for row in dados

            ],
        width=getCache(page,"largura")+100,
        bgcolor="yellow",
        border=ft.border.all(2, "red"),
        border_radius=10,
        vertical_lines=ft.BorderSide(3, "blue"),
        horizontal_lines=ft.BorderSide(1, "green"),
        sort_column_index=0,
        sort_ascending=True,
        heading_row_color=ft.Colors.BLACK12,
        heading_row_height=100,
        data_row_color={ft.ControlState.HOVERED: "0x30FF0000"},
        show_checkbox_column=True,
        divider_thickness=0,
        expand=True,
        column_spacing=getCache(page,"largura") * 0.02,
        height=None,
        )
    cv = ft.Column([TABELA],scroll=True)
    rv = ft.Row([cv],scroll=True,expand=1,vertical_alignment=ft.CrossAxisAlignment.START)
    return criar_form(superiorInfo, rv)


def getLog():
    import logging
    from logging.handlers import RotatingFileHandler
    LOG_FILE = "app.log"
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
    BACKUP_COUNT = 5  # Mantém até 5 arquivos antigos

    handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    class LogRedirector:
        def write(self, message):
            if message.strip():
                logger.info(message.strip())

        def flush(self):
            pass

        def isatty(self):
            return False

    sys.stdout = LogRedirector()
    sys.stderr = LogRedirector()