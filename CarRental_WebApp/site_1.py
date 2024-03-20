from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

from sqlalchemy import or_

site = Flask(__name__) # Em site encontra-se o nosso servidor web de Flask
site.config['DEGUB'] = True
site.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/base_dados.db'
db = SQLAlchemy(site) # Cursor para a base de dados SQLite


#Criar a tabela clientes
class Cliente(db.Model):
  __tablename__ = "clientes"
  #identificador de cada cliente (não pode haver dois com o mesmo id, por isso é primary key)
  id = db.Column(db.Integer, primary_key=True)
  #email do cliente, um texto com máximo 200 caracteres
  email = db.Column(db.String(200), unique=True, nullable=False)
  #password do cliente, um texto com máximo 20 caracteres
  password = db.Column(db.String(20), nullable=False)
  #Primeiro Nome, texto com máximo 100 caracteres
  nome = db.Column(db.String(100), nullable=False)
  #Último Nome, texto com máximo 100 caracteres
  apelido = db.Column(db.String(100), nullable=False)
  #Número de contribuinte
  contribuinte = db.Column(db.Integer, unique=True, nullable=False)
  #Data de Nascimento
  nascimento = db.Column(db.Date, nullable=False)
  #Id da reserva associada ao cliente
  reserva = db.Column(db.Integer)

#Criar a tabela carros
class Veiculo(db.Model):
  __tablename__ = "veiculos"
  #identificador de cada cliente (não pode haver dois com o mesmo id, por isso é primary key)
  id = db.Column(db.Integer, primary_key=True)
  #marca do veículo
  marca = db.Column(db.String(100))
  #modelo do veículo
  modelo = db.Column(db.String(100))
  #categoria do veículo(pequeno/médio/grande/SUV/luxo)
  categoria = db.Column(db.String(100))
  #tipo de veiculo(mota/carro)
  veiculo = db.Column(db.String(100))
  #cor do veículo
  cor = db.Column(db.String(100))
  #tipo do motor do veículo
  motor = db.Column(db.String(100))
  #combustivel utilizado do veiculo
  combustivel = db.Column(db.String(100))
  #tipo da transmição do veículo
  transmicao = db.Column(db.String(100))
  #tração do veículo
  tracao = db.Column(db.String(100))
  #número de portas no veículo
  portas = db.Column(db.Integer)
  #número de pessoas que pode levar
  pessoas = db.Column(db.Integer)
  #path da imagem web do veículo
  imagem = db.Column(db.String(250))
  #valor diário do aluguer(600/250/50)
  valor = db.Column(db.Integer)
  #data da ultima revisao
  ultrevisao = db.Column(db.Date)
  #data da proxima revisao
  proxrevisao = db.Column(db.Date)
  #data da proxima legalizaçao
  legalizacao = db.Column(db.Date)
  #boolean caso o veiculo está em manutenção(1/0), default 0
  manutencao = db.Column(db.Boolean)
  #boolean caso o veiculo está alugado(1/0), default 0
  alugado = db.Column(db.Boolean)

#Criar a tabela de reservas
class Reserva(db.Model):
  __tablename__ = "reservas"
  #identificador de cada cliente (não pode haver dois com o mesmo id, por isso é primary key)
  id = db.Column(db.Integer, primary_key=True)
  #id do cliente que fez a reserva
  cliente = db.Column(db.Integer)
  #id do veículo da reserva
  veiculo = db.Column(db.Integer)
  #data de inicio da reserva
  inicio = db.Column(db.Date)
  #data de fim da reserva
  fim = db.Column(db.Date)
  #valor total da reserva tendo em conta o numero de dias e o valor diário
  total = db.Column(db.Integer)

#Criar a tabela de pagamentos
class Pagamento(db.Model):
  __tablename__ = "pagamentos"
  #identificador de cada cliente (não pode haver dois com o mesmo id, por isso é primary key)
  id = db.Column(db.Integer, primary_key=True)
  #id da reserva
  reserva = db.Column(db.Integer)
  #tipo de pagamento feito(dinheiro/cartao de credito)
  forma_pagamento = db.Column(db.String(50))
  #valor total do pagamento
  total = db.Column(db.Integer)
  

with site.app_context():
  #criar as tabelas
  db.create_all()
  #execução das tarefas pendentes da base de dados
  db.session.commit()



#Routes do site
  #Redirecionar para Home page
