import flet as ft
import requests
import json
import math
import time
from datetime import datetime

LastMaquinaPrice = 0
LastMaquinaTipe = ''
def main(page: ft.Page):
    # Configurações da Página
    page.title = "TGAMES"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.window_width = 500
    page.window_height = 800
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = ft.colors.BLACK12


    def arredondar_para_baixo(numero):
        return math.floor(numero * 100) / 100


    def gerenciar_clique(e, on_click,cor,texto):
        botao = e.control
        # botao.content = ft.Text("AGUARDE",size=page.window_width/15,weight=ft.FontWeight.BOLD)
        botao.bgcolor = ft.colors.BLUE  # Muda cor enquanto processa
        botao.update()
        on_click(e)
        botao.bgcolor = cor  # Restaura cor original
        # botao.content = ft.Text(texto,size=page.window_width/15,weight=ft.FontWeight.BOLD)
        page.update()

    def criar_botao(texto, on_click, cor=ft.colors.AMBER_500,tamanho = page.window_width * 0.8):
        def rodar(e):
            return gerenciar_clique(e, on_click,cor,texto)
        return ft.ElevatedButton(
            content=ft.Text(texto,size=page.window_width/15,weight=ft.FontWeight.BOLD),
            on_click=rodar,
            style=ft.ButtonStyle(
                padding=ft.padding.all(20),
                side=ft.BorderSide(2, ft.colors.RED),
                bgcolor=cor,
                color=ft.colors.WHITE,
            ),width=tamanho
        )

    def switch_view(view):
        try:
            msgRetornoSuperior.value = ""
            msgRetornoSuperior.visible = False
        except: pass
        page.clean()
        page.add(view)
        page.update()


    #INFORMAÇÔES PARTE SUPERIOR
    # LOGO = ft.Text("TGAMES", size=90, weight=ft.FontWeight.BOLD, color=ft.colors.RED, text_align=ft.TextAlign.CENTER)
    LOGO = ft.Image(src='/logo - B.png', fit=ft.ImageFit.CONTAIN)
    superiorInfo = ft.Column([ft.Text("",height=10),ft.Row(
        [
            ft.Text("", size=21, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            iconHome := ft.IconButton(ft.icons.HOME, on_click=lambda e: switch_view(init_form),icon_size=page.window_width/14,icon_color='white'),
            text_superior := ft.Text("", size=page.window_width/20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white'),
            iconReload := ft.IconButton(ft.icons.UPDATE_ROUNDED, on_click=lambda e: updateUserInfo(),icon_size=page.window_width/14,icon_color='white'),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )])
    msgRetornoSuperior = ft.Text("", size=25, weight=ft.FontWeight.BOLD, color='red', text_align=ft.TextAlign.CENTER,visible=False)
    ###################################################


    # Funções de Negócio
    def iniciar_tempo(e):
        try:
            float(creditosSelecionados.value)
        except:
            return
        global userInfo
        iniciarButton.disabled = True
        iniciarButton.update()
        CREDITOS = float(creditosSelecionados.value) if creditosSelecionados.value!=0 else page.client_storage.get("UserInfo")['CREDITOS']


        if CREDITOS>arredondar_para_baixo(page.client_storage.get("UserInfo")['CREDITOS']) or page.client_storage.get("UserInfo")['CREDITOS']==0:
            msgRetornoSuperior.value = "CRÉDITOS INSUFICIENTES."
            msgRetornoSuperior.visible = True
            iniciarButton.disabled = False
            msgRetornoSuperior.update()
            iniciarButton.update()
            return
        
        resp = requests.post("https://e6tqv6zegsyxd2zhuzkhuug5o40wdmrf.lambda-url.sa-east-1.on.aws/",json={"USUARIO":page.client_storage.get("UserInfo")['USUARIO'],"MAQUINA":codigoMaquina.value,"TOKEN":page.client_storage.get("TOKEN"),"QNTD_CREDITOS":CREDITOS}).content.decode()
        if "TOKEN EXPIRADO" in resp:
            switch_view(login_form)
            return
        if "INICIADO" in resp:
            maqInfo.value = "Máquina liberada!"
            text_superior.value = f"Você tem {page.client_storage.get('UserInfo')['CREDITOS']-CREDITOS} Reais"
            msgRetornoSuperior.visible = False
            iniciarButton.disabled = False
            updateUserInfo()
            switch_view(maquina_form_suced)
        else:
            msgRetornoSuperior.value = resp
            msgRetornoSuperior.visible = True
            msgRetornoSuperior.update()
            iniciarButton.disabled = False
            iniciarButton.update()
        return



    def FinalizarMaquinaAtiva(e,dados): #FECHA MAQUINAS COM TEMPO DISPONIVEL
        def finalizar_maquina(e):
            botaoCancelarMaq.disabled = True
            botaoCancelarMaq.update()
            resp = requests.post("https://e6tqv6zegsyxd2zhuzkhuug5o40wdmrf.lambda-url.sa-east-1.on.aws/",json={"ID":dados['ID'],"PARAR":True,'USUARIO':dados['USUARIO'],"MAQUINA":dados['MAQUINA'],'TOKEN':page.client_storage.get("TOKEN")}).content.decode()
            if "TOKEN EXPIRADO" in resp:
                dialog.open = False
                page.update()
                switch_view(login_form)
                botaoCancelarMaq.disabled = False
                botaoCancelarMaq.update()
                return
            updateUserInfo(username=None)
            dialog.open = False
            botaoCancelarMaq.disabled = False
            page.update()
        def cancelar(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"FINALIZAR MÁQUINA {dados['MAQUINA']}?",size=20),
            content=ft.Text(f"Os créditos restantes serão devolvidos!", size=20, color="black", weight=ft.FontWeight.BOLD),
            actions=[
                ft.TextButton("Não", on_click=cancelar),
                botaoCancelarMaq := ft.TextButton("Sim", on_click=finalizar_maquina),
            ]
            )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def updateUserInfo(username=None): #LÊ OS DADOS DO USUARIO E ATUALIZA AS VARIAVEIS.
        global userInfo
        username = username if username!=None else page.client_storage.get("UserInfo")['USUARIO']
        resp = requests.post("https://utpbliutdlvfuvnjyblsb2qrqy0heikd.lambda-url.sa-east-1.on.aws/",json={"USUARIO":username,"TOKEN":page.client_storage.get("TOKEN")})
        if "TOKEN EXPIRADO" in resp.content.decode():
            switch_view(login_form)
            return False
        page.client_storage.set("UserInfo",json.loads(resp.content))
        try:
            text_superior.value = f"Saldo: {arredondar_para_baixo(page.client_storage.get('UserInfo')['CREDITOS'])} Reais"
        except: pass
        try:
            maquinasInfoDados = []
            if len(page.client_storage.get("UserInfo")['MAQ_ATIVAS'])>0:
                maquinasInfoDados.append(ft.Text("MAQUINAS ATIVAS:", size=16, color="white", weight=ft.FontWeight.BOLD))
            for item in page.client_storage.get("UserInfo")['MAQ_ATIVAS']:
                inicio = item['DATA_INICIO'].split(".")[0].split("T")
                fim = item['DATA_FIM'].split(".")[0].split("T")
                dados = ft.Row(
                    [
                        ft.Image("ImageControle.png",width=70,height=70),
                        ft.Text(
                            f"Máquina: {item['MAQUINA']}\nInicio: {inicio[1]}\nFim: {fim[1]}\nCréditos: {round(item['CREDITOS'],2)}",
                            size=14,
                            color="white",
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.TextButton(
                            content=ft.Text("FINALIZAR", size=16, color="white", weight=ft.FontWeight.BOLD),
                            on_click=lambda e: FinalizarMaquinaAtiva(e, item),
                        
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,  # Alinha horizontalmente no centro
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,  # Alinha verticalmente no centro
                    )

                maquinasInfoDados.append(ft.Container(dados,border=ft.border.all(3, ft.colors.WHITE),border_radius=10,alignment=ft.alignment.center))    

            maquinasAtivas.controls = maquinasInfoDados
        except: pass
        try:
            creditosSelecionados.value = arredondar_para_baixo(page.client_storage.get("UserInfo")['CREDITOS'])
        except: pass
        page.update()
        return True
    
    def login(e): #FAZ LOGIN E ARMAZENA O TOKEN DO USUARIO
        global userInfo
        botaoLogin.disabled = True
        botaoLogin.update()
        time.sleep(2)
        username, password = username_input.value, password_input.value
        if username=='' or password=='':
            loginMsg.value = 'Usuário/EMAIL ou senha inválidos'
            loginMsg.update()
            botaoLogin.disabled = False
            botaoLogin.update()
            return
        resp = requests.post("https://s6v6wlfxlyjyamy7ye77m6y3ou0josxg.lambda-url.sa-east-1.on.aws/",json={"USUARIO":username,"SENHA":password}).content.decode()

        if "TOKEN" in resp:
            DADOS = eval(resp)
            page.client_storage.set("TOKEN", DADOS['TOKEN'])
            page.client_storage.set("USUARIO", DADOS['USUARIO'])
            updateUserInfo(DADOS['USUARIO'])
            switch_view(init_form)
            loginMsg.value = ""
        else:
            loginMsg.value = resp
            page.update()
        botaoLogin.disabled = False
        botaoLogin.update()

    def register(e): #REALIZA O REGISTRO DE UM NOVO USUARIO
        registerButon.disabled = True
        registerButon.update()
        data_nasc = birth_date_inputButton.text.split("NASCIMENTO: ")[-1]
        if username_input.value =="" or reg_password_input.value == "" or reg_nome_input.value =="" or reg_Email_input.value=='' or reg_Telefone_input.value=='':
            RegisterMsg.value = "Preencha todos os dados!"
            RegisterMsg.color = "red"
            RegisterMsg.update()

        elif "SELECIONE" in data_nasc:
            RegisterMsg.value = "Selecione a data de nascimento!"
            RegisterMsg.color = "red"
            RegisterMsg.update()
        elif len(reg_password_input.value)<4:
            RegisterMsg.value = "A senha precisa ter pelo menos 4 caracteres!"
            RegisterMsg.color = "red"
            RegisterMsg.update()
        elif reg_password_input.value != reg_confirm_password_input.value:
            RegisterMsg.value = "As senhas não coincidem!"
            RegisterMsg.color = "red"
            RegisterMsg.update()
        else:
            data = {'USUARIO': reg_username_input.value, 'SENHA': reg_password_input.value,"DATA_NASC":data_nasc, 'NOME':reg_nome_input.value, "APELIDO":reg_apelido_input.value, "EMAIL":reg_Email_input.value, "TELEFONE":reg_Telefone_input.value}
            print(data)
            resp = requests.post("https://pvp4jjjptiptokuabpz2yscqya0frafw.lambda-url.sa-east-1.on.aws/",json=data).content.decode()

            msg_color = "green" if "CADASTRADO" in resp else "red"
            RegisterMsg.value = resp
            RegisterMsg.color = msg_color
            RegisterMsg.update()
            if "CADASTRADO" in resp:
                switch_view(login_form)
        registerButon.disabled = False
        registerButon.update()


    def criar_form(*controls): #CRIA AS PAGINAS
        return ft.Column(
            controls, alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20
        )
    
    def calcTempoMaq(creditos,fatorMaquina):
        try:
            calc = float(creditos) / fatorMaquina

            if calc >= 60:
                # Se o total for 60 minutos ou mais, converte para horas e minutos
                horas = int(calc // 60)
                minutos = int(calc % 60)
                if minutos>0:
                    return f"{horas} {'horas' if horas > 1 else 'hora'} e {minutos} {'minutos' if minutos > 1 else 'minuto'}"
                return f"{horas} {'horas' if horas > 1 else 'hora'}"
            else:
                # Para menos de 60 minutos, exibe minutos e segundos
                minutos = int(calc)
                segundos = int((calc - minutos) * 60)
                if minutos>0 and segundos>0:
                    return f"{minutos} {'minutos' if minutos > 1 else 'minuto'} e {segundos} {'segundos' if minutos > 1 else 'segundo'}"
                elif minutos>0:
                    return f"{minutos} {'minutos' if minutos > 1 else 'minuto'}"
                elif segundos>0:
                    return f"{segundos} {'segundos' if minutos > 1 else 'segundo'}"
                else:
                    return "0 minutos"
        except:
            return "0 minutos"
        
    def calcFichaMaq(creditos,fatorMaquina):
        try:
            calc = int(float(creditos) / fatorMaquina)
            return f'{calc} {"fichas" if calc>1 else "ficha"}'
        except:
            return "0 minutos"

    def obterInfoMaquina(e): #PEGA INFORMAÇÂO DAS MAQUINAS DISPONIVEIS
        global userInfo
        global LastMaquinaPrice
        global LastMaquinaTipe
        try:
            botaoConfirmMaq.disabled = True
            botaoConfirmMaq.update()
            resp = requests.post("https://e6tqv6zegsyxd2zhuzkhuug5o40wdmrf.lambda-url.sa-east-1.on.aws/",json={"USUARIO":page.client_storage.get("UserInfo")['USUARIO'],"MAQUINA":codigoMaquina.value,"TOKEN":page.client_storage.get("TOKEN"),'INFOMAQ':True})
            if "TOKEN EXPIRADO" in resp.text:
                switch_view(login_form)
                return
            resp = resp.json()
            if resp['tipo']=='TEMPO':
                maqInfo.value = f"Essa máquina consome R${round(resp['preco'],2)} por minuto.\nVocê poderá jogar por no máximo {calcTempoMaq(page.client_storage.get("UserInfo")['CREDITOS'],resp['preco'])} usando todo o saldo."
            else:
                creditosSelecionados.value = resp['preco'] if page.client_storage.get("UserInfo")['CREDITOS']>resp['preco'] else 0
                maqInfo.value = f"Cada ficha para essa maquina custa R${round(resp['preco'],2)}\n *Você não poderá recuperar esse saldo após confirmar"
            botaoConfirmMaq.disabled = False
            botaoConfirmMaq.update()
            switch_view(descricao_maquina)
            LastMaquinaPrice = resp['preco']
            LastMaquinaTipe = resp['tipo']
            return
        except:
            import traceback
            print(traceback.format_exc())
            msgRetornoSuperior.value = f"Máquina '{codigoMaquina.value}' não encontrada."
            msgRetornoSuperior.visible = True
            botaoConfirmMaq.disabled = False

        page.update()
        return

    def atualizaData(e): #ATUALIZA DATA DE NASCIMENTO NO CADASTRO
        birth_date_inputButton.text = "NASCIMENTO: "+e.data.split("T")[0]
        birth_date_inputButton.update()
 
    def updateTempoMaquina(e): #ATUALIZA O TEMPO DE MAQUINA PARA EXIBIR PARA O USUARIO
        global LastMaquinaPrice
        e.data = e.data.replace(",",".")
        if LastMaquinaTipe=='TEMPO':
            maqInfo.value = f"Essa máquina consome R${round(LastMaquinaPrice,2)} por minuto.\nVocê poderá jogar por {calcTempoMaq(e.data,LastMaquinaPrice)}."
        else:
            maqInfo.value = f"Cada ficha para essa maquina custa R${round(LastMaquinaPrice,2)}\nVocê poderá jogar com {calcFichaMaq(e.data,LastMaquinaPrice)}.\n *Você não poderá recuperar esse saldo após confirmar"

        maqInfo.update()
        creditosSelecionados.value = e.data
        creditosSelecionados.update()
        return


    def comprarCreditos(e):
        try:
            quantidade = float(quantidadeCreditos.value)
        except:
            return
        global userInfo
        botaoComprarCreditos.disabled = True
        botaoComprarCreditos.update()
        def voltarComprarCreditos(e):
            updateUserInfo()
            switch_view(init_form)
            return

        resp = requests.post("https://5n2aczmdhfw7lbu32kgmnuhhdq0bmqfz.lambda-url.sa-east-1.on.aws/",json={"USUARIO":page.client_storage.get("UserInfo")['USUARIO'],"QUANTIDADE":quantidade})
        navegador = criar_form(
                superiorInfo, msgRetornoSuperior,LOGO,
                criar_botao("VOLTAR", voltarComprarCreditos)
            )
        page.launch_url(resp.text)
        time.sleep(2)
        switch_view(navegador)
        botaoComprarCreditos.disabled = False
        botaoComprarCreditos.update()
        return


    def DESLOGAR(e):
        global userInfo 
        page.client_storage.set("UserInfo",{})

        password_input.value=''
        page.client_storage.set("TOKEN", '')
        switch_view(login_form)
        return
    
    # PAGINA LOGIN

    def updateCreditosValor(e): #ATUALIZA O TEMPO DE MAQUINA PARA EXIBIR PARA O USUARIO
        quantidadeCreditos.value = e.data.replace(",",".")
        quantidadeCreditos.update()
        return

    def ajustarComponentes(x=None):
        def ajustButton(x,largura = page.window.width * 0.8):
            x.width = largura
            x.content.size = page.window.width / 15

        iconHome.icon_size=page.window.width/14
        iconReload.icon_size=page.window.width/14
        text_superior.size=page.window.width/20

        ajustButton(botaoLogin)
        ajustButton(registerButon)
        ajustButton(botaoConfirmMaq)
        ajustButton(iniciarButton)
        ajustButton(voltarButton)
        ajustButton(botaoComprarCreditos)
        ajustButton(liberarMaqButton)
        ajustButton(ComprarCreditosButton)
        ajustButton(SairButton,page.window.width * 0.4)
        page.update()  # Atualiza a interface


    login_form = criar_form(
        ft.Text("", size=21, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        LOGO, ft.Text("Login", size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white'),
        username_input := ft.TextField(label=ft.Text("Usuário/EMAIL",color='white'), autofocus=True, value=page.client_storage.get("USUARIO"), text_align=ft.TextAlign.LEFT,text_size=25,color='white',border_color='white'),
        password_input := ft.TextField(label=ft.Text("Senha",color='white'), password=True, can_reveal_password=True, value='', text_align=ft.TextAlign.LEFT,text_size=25,color='white',border_color='white'),
        botaoLogin := criar_botao("Entrar", lambda x:login(x)),
        ft.TextButton("Criar uma conta", on_click=lambda e: switch_view(register_form),icon_color='white'),
        loginMsg := ft.Text("", color="red", text_align=ft.TextAlign.CENTER)
    )

    #PAGINA REGISTRO
    register_form = criar_form(
        LOGO, ft.Text("Cadastro", size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white'),
        reg_username_input := ft.TextField(label=ft.Text("Usuário",color='white'), autofocus=True, text_align=ft.TextAlign.LEFT,text_size=25,color='white',border_color='white'),
        reg_nome_input := ft.TextField(label=ft.Text("Nome completo",color='white'), autofocus=False, text_align=ft.TextAlign.LEFT,text_size=25,color='white',border_color='white'),
        reg_apelido_input := ft.TextField(label=ft.Text("Apelido",color='white'), autofocus=False, text_align=ft.TextAlign.LEFT,text_size=25,color='white',border_color='white'),
        reg_Email_input := ft.TextField(label=ft.Text("Email",color='white'), autofocus=False, text_align=ft.TextAlign.LEFT,text_size=25,color='white',border_color='white'),
        reg_Telefone_input := ft.TextField(label=ft.Text("Telefone",color='white'), autofocus=False,text_size=25,keyboard_type=ft.KeyboardType.NUMBER,color='white',border_color='white'),

        reg_password_input := ft.TextField(label=ft.Text("Senha",color='white'), password=True, can_reveal_password=True, text_align=ft.TextAlign.LEFT,text_size=25,color='white',border_color='white'),
        reg_confirm_password_input := ft.TextField(label=ft.Text("Confirme a senha",color='white'), password=True, can_reveal_password=True, text_align=ft.TextAlign.LEFT,text_size=25,color='white',border_color='white'),
        birth_date_inputButton := ft.ElevatedButton("SELECIONE A DATA DE NASCIMENTO",icon=ft.icons.CALENDAR_MONTH,on_click=lambda e: page.open(ft.DatePicker(first_date=datetime(year=1900, month=1, day=1),last_date=datetime.today(),on_change=atualizaData)),color='black'),
        RegisterMsg := ft.Text("", text_align=ft.TextAlign.CENTER,color='white'),
        registerButon := criar_botao("Cadastrar", register),
        ft.TextButton("Já tem uma conta? Login", on_click=lambda e: switch_view(login_form))
    )

    #PARTE DE LIBERACAO MAQUINA

    escolher_maquina = criar_form(
        superiorInfo, msgRetornoSuperior, LOGO,
        codigoMaquina := ft.TextField(label=ft.Text("DIGITE O NÚMERO DA MÁQUINA",color='white'), autofocus=True, value='1', text_align=ft.TextAlign.CENTER,text_size=30,keyboard_type=ft.KeyboardType.NUMBER,color='white',border_color='white'),
        botaoConfirmMaq := criar_botao("Confirmar", obterInfoMaquina)
    )

    maqInfo = ft.Text(size=21, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white')
    descricao_maquina = criar_form(
        superiorInfo, 
        LOGO, 
        msgRetornoSuperior, 
        creditosSelecionados := ft.TextField(label=ft.Text("DIGITE O VALOR QUE DESEJA UTILIZAR DO SALDO:",color='white'), autofocus=False,value=0, text_align=ft.TextAlign.CENTER,text_size=30,keyboard_type=ft.KeyboardType.NUMBER,on_change=updateTempoMaquina,color='white',border_color='white'),
        ft.Container(maqInfo,border=ft.border.all(2, ft.colors.GREY_500),border_radius=10,alignment=ft.alignment.center),
        iniciarButton := criar_botao("INICIAR", iniciar_tempo)
    )

    maquina_form_suced = criar_form(
        superiorInfo, 
        LOGO, 
        msgRetornoSuperior, 
        ft.Text("MÁQUINA LIBERADA!\n Boa diversão.",size=40, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white'),
        voltarButton := criar_botao("VOLTAR", lambda x:switch_view(init_form))
    )

    compraCreditos_form = criar_form(
        superiorInfo, msgRetornoSuperior, LOGO,
        ft.Text("Digite o valor em reais para comprar créditos.", size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white'),
        quantidadeCreditos := ft.TextField(autofocus=True, text_align=ft.TextAlign.CENTER,text_size=30,keyboard_type=ft.KeyboardType.NUMBER,color='white',border_color='white',on_change = updateCreditosValor),
        botaoComprarCreditos := criar_botao("Confirmar", comprarCreditos)  # Implemente a lógica de compra aqui
    )

    def open_pdf(pdf_path):
        page.launch_url(pdf_path)
        page.update()



    inscricaoFinalizada = criar_form(
        superiorInfo, 
        LOGO, 
        msgRetornoSuperior, 
        TextInscricao  := ft.Text("Inscrição finalizada!",size=40, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white'),
        criar_botao("VOLTAR", lambda x:switch_view(init_form))
    )

    def inscreverCampeonato(e,item): #FECHA MAQUINAS COM TEMPO DISPONIVEL
        def aceitar(e):
            resp = requests.post("https://agephcxlxb7ah2fsmsmrrmmgd40acodq.lambda-url.sa-east-1.on.aws/",json={"USUARIO":page.client_storage.get("UserInfo")['USUARIO'],"TORNEIO":(item['NOME'],item['DATA']),"TOKEN":page.client_storage.get("TOKEN")}).content.decode()
            page.close(dialog2)
            page.update()
            time.sleep(0.1)
            if "SUCESSO" in resp:
                TextInscricao.value = "Inscrição finalizada com sucesso!"
            else:
                TextInscricao.value = resp
            switch_view(inscricaoFinalizada)

        def cancelar(e):
            page.close(dialog2)

        dialog2 = ft.AlertDialog(
            title=ft.Text(f"ACEITAR REGULAMENTO?",size=20),
            content=ft.Text(f"Clicando em sim, você está automaticamente aceitando os termos descritos no regulamento do torneio.", size=20, color="black", weight=ft.FontWeight.BOLD),
            actions=[
                ft.TextButton("Não", on_click=cancelar),
                ft.TextButton("Sim", on_click=aceitar),
            ]
            )
        page.overlay.append(dialog2)
        dialog2.open = True
        page.update()



    def getTorneios():
        global userInfo
        resp = requests.post("https://agephcxlxb7ah2fsmsmrrmmgd40acodq.lambda-url.sa-east-1.on.aws/",json={"LISTAR":True}).json()
        campeonatosDados = []
        for item in resp:
            if not page.client_storage.get("USUARIO") in item['INSCRITOS']:
                buttonInscricao = ft.TextButton(content=ft.Text("INSCREVER-SE", size=16, color="white", weight=ft.FontWeight.BOLD),on_click=lambda e: inscreverCampeonato(e, item),)
            else:
                buttonInscricao = ft.TextButton(content=ft.Text("JA INSCRITO", size=16, color="green", weight=ft.FontWeight.BOLD))

            dados = ft.Column([ft.Row(
                [
                    ft.Image(src = item['IMAGEM'],width=70,height=100),
                    ft.Text(
                        f"TORNEIO: {item['NOME']} | Inicio: {item['DATA']}",
                        size=20,
                        color="white",
                        weight=ft.FontWeight.BOLD,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,  # Alinha horizontalmente no centro
                vertical_alignment=ft.CrossAxisAlignment.CENTER,  # Alinha verticalmente no centro
                ),
                ft.Row([
                    ft.TextButton(
                        content=ft.Text("REGULAMENTO", size=16, color="white", weight=ft.FontWeight.BOLD),
                        on_click=lambda e: open_pdf(item['REGULAMENTO']),
                    ),
                    buttonInscricao,
                ],
                alignment=ft.MainAxisAlignment.CENTER,  # Alinha horizontalmente no centro
                vertical_alignment=ft.CrossAxisAlignment.CENTER,  # Alinha verticalmente no centro
                )])
            campeonatosDados.append(ft.Container(dados,border=ft.border.all(3, ft.colors.WHITE),border_radius=10,alignment=ft.alignment.center))    
        campeonadosDisp.controls = campeonatosDados
        return None
    
    campeonatoForm = criar_form(
        superiorInfo, msgRetornoSuperior, LOGO,
        ft.Text("Campeonatos:", size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white'),
        campeonadosDisp := ft.Column(controls=[]),
    )
        
    init_form = criar_form(
        superiorInfo, msgRetornoSuperior, LOGO,
        liberarMaqButton := criar_botao("Liberar Máquina", lambda e: switch_view(escolher_maquina)),
        ComprarCreditosButton := criar_botao("Comprar Créditos", lambda e: switch_view(compraCreditos_form)),
        criar_botao("Campeonatos", lambda e: (getTorneios(), switch_view(campeonatoForm))[-1] ),

        maquinasAtivas := ft.Column(controls=[]),
        SairButton := criar_botao("SAIR",DESLOGAR,cor=ft.colors.RED,tamanho=200)
    
    )
    def backButton(x):
        if updateUserInfo(username=page.client_storage.get("USUARIO")):
            switch_view(init_form)
        else:
            switch_view(login_form)
        return 
    
    # Verificação de Token e Inicialização

    try:
        # page.on_app_lifecycle_state_change = backButton
        # page.on_app_lifecycle_state_change = backButton
        page.bgcolor = ft.colors.BLACK 
        ajustarComponentes()
        page.theme_mode = ft.ThemeMode.LIGHT       
        global userInfo
        if updateUserInfo(username=page.client_storage.get("USUARIO")):
            switch_view(init_form)
        else:
            switch_view(login_form)
    except:
        switch_view(login_form)

# Executa o aplicativo Flet
# ft.app(target=main)
# ft.app(target=main, view=ft.WEB_BROWSER, assets_dir='assets', port=80)
ft.app(target=main, view=ft.WEB_BROWSER, assets_dir='assets', host = "0.0.0.0", port=80)
