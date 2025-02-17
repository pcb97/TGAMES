import flet as ft
import requests
import json
import time
from datetime import datetime
import flet as ft
import traceback
from utils import criar_form, criar_botao, getCache, setCache, contemCache, switch_view,arredondar_para_baixo,criarAlerta,createTable,getLog
import os
botoesList = []
def main(page: ft.Page):
    try:
        if page.web:
            getLog()
        time.sleep(0.2)
        setCache(page,"largura",page.width)
        page.title = "TGAMES"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.padding = 10
        page.window_width = 500
        page.window_height = 800
        page.scroll = ft.ScrollMode.AUTO
        page.bgcolor = ft.Colors.BLACK12



        #INFORMAÇÔES PARTE SUPERIOR
        LOGO = ft.Image(src='LOGO_FIXED.png')
        superiorInfo = ft.Column([ft.Row([ft.Text("",height=10)]),ft.Row(
            [
                iconHome := ft.IconButton(ft.Icons.HOME, on_click=lambda e: switch_view(page,init_form),icon_size=getCache(page,"largura")/10,icon_color='white',padding=0),
                text_superior := ft.Text("", size=getCache(page,"largura")/20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white'),
                iconReload := ft.IconButton(ft.Icons.UPDATE_ROUNDED, on_click=lambda e: updateUserInfo(),icon_size=getCache(page,"largura")/10,icon_color='white'),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )],alignment=ft.MainAxisAlignment.CENTER)
        msgRetornoSuperior = ft.Text("", size=25, weight=ft.FontWeight.BOLD, color='red', text_align=ft.TextAlign.CENTER,visible=False)
        ###################################################


        # Funções de Negócio
        def iniciar_tempo(e):
            try:
                float(creditosSelecionados.value)
            except:
                return
            CREDITOS = float(creditosSelecionados.value) if creditosSelecionados.value!=0 else getCache(page,"UserInfo")['CREDITOS']


            if CREDITOS>arredondar_para_baixo(getCache(page,"UserInfo")['CREDITOS']) or getCache(page,"UserInfo")['CREDITOS']==0:
                msgRetornoSuperior.value = "CRÉDITOS INSUFICIENTES."
                msgRetornoSuperior.visible = True
                msgRetornoSuperior.update()
                return
            
            resp = requests.post("https://e6tqv6zegsyxd2zhuzkhuug5o40wdmrf.lambda-url.sa-east-1.on.aws/",json={"USUARIO":getCache(page,"UserInfo")['USUARIO'],"MAQUINA":codigoMaquina.value,"TOKEN":getCache(page,"TOKEN"),"QNTD_CREDITOS":CREDITOS}).content.decode()
            if "TOKEN EXPIRADO" in resp:
                switch_view(page,login_form)
                return
            if "INICIADO" in resp:
                maqInfo.value = "Máquina liberada!"
                text_superior.value = f"Você tem {getCache(page,'UserInfo')['CREDITOS']-CREDITOS} Reais"
                msgRetornoSuperior.visible = False
                updateUserInfo()
                switch_view(page,maquina_form_suced)
            else:
                msgRetornoSuperior.value = resp
                msgRetornoSuperior.visible = True
                msgRetornoSuperior.update()
            return



        def finalizar_maquina(dados):
            resp = requests.post("https://e6tqv6zegsyxd2zhuzkhuug5o40wdmrf.lambda-url.sa-east-1.on.aws/",json={"ID":dados['ID'],"PARAR":True,'USUARIO':dados['USUARIO'],"MAQUINA":dados['MAQUINA'],'TOKEN':getCache(page,"TOKEN")}).content.decode()
            if "TOKEN EXPIRADO" in resp:
                return switch_view(page,login_form)
            else:
                return updateUserInfo(username=None)
            
        def updateUserInfo(username=None): #LÊ OS DADOS DO USUARIO E ATUALIZA AS VARIAVEIS.
            username = username if username!=None else getCache(page,"UserInfo")['USUARIO']

            resp = requests.post("https://utpbliutdlvfuvnjyblsb2qrqy0heikd.lambda-url.sa-east-1.on.aws/",json={"USUARIO":username,"TOKEN":getCache(page,"TOKEN")})
            if "TOKEN EXPIRADO" in resp.content.decode():
                switch_view(page,login_form)
                return False
            setCache(page,"UserInfo",json.loads(resp.content))
            try:
                text_superior.value = f"Saldo: {arredondar_para_baixo(getCache(page,'UserInfo')['CREDITOS'],tratar=True)} Reais"
            except: pass
            try:
                maquinasInfoDados = []
                if len(getCache(page,"UserInfo")['MAQ_ATIVAS'])>0:
                    maquinasInfoDados.append(ft.Text("MAQUINAS ATIVAS:", size=16, color="white", weight=ft.FontWeight.BOLD))
                for item in getCache(page,"UserInfo")['MAQ_ATIVAS']:
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
                                on_click=lambda e: criarAlerta(page,{'title':f"FINALIZAR MÁQUINA {item['MAQUINA']}?",'text':"Os créditos restantes serão devolvidos!",'aceitar':lambda x:finalizar_maquina(item)}),
                            
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,  # Alinha horizontalmente no centro
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,  # Alinha verticalmente no centro
                        )

                    maquinasInfoDados.append(ft.Container(dados,border=ft.border.all(3, ft.Colors.WHITE),border_radius=10,alignment=ft.alignment.center))    

                maquinasAtivas.controls = maquinasInfoDados

                if getCache(page,"UserInfo").get("ADMIN",False):
                    ADM_MODE.visible = True
                else:
                    ADM_MODE.visible = False
            except: pass
            try:
                creditosSelecionados.value = arredondar_para_baixo(getCache(page,"UserInfo")['CREDITOS'])
            except: pass
            page.update()
            return True
        
        def login(e): #FAZ LOGIN E ARMAZENA O TOKEN DO USUARIO
            username, password = username_input.value, password_input.value
            if username=='' or password=='':
                loginMsg.value = 'Usuário/EMAIL ou senha inválidos'
                loginMsg.update()
                return
            resp = requests.post("https://s6v6wlfxlyjyamy7ye77m6y3ou0josxg.lambda-url.sa-east-1.on.aws/",json={"USUARIO":username,"SENHA":password}).content.decode()

            if "TOKEN" in resp:
                DADOS = eval(resp)
                setCache(page,"TOKEN", DADOS['TOKEN'])
                updateUserInfo(DADOS['USUARIO'])
                switch_view(page,init_form)
                loginMsg.value = ""
            else:
                loginMsg.value = resp
                page.update()
            password_input.value = ""

        def redefinir_senha(e):
            if esqueci_username_input.value!="" and esqueci_Email_input.value!="" and esqueci_birth_date_inputButton!="":
                resp = requests.post("https://zfkvumifymjafmmf2ygtnlims40yvvar.lambda-url.sa-east-1.on.aws/",json={"USUARIO":esqueci_username_input.value,'EMAIL':esqueci_Email_input.value,"TIPO":'ESQUECI_SENHA',"DATA_NASCIMENTO":esqueci_birth_date_inputButton.text.split("NASCIMENTO: ")[-1]}).text
                if resp == "SENHA REDEFINIDA":
                    esqueci_RegisterMsg.value = "Senha redefinida com sucesso!\nVerifique seu email!"
                    esqueci_RegisterMsg.color = "green"
                else:
                    esqueci_RegisterMsg.value = resp
                    esqueci_RegisterMsg.color = "red"
            else:
                esqueci_RegisterMsg.value = "PREENCHA TODOS OS CAMPOS"
                esqueci_RegisterMsg.color = "red"
            esqueci_RegisterMsg.update()
            return

        def register(e): #REALIZA O REGISTRO DE UM NOVO USUARIO
            data_nasc = birth_date_inputButton.text.split("NASCIMENTO: ")[-1]
            if reg_username_input.value =="" or reg_password_input.value == "" or reg_nome_input.value =="" or reg_Email_input.value=='' or reg_Telefone_input.value=='':
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
                    switch_view(page,login_form)



        
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
            try:
                resp = requests.post("https://e6tqv6zegsyxd2zhuzkhuug5o40wdmrf.lambda-url.sa-east-1.on.aws/",json={"USUARIO":getCache(page,"UserInfo")['USUARIO'],"MAQUINA":codigoMaquina.value,"TOKEN":getCache(page,"TOKEN"),'INFOMAQ':True})
                if "TOKEN EXPIRADO" in resp.text:
                    switch_view(page,login_form)
                    return
                resp = resp.json()
                if resp['tipo']=='TEMPO':
                    maqInfo.value = f"Essa máquina consome R${round(resp['preco'],2)} por minuto.\nVocê poderá jogar por no máximo {calcTempoMaq(getCache(page,'UserInfo')['CREDITOS'],resp['preco'])} usando todo o saldo."
                else:
                    creditosSelecionados.value = resp['preco'] if getCache(page,"UserInfo")['CREDITOS']>resp['preco'] else 0
                    maqInfo.value = f"Cada ficha para essa maquina custa R${round(resp['preco'],2)}\n *Você não poderá recuperar esse saldo após confirmar"
                switch_view(page,descricao_maquina)
                setCache(page,"LastMaquinaPrice",resp['preco'])
                setCache(page,"LastMaquinaTipe",resp['tipo'])
                return
            except:
                print(traceback.format_exc())
                msgRetornoSuperior.value = f"Máquina '{codigoMaquina.value}' não encontrada."
                msgRetornoSuperior.visible = True

            page.update()
            return

        def atualizaData(e): #ATUALIZA DATA DE NASCIMENTO NO CADASTRO
            birth_date_inputButton.text = "NASCIMENTO: "+e.data.split("T")[0]
            birth_date_inputButton.update()

        def atualizaDataRedefinicao(e): #ATUALIZA DATA DE NASCIMENTO NO CADASTRO
            esqueci_birth_date_inputButton.text = "NASCIMENTO: "+e.data.split("T")[0]
            esqueci_birth_date_inputButton.update()
    
        def updateTempoMaquina(e): #ATUALIZA O TEMPO DE MAQUINA PARA EXIBIR PARA O USUARIO
            LastMaquinaPrice = getCache(page,"LastMaquinaPrice")
            e.data = e.data.replace(",",".")
            if getCache(page,"LastMaquinaTipe")=='TEMPO':
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
            def voltarComprarCreditos(e):
                updateUserInfo()
                switch_view(page,init_form)
                return

            resp = requests.post("https://5n2aczmdhfw7lbu32kgmnuhhdq0bmqfz.lambda-url.sa-east-1.on.aws/",json={"USUARIO":getCache(page,"UserInfo")['USUARIO'],"QUANTIDADE":quantidade})
            navegador = criar_form(
                    superiorInfo, msgRetornoSuperior,LOGO,
                    criar_botao(page,botoesList,"VOLTAR", voltarComprarCreditos)
                )
            page.launch_url(resp.text)
            time.sleep(2)
            switch_view(page,navegador)
            return


        def DESLOGAR(e):
            page.client_storage.remove("UserInfo")
            password_input.value=''
            setCache(page,"TOKEN", '')
            switch_view(page,login_form)
            return
        
        # PAGINA LOGIN

        def updateCreditosValor(e): #ATUALIZA O TEMPO DE MAQUINA PARA EXIBIR PARA O USUARIO
            quantidadeCreditos.value = e.data.replace(",",".")
            quantidadeCreditos.update()
            return

        def ajustarComponentes(dados,largura=None):
            largura = json.loads(dados.data)['width'] if largura==None else largura
            setCache(page,"largura",largura)
            if largura>800: 
                largura = 800
                LOGO.width = 800
            def ajustButton(x,largura=largura*0.9):
                x.width = largura
                x.content.size = largura / 10

            iconHome.icon_size=largura/8
            iconReload.icon_size=largura/8
            text_superior.size=largura/15
            for botao in botoesList:
                ajustButton(botao)
            ajustButton(SairButton,largura * 0.6)
            ajustButton(ADM_MODE,largura * 0.6)
            page.update()  # Atualiza a interface

        
        userInfo = getCache(page,"UserInfo")
        login_form = criar_form(
            ft.Text("", size=21, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            LOGO, ft.Text("Login", size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white'),
            username_input := ft.TextField(label=ft.Text("Usuário/EMAIL",color='white'), autofocus=True, value=userInfo['USUARIO'] if userInfo!=None and "USUARIO" in userInfo.keys() else "", text_align=ft.TextAlign.LEFT,text_size=25,color='white',border_color='white'),
            password_input := ft.TextField(label=ft.Text("Senha",color='white'), password=True, can_reveal_password=True, value='', text_align=ft.TextAlign.LEFT,text_size=25,color='white',border_color='white'),
            botaoLogin := criar_botao(page,botoesList,"Entrar", lambda x:login(x)),
            ft.TextButton("Criar uma conta", on_click=lambda e: switch_view(page,register_form),icon_color='white'),
            ft.TextButton("Esqueci a senha", on_click=lambda e: switch_view(page,redefinirSenhaForm),icon_color='white'),
            loginMsg := ft.Text("", color="red", text_align=ft.TextAlign.CENTER,size=25),
        )
        redefinirSenhaForm = criar_form(
            LOGO, ft.Text("Redefinir senha", size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white'),
            esqueci_username_input := ft.TextField(label=ft.Text("Usuário",color='white'), autofocus=True, text_align=ft.TextAlign.LEFT,text_size=25,color='white',border_color='white'),
            esqueci_Email_input := ft.TextField(label=ft.Text("Email",color='white'), autofocus=False, text_align=ft.TextAlign.LEFT,text_size=25,color='white',border_color='white'),
            esqueci_birth_date_inputButton := ft.ElevatedButton("SELECIONE A DATA DE NASCIMENTO",icon=ft.Icons.CALENDAR_MONTH,on_click=lambda e: page.open(ft.DatePicker(first_date=datetime(year=1900, month=1, day=1),last_date=datetime.today(),on_change=atualizaDataRedefinicao)),color='black'),
            esqueci_RegisterMsg := ft.Text("", text_align=ft.TextAlign.CENTER,color='white',size=25),
            esqueciSenhaBtn := criar_botao(page,botoesList,"Redefinir Senha", redefinir_senha),
            ft.TextButton("Já resetou a senha? Login", on_click=lambda e: switch_view(page,login_form))
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
            birth_date_inputButton := ft.ElevatedButton("SELECIONE A DATA DE NASCIMENTO",icon=ft.Icons.CALENDAR_MONTH,on_click=lambda e: page.open(ft.DatePicker(first_date=datetime(year=1900, month=1, day=1),last_date=datetime.today(),on_change=atualizaData)),color='black'),
            RegisterMsg := ft.Text("", text_align=ft.TextAlign.CENTER,color='white',size=25),
            registerButon := criar_botao(page,botoesList,"Cadastrar", register),
            ft.TextButton("Já tem uma conta? Login", on_click=lambda e: switch_view(page,login_form))
        )

        #PARTE DE LIBERACAO MAQUINA

        escolher_maquina = criar_form(
            superiorInfo, msgRetornoSuperior, LOGO,
            codigoMaquina := ft.TextField(label=ft.Text("DIGITE O NÚMERO DA MÁQUINA",color='white'), autofocus=True, value='1', text_align=ft.TextAlign.CENTER,text_size=30,keyboard_type=ft.KeyboardType.NUMBER,color='white',border_color='white'),
            botaoConfirmMaq := criar_botao(page,botoesList,"Confirmar", obterInfoMaquina)
        )

        maqInfo = ft.Text(size=21, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white')
        descricao_maquina = criar_form(
            superiorInfo, 
            LOGO, 
            msgRetornoSuperior, 
            creditosSelecionados := ft.TextField(label=ft.Text("DIGITE O VALOR QUE DESEJA UTILIZAR DO SALDO:",color='white'), autofocus=False,value=0, text_align=ft.TextAlign.CENTER,text_size=30,keyboard_type=ft.KeyboardType.NUMBER,on_change=updateTempoMaquina,color='white',border_color='white'),
            ft.Container(maqInfo,border=ft.border.all(2, ft.Colors.GREY_500),border_radius=10,alignment=ft.alignment.center),
            iniciarButton := criar_botao(page,botoesList,"INICIAR", iniciar_tempo)
        )

        maquina_form_suced = criar_form(
            superiorInfo, 
            LOGO, 
            msgRetornoSuperior, 
            ft.Text("MÁQUINA LIBERADA!\n Boa diversão.",size=40, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white'),
            voltarButton := criar_botao(page,botoesList,"VOLTAR", lambda x:switch_view(page,init_form))
        )

        compraCreditos_form = criar_form(
            superiorInfo, msgRetornoSuperior, LOGO,
            ft.Text("Digite o valor em reais para comprar créditos.", size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white'),
            quantidadeCreditos := ft.TextField(autofocus=True, text_align=ft.TextAlign.CENTER,text_size=30,keyboard_type=ft.KeyboardType.NUMBER,color='white',border_color='white',on_change = updateCreditosValor),
            botaoComprarCreditos := criar_botao(page,botoesList,"Confirmar", comprarCreditos)  # Implemente a lógica de compra aqui
        )

        def open_pdf(pdf_path):
            page.launch_url(pdf_path)
            page.update()



        inscricaoFinalizada = criar_form(
            superiorInfo, 
            LOGO, 
            msgRetornoSuperior, 
            TextInscricao  := ft.Text("Inscrição finalizada!",size=40, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white'),
            voltarButtonInscricao := criar_botao(page,botoesList,"VOLTAR", lambda x:switch_view(page,init_form))
        )

        def inscreverCampeonato(item):
            resp = requests.post("https://agephcxlxb7ah2fsmsmrrmmgd40acodq.lambda-url.sa-east-1.on.aws/",json={"USUARIO":getCache(page,"UserInfo")['USUARIO'],"TORNEIO":(item['NOME'],item['DATA']),"TOKEN":getCache(page,"TOKEN")}).content.decode()
            if "SUCESSO" in resp:
                time.sleep(0.5)
                updateUserInfo()
                TextInscricao.value = "Inscrição finalizada com sucesso!"
            else:
                TextInscricao.value = resp
            return
        
        def getTorneios():
            resp = requests.post("https://agephcxlxb7ah2fsmsmrrmmgd40acodq.lambda-url.sa-east-1.on.aws/",json={"LISTAR":True}).json()
            campeonatosDados = []
            campeonatosDadosADM = []
            for item in resp:
                if not getCache(page,"UserInfo")['USUARIO'] in [x['USUARIO'] for x in item['INSCRITOS']]:
                    buttonInscricao = ft.TextButton(content=ft.Text("INSCREVER-SE", size=16, color="white", weight=ft.FontWeight.BOLD),on_click=lambda e: criarAlerta(page,{'title':"ACEITAR REGULAMENTO?",'text':"Clicando em sim, você está automaticamente aceitando os termos descritos no regulamento do torneio.",'aceitar':lambda x:inscreverCampeonato(item),'swith':inscricaoFinalizada}))

                else:
                    buttonInscricao = ft.TextButton(content=ft.Text("JA INSCRITO", size=16, color="green", weight=ft.FontWeight.BOLD))

                dados = ft.Column([ft.Row(
                    [
                        ft.Image(src = item['IMAGEM'],width=70,height=100),
                        ft.Text(
                            f"TORNEIO: {item['NOME']}\nInicio: {item['DATA']}\nValor Inscrição:  {item['VALOR_INSCRICAO']} Reais",
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
                
                dadosADM = ft.Column([ft.Row(
                    [
                        ft.Image(src = item['IMAGEM'],width=70,height=100),
                        ft.Text(
                            f"TORNEIO: {item['NOME']}\nInicio: {item['DATA']}\nValor Inscrição:  {item['VALOR_INSCRICAO']} Reais",
                            size=20,
                            color="white",
                            weight=ft.FontWeight.BOLD,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,  # Alinha horizontalmente no centro
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,  # Alinha verticalmente no centro
                    )])
                    
                campeonatosDados.append(ft.Container(dados,border=ft.border.all(3, ft.Colors.WHITE),border_radius=10,alignment=ft.alignment.center))  
                campeonatosDadosADM.append(ft.Container(dadosADM,border=ft.border.all(3, ft.Colors.WHITE),border_radius=10,alignment=ft.alignment.center,on_click=lambda x:(campeonatoList:=createTable(page,(item["INSCRITOS"]),superiorInfo),switch_view(page,campeonatoList))[-1]))  
            campeonadosDisp.controls = campeonatosDados
            inscritosCampeonatosDisp.controls = campeonatosDadosADM
            return None
        
        campeonatoForm = criar_form(
            superiorInfo, msgRetornoSuperior, LOGO,
            ft.Text("Torneios:", size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white'),
            campeonadosDisp := ft.Column(controls=[]),
        )

        VerInscritosCampeonatosForm = criar_form(
            superiorInfo, msgRetornoSuperior, LOGO,
            ft.Text("Torneios:", size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,color='white'),
            inscritosCampeonatosDisp := ft.Column(controls=[]),
        )
        ADMForm = criar_form(
            superiorInfo, msgRetornoSuperior, LOGO,
            INSCRITOS_CAMPEONATOS:=criar_botao(page,botoesList,"Inscritos torneios", lambda e: (getTorneios(), switch_view(page,VerInscritosCampeonatosForm))[-1]),
        )


        def deletarConta(page):
            username = (getCache(page,"UserInfo"))['USUARIO']
            resp = requests.post("https://zfkvumifymjafmmf2ygtnlims40yvvar.lambda-url.sa-east-1.on.aws/",json={"USUARIO":username,"TOKEN":getCache(page,"TOKEN"),"TIPO":'APAGAR_CONTA'})
            if 'DELETADO' in resp.text:
                page.client_storage.remove("UserInfo")
                password_input.value=''
                setCache(page,"TOKEN", '')
            time.sleep(0.5)
            return 
        
        def alterarSenha(page):
            if nova_senha1.value!=nova_senha2.value:
                msg_alterar_senha.value = "As senhas informadas não conferem!"
                msg_alterar_senha.color = 'red'
                msg_alterar_senha.update()
                return
            elif len(nova_senha1.value)<4:
                msg_alterar_senha.value = "A nova senha deve ter pelo menos 4 caracteres"
                msg_alterar_senha.color = 'red'
                msg_alterar_senha.update()
                return
            username = (getCache(page,"UserInfo"))['USUARIO']
            resp = requests.post("https://zfkvumifymjafmmf2ygtnlims40yvvar.lambda-url.sa-east-1.on.aws/",json={"USUARIO":username,"TOKEN":getCache(page,"TOKEN"),"TIPO":'ALTERA_SENHA',"SENHA_ANTIGA":senha_anterior.value,"SENHA_NOVA":nova_senha1.value})
            if 'SENHA ALTERADA' in resp.text:
                senha_anterior.value = ""
                nova_senha1.value = ""
                nova_senha2.value = ""
                msg_alterar_senha.value = "SENHA ALTERADA COM SUCESSO!"
                msg_alterar_senha.color = 'green'
                nova_senha1.update()
                nova_senha2.update()
                senha_anterior.update()
                msg_alterar_senha.update()
            else:
                msg_alterar_senha.value = resp.text
                msg_alterar_senha.color = 'red'
                msg_alterar_senha.update()
            return 
            
        alterarSenhaForm = criar_form(
            superiorInfo, msgRetornoSuperior, LOGO,
            msg_alterar_senha := ft.Text("",color='white',size=25),
            senha_anterior := ft.TextField(label=ft.Text("Senha Antiga",color='white'), password=True, can_reveal_password=True, value='', text_align=ft.TextAlign.LEFT,text_size=25,color='white',border_color='white'),
            nova_senha1 := ft.TextField(label=ft.Text("Nova Senha",color='white'), password=True, can_reveal_password=True, value='', text_align=ft.TextAlign.LEFT,text_size=25,color='white',border_color='white'),
            nova_senha2 := ft.TextField(label=ft.Text("Repetir Nova Senha",color='white'), password=True, can_reveal_password=True, value='', text_align=ft.TextAlign.LEFT,text_size=25,color='white',border_color='white'),
            alterarSenhaBtcConfirm := criar_botao(page,botoesList,"Alterar",lambda x:alterarSenha(page))
        )
        


        minhaConta_form = criar_form(
            superiorInfo, msgRetornoSuperior, LOGO,
            alterarSenhaBtn:=criar_botao(page,botoesList,"Alterar senha", lambda e:switch_view(page,alterarSenhaForm)),
            deletarContaBtn:=criar_botao(page,botoesList,"Deletar conta", lambda e: criarAlerta(page,{'title':'Deletar sua conta?','text':'Todos os seus dados serão deletados do nosso banco de dados.\nOs créditos restantes serão perdidos.','aceitar':deletarConta,'swith':login_form}),cor=ft.Colors.RED),
        )

        init_form = criar_form(
            superiorInfo, msgRetornoSuperior, LOGO,
            liberarMaqButton := criar_botao(page,botoesList,"Liberar Máquina", lambda e: switch_view(page,escolher_maquina)),
            ComprarCreditosButton := criar_botao(page,botoesList,"Comprar Créditos", lambda e: switch_view(page,compraCreditos_form)),
            botaoCampeonatos:=criar_botao(page,botoesList,"Torneios", lambda e: (getTorneios(), switch_view(page,campeonatoForm))[-1] ),
            minhaConta:=criar_botao(page,botoesList,"Minha Conta", lambda e: switch_view(page,minhaConta_form)),
            maquinasAtivas := ft.Column(controls=[]),
            SairButton := criar_botao(page,botoesList,"SAIR",DESLOGAR,cor=ft.Colors.RED,tamanho=200),
            ADM_MODE:=criar_botao(page,botoesList,"ADM", lambda e: switch_view(page,ADMForm),visivel=False,cor=ft.Colors.BLUE),
        
        )
        # def backButton(x):
        #     print(x.data)
        #     if updateUserInfo():
        #         switch_view(page,init_form)
        #     else:
        #         switch_view(page,login_form)
        #     return 
        def backButton(e):
            if e.data=='detach' and page.platform == ft.PagePlatform.ANDROID:
                os._exit(1)

        try:
            # page.window.prevent_close = True
            # page.on_back_pressed = backButton
            if not page.web and page.platform!=ft.PagePlatform.WINDOWS:
                page.on_app_lifecycle_state_change = backButton
            # page.window.on_event = backButton

            # page.on_route_change = backButton
            # page.on_view_pop = backButton
            page.on_resized = ajustarComponentes
            page.locale_configuration = ft.LocaleConfiguration(
            supported_locales=[
                ft.Locale("pt", "BR"),  
                ft.Locale("en", "US"), 
            ],
            current_locale=ft.Locale("de", "DE"),
            )

            page.bgcolor = ft.Colors.BLACK 
            ajustarComponentes(None,page.width)
            page.theme_mode = ft.ThemeMode.LIGHT
            if contemCache(page,"UserInfo") and updateUserInfo(username=getCache(page,"UserInfo")['USUARIO']):
                switch_view(page,init_form)
            else:
                switch_view(page,login_form)
        except:
            print(traceback.format_exc())
            switch_view(page,login_form)
    except:
        page.clean()
        page.add(ft.Text(traceback.format_exc()))

def rodar():
    try:
        ft.app(target=main, view=ft.WEB_BROWSER, assets_dir='assets', host = "0.0.0.0", port=80)
    except: 
        print(traceback.format_exc())
        return rodar()
rodar()

# Executa o aplicativo Flet
# ft.app(target=main)
# ft.app(target=main, view=ft.WEB_BROWSER, assets_dir='assets', port=80)
#flet run --port=80 --host="0.0.0.0" --web