@site.route('/')
def home():
  return render_template("login.html")

  #Redirecionar para Página login com mensagem de erro
@site.route('/login/<message>')
def login(message):
  return render_template("login.html", error=message)

  #Redirecionar para Página register com mensagem de erro
@site.route('/register/<message>')
def register(message):
  return render_template("register.html", error=message)

  #Redirecionar para Página dos veículos com id do cliente atual
@site.route('/veiculos/<id_cliente>')
def veiculos(id_cliente):
  #verifica se algum carro tem a revisão ou a legalização atrasada, caso tenha, o carro será posto em manutenção
  hoje = datetime.today().strftime('%Y-%m-%d')
  data_atual = (hoje).split('-')
  data_hoje = date(int(data_atual[0]), int(data_atual[1]), int(data_atual[2]))
  veiculos = Veiculo.query.all()
  for veiculo in veiculos:
    if ((veiculo.proxrevisao-data_hoje).days<0) or ((veiculo.legalizacao-data_hoje).days<0):
      veiculo.manutencao=1
      db.session.commit()
  #carregar a página com a lista dos carros disponíveis (carros em manutenção ou alugados não estarão disponíveis)
  lista_veiculos = Veiculo.query.filter(Veiculo.alugado==0, Veiculo.manutencao==0).order_by(Veiculo.id)
  return render_template("veiculos.html", cliente=id_cliente, veiculos=lista_veiculos)

  #Redirecionar para Página filtrar veículos com id do cliente atual
@site.route('/filtrar_veiculos/<id_cliente>', methods=['POST'])
def filtrar_veiculos(id_cliente):
  #carregar a página com os carros filtrados
  #variável para guardar os filtros selecionados
  filtros = [0, 0, 0, 0, 0, 0]
  filtros[0]=request.form.get('pesquisar').lower().split()
  filtros[1]=request.form.getlist('categoria')
  filtros[2]=request.form.getlist('transmissao')
  filtros[3]=request.form.getlist('tipo')
  filtros[4]=request.form.getlist('valor')
  pessoas = request.form.getlist('pessoas')
  #caso haja filtros de número de pessoas que o veículo pode transportar selecionados
  if pessoas!=[]:
    filtros[5]=pessoas[0].split()

  lista_veiculos = Veiculo.query.filter(Veiculo.alugado==0, Veiculo.manutencao==0).order_by(Veiculo.id)
  #caso haja filtros pesquisa
  if (filtros[0]!=[]):
    lista_veiculos = lista_veiculos.filter(or_(Veiculo.marca.in_(filtros[0]), Veiculo.modelo.in_(filtros[0])))
  #caso haja filtros categoria
  if (filtros[1]!=[]):
    lista_veiculos = lista_veiculos.filter(Veiculo.categoria.in_(filtros[1]))
  #caso haja filtros transmissão
  if (filtros[2]!=[]):
    lista_veiculos = lista_veiculos.filter(Veiculo.transmicao.in_(filtros[2]))
  #caso haja filtros tipo de veículo
  if (filtros[3]!=[]):
    lista_veiculos = lista_veiculos.filter(Veiculo.veiculo.in_(filtros[3]))
  #caso haja filtros valor diário  
  if (filtros[4]!=[]):
    lista_veiculos = lista_veiculos.filter(Veiculo.valor.in_(filtros[4]))
  #caso haja filtros número de pessoas
  if (filtros[5]!=0):
    #caso o número de pessoas 7+
    if filtros[5][0]=="7":
      lista_veiculos = Veiculo.query.filter(Veiculo.pessoas>=7)
    #caso o número de pessoas é 1-4 ou 5-6
    else: 
      lista_veiculos = Veiculo.query.filter(Veiculo.pessoas.in_(filtros[5]))
  #carrega a página de veículos com a lista de veículos filtrada
  return render_template("veiculos.html", cliente=id_cliente, veiculos=lista_veiculos)

  #Redirecionar para Página cliente com o id do cliente atual
@site.route('/cliente/<id_cliente>')
def cliente(id_cliente):
  cliente_atual = Cliente.query.filter_by(id=id_cliente).first()
  #caso o cliente não tenha uma reserva feita
  if cliente_atual.reserva == 0:
    return render_template("cliente.html", cliente=cliente_atual)
  else:
    reserva_atual = Reserva.query.filter_by(id=cliente_atual.id).first()
    veiculo_reservado = Veiculo.query.filter_by(id=reserva_atual.veiculo).first()
    pagamento_atual = Pagamento.query.filter_by(reserva=cliente_atual.reserva).first()
    #carrega a página do cliente com a informação da reserva efetuada
    return render_template("cliente.html", cliente=cliente_atual, veiculo=veiculo_reservado, reserva=reserva_atual, pagamento=pagamento_atual)


  #Redirecionar para Página reserva com id do cliente atual, id do carro para alugar e mensagem de erro
@site.route('/reserva/<id_cliente>/<id_veiculo>/<message>')
def reserva(id_cliente,id_veiculo,message):
  cliente_atual = Cliente.query.filter_by(id=id_cliente).first()
  veiculo_atual = Veiculo.query.filter_by(id=id_veiculo).first()
  #caso o cliente já tenha uma reserva, volta para a página do cliente
  if cliente_atual.reserva!=0:
    return redirect(url_for("cliente", id_cliente=id_cliente))
  else:
    if message == "message":
      message = " "
    return render_template("reservar.html", cliente=cliente_atual, veiculo=veiculo_atual, error=message)
  

  #Redirecionar para Página de alterar reserva com id do cliente atual, id do carro alugado e mensagem de erro
@site.route('/editar_reserva/<id_cliente>/<id_veiculo>/<message>')
def editar_reserva(id_cliente,id_veiculo,message):
  #carregar o cliente e veículo da reserva
  cliente_atual = Cliente.query.filter_by(id=id_cliente).first()
  veiculo_atual = Veiculo.query.filter_by(id=id_veiculo).first()
  if message == "message":
    message = " "
  reserva_atual = Reserva.query.filter_by(id=cliente_atual.id).first()
  pagamento_atual = Pagamento.query.filter_by(reserva=cliente_atual.reserva).first()
  #carrega a página de editar a reserva com a informação da reserva que será alterada
  return render_template("editar.html", cliente=cliente_atual, veiculo=veiculo_atual, reserva=reserva_atual, error=message, pagamento=pagamento_atual)


#Funções do site
  #Criar um cliente novo
@site.route('/criar-cliente', methods=['POST'])
def criar():
  #variáveis para guardar informação do cliente
  email_cliente = request.form['inputEmail']
  password_cliente = request.form['inputPassword']
  nome_cliente = (request.form['inputNome']).title()
  apelido_cliente = (request.form['inputApelido']).title()
  contribuinte_cliente = request.form['inputContribuinte']
  nascer = request.form['inputNascimento']
  #Caso o utilizador não preencha todos os campos
  if((email_cliente=="") or (password_cliente=="") or (nome_cliente=="") or (apelido_cliente=="") or (contribuinte_cliente=="") or (nascer=="")):
    return redirect(url_for('register', message="Preencha todos os campos"))
  else:
    cliente_existe = Cliente.query.filter_by(email=email_cliente).first() #guarda o primeiro cliente caso exista na base de dados com o mesmo email
    #Caso o cliente não exista na base de dados
    if cliente_existe==None:
      #Caso a palavra pass tenha pelo menos 6 dígitos
      if len(password_cliente)>=6:
        cliente_existe = Cliente.query.filter_by(contribuinte=contribuinte_cliente).first() #guarda o primeiro cliente caso exista na base de dados com o mesmo nºcontribuinte
        #Caso não exista um cliente com esse número de contribuinte
        if cliente_existe==None:
          #Criar uma variável com a data de hoje
          hoje = datetime.today().strftime('%Y-%m-%d')
          data_atual = (hoje).split('-')
          data_hoje = date(int(data_atual[0]), int(data_atual[1]), int(data_atual[2]))
          #Criar uma variável com a data de nascimento do cliente
          data = (nascer).split('-')
          nascimento_cliente = date(int(data[0]), int(data[1]), int(data[2]))
          #Caso o cliente tenha mais de 18 anos
          if (((data_hoje - nascimento_cliente).days)/365.25)>=18:
            cliente = Cliente(email=email_cliente, password=password_cliente, nome=nome_cliente, apelido=apelido_cliente, contribuinte=contribuinte_cliente, nascimento=nascimento_cliente, reserva=0) #variável onde se vai guardar a informação dada pelo utilizador
            db.session.add(cliente)
            db.session.commit()
            return redirect(url_for('cliente', id_cliente=cliente.id))
          #mensagens de erro caso as condições não sejam cumpridas
          else:
            return redirect(url_for('register', message="Tem de ter mais de 18 anos"))
        else:
          return redirect(url_for('register', message="O nºcontribuinte já está associado a uma conta"))
      else:
        return redirect(url_for('register', message="A password deve conter no mínimo 6 caractéres"))
    else:
      return redirect(url_for('register', message="O email já está associado a uma conta"))


  #Fazer login ou ir para a página de criação de novo cliente
@site.route('/login-cliente', methods=['POST'])
def login_register():
  #Vai para a página para registar um cliente
  if request.form['acao']=="register":
    return redirect(url_for('register', message=" "))
  #Verifica se o cliente existe para fazer login
  else:
    #variáveis colocadas pelo utilizador
    email_cliente = request.form['inputEmail']
    password_cliente = request.form['inputPassword']
    #Caso o utilizador não preencha os dois campos
    if((email_cliente=="") or (password_cliente=="")):
      return redirect(url_for('login', message="Credenciais inválidas"))
    else:
      cliente_existe = Cliente.query.filter_by(email=email_cliente).first() #guarda o primeiro cliente com o email escrito caso exista na base de dados
      #Caso a palavra pass e o utilizador estejam corretos
      if cliente_existe!=None and password_cliente==cliente_existe.password:
        return redirect(url_for('cliente', id_cliente=cliente_existe.id))
      else:
        return redirect(url_for('login', message="Credenciais inválidas"))
      

  #Reservar o veículo
@site.route('/reservar_veiculo/<cliente>/<veiculo>', methods=['POST'])
def reservar_veiculo(cliente,veiculo):
  #variáveis para guardar informação da reserva
  dataInicio = request.form['inicioReserva']
  dataFim = request.form['fimReserva']
  forma_pagamento = request.form.getlist('pagamento')
  if dataInicio=="" or dataFim=="":
    erro = "Preencha todos os campos"
    return redirect(url_for('reserva',id_cliente=cliente, id_veiculo=veiculo, message=erro))
  else:
    #variável para a data de hoje
    hoje = datetime.today().strftime('%Y-%m-%d')
    data_atual = (hoje).split('-')
    data_hoje = date(int(data_atual[0]), int(data_atual[1]), int(data_atual[2]))
    #variável para a data de início da reversa
    inicio_reserva = (dataInicio).split('-')
    inicoReserva = date(int(inicio_reserva[0]), int(inicio_reserva[1]), int(inicio_reserva[2]))
    #variável para a data de fim da reversa
    fim_reserva = (dataFim).split('-')
    fimReserva = date(int(fim_reserva[0]), int(fim_reserva[1]), int(fim_reserva[2]))
    #caso as datas não sejam válidas
    if ((fimReserva-data_hoje).days<0) or ((inicoReserva-data_hoje).days<0) or ((fimReserva-inicoReserva).days<0):
      erro = "Datas inválidas"
      return redirect(url_for('reserva',id_cliente=cliente, id_veiculo=veiculo, message=erro))
    elif forma_pagamento==[]:
      erro = "Selecione uma forma de pagamento"
      return redirect(url_for('reserva',id_cliente=cliente, id_veiculo=veiculo, inicio=inicoReserva, fim=fimReserva, message=erro))
    elif len(forma_pagamento)==2:
      erro = "Selecione apenas uma forma de pagamento"
      return redirect(url_for('reserva',id_cliente=cliente, id_veiculo=veiculo, inicio=inicoReserva, fim=fimReserva, message=erro))
    else:
      #cria uma reserva e pagamento e adiciona na base de dados
      veiculo_atual=Veiculo.query.filter_by(id=veiculo).first()
      veiculo_atual.alugado = 1
      valor_total=((fimReserva-inicoReserva).days+1)*veiculo_atual.valor
      reserva = Reserva(cliente=cliente, veiculo=veiculo, inicio=inicoReserva, fim=fimReserva, total=valor_total)
      db.session.add(reserva)
      cliente_atual = Cliente.query.filter_by(id=cliente).first()
      cliente_atual.reserva = reserva.id
      db.session.commit()
      pagamento = Pagamento(reserva=reserva.id, forma_pagamento=forma_pagamento[0], total=valor_total)
      db.session.add(pagamento)
      db.session.commit()
      return redirect(url_for("cliente", id_cliente=cliente))

  #Alterar a reserva
@site.route('/alterar/<id_cliente>/<id_veiculo>/<id_reserva>/<id_pagamento>', methods=['POST'])    
def alterar(id_cliente,id_veiculo,id_reserva,id_pagamento):
  acao = request.form.get('editar')
  #carrega as informações para alterar na base de dados
  cliente_atual = Cliente.query.filter_by(id=id_cliente).first()
  veiculo_atual = Veiculo.query.filter_by(id=id_veiculo).first()
  reserva_atual = Reserva.query.filter_by(id=id_reserva).first()
  pagamento_atual = Pagamento.query.filter_by(id=id_pagamento).first()
  #caso o utilizador deseje eliminar a reserva
  if acao=="eliminar":
    cliente_atual.reserva = 0
    veiculo_atual.alugado = 0
    db.session.delete(reserva_atual)
    db.session.delete(pagamento_atual)
    db.session.commit()
    return redirect(url_for("cliente", id_cliente=id_cliente))
  else:
    dataInicio = request.form['inicioReserva']
    dataFim = request.form['fimReserva']
    #caso o utilizador queira alterar a data de início e fim da reserva
    if dataFim=="" and dataInicio=="":
      erro = "Preencha pela menos uma data"
      return redirect(url_for('editar_reserva',id_cliente=id_cliente, id_veiculo=id_veiculo, message=erro))
    else:
      #variável para a data de hoje
      hoje = datetime.today().strftime('%Y-%m-%d')
      data_atual = (hoje).split('-')
      data_hoje = date(int(data_atual[0]), int(data_atual[1]), int(data_atual[2]))
      if dataInicio!="":
        #variável para a data de inicio da reversa
        inicio_reserva = (dataInicio).split('-')
        inicioReserva = date(int(inicio_reserva[0]), int(inicio_reserva[1]), int(inicio_reserva[2]))
        if dataFim!="":
          #variável para a data de fim da reversa
          fim_reserva = (dataFim).split('-')
          fimReserva = date(int(fim_reserva[0]), int(fim_reserva[1]), int(fim_reserva[2]))
          #caso as datas não seja válida
          if ((inicioReserva-data_hoje).days<0) or ((fimReserva-inicioReserva).days<0):
            erro = "Data inválida"
            return redirect(url_for('editar_reserva',id_cliente=id_cliente, id_veiculo=id_veiculo, message=erro))
          else:
            reserva_atual.inicio = inicioReserva
            reserva_atual.fim = fimReserva
            valor_total=((fimReserva-inicioReserva).days+1)*veiculo_atual.valor
            pagamento_atual.valor = valor_total
            reserva_atual.total = valor_total
            db.session.commit()
            return redirect(url_for("cliente", id_cliente=id_cliente))
        else:
          #caso a data de início de reserva não seja válida
          if ((inicioReserva-data_hoje).days<0) or ((reserva_atual.fim-inicioReserva).days<0):
            erro = "Data inválida"
            return redirect(url_for('editar_reserva',id_cliente=id_cliente, id_veiculo=id_veiculo, message=erro))
          else:
            reserva_atual.inicio = inicioReserva
            valor_total=((reserva_atual.fim-inicioReserva).days+1)*veiculo_atual.valor
            pagamento_atual.valor = valor_total
            reserva_atual.total = valor_total
            db.session.commit()
            return redirect(url_for("cliente", id_cliente=id_cliente))
      #caso o utilizador só queria alterar a data de fim da reserva
      elif dataFim!="":
          #variável para a data de fim da reversa
          fim_reserva = (dataFim).split('-')
          fimReserva = date(int(fim_reserva[0]), int(fim_reserva[1]), int(fim_reserva[2]))
          #caso a data de fim de reserva não seja válida
          if ((fimReserva-reserva_atual.inicio).days<0):
            erro = "Data inválida"
            return redirect(url_for('editar_reserva',id_cliente=id_cliente, id_veiculo=id_veiculo, message=erro))
          else:
            reserva_atual.fim = fimReserva
            valor_total=((fimReserva-reserva_atual.inicio).days+1)*veiculo_atual.valor
            pagamento_atual.valor = valor_total
            reserva_atual.total = valor_total
            db.session.commit()
            return redirect(url_for("cliente", id_cliente=id_cliente))


#Iniciar o site
site.run()