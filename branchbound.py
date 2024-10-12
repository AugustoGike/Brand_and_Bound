# -*- coding: utf-8 -*-

from mip import * #Pacote usado pra resolver modelos de programação linear
from threading import * #Pacote usado para criar Thread
from graphviz import Digraph #Pacote usado para criar a imagem da arvore dos nos

#Classe No
#Sera utilizando quando o modelo nao gerar uma solucao inteira
#E precisara sair dividindo o dominio para achar uma solucao inteira
class node:

  #Funcao de Iniciação
  #Parametros:
  # m-> Modelo associado ao no
  # valor_solucao -> Valor da solucao gerada pelo modelo
  # variaveis -> Variaveis que geraram a solucao
  def __init__(self,m, valor_solucao, variaveis):
    self.model = m # Armazena o modelo que o no vai ser usado
    self.valor_solucao = valor_solucao  # Armazena o valor da solucao
    self.variaveis = variaveis  # Armazena a lista das variaveis ativadas na solucao
    self.left = None  # Armazena o no do filho a esquerda
    self.right = None  # Armazena o no do filho a direita

  #Função para visualizar a arvore => Dado o no, a sub-arvore abaixo desse no
  #Parametros:
  # graph -> Possivel variavel graph na qual sera criado a imagem do grafico
  def visualize_tree(self, graph=None):
      #Testa a variavel graph foi mandada, pois ela sera usada
      if graph is None:
        graph = Digraph() #Se nao foi, vamos criar uma do zero

      if self.variaveis is None:
        return graph #Se o nó não tiver sub-arvore, so retorna

      #Filtra as variáveis para mostrar apenas aquelas cujo valor seja > 0
      variaveis_filtradas = [(v, valor) for v, valor in self.variaveis if valor != None and valor > 0]

      #Cria o rótulo com o valor da solução e a lista filtrada de variáveis
      label = f"{variaveis_filtradas}\nZ={self.valor_solucao}"

      #Cria um identificador único para o nó usando o id do no
      #Para criar uma arvore sem utilizar um no ja existente
      node_id = str(id(self))

      # Adiciona o nó ao gráfico com o identificador único
      graph.node(node_id, label=label)

      # Se houver filho à esquerda, cria a conexão e faz a recursão
      if self.left is not None:
        if self.left.variaveis is not None:
          left_node_id = str(id(self.left))  # Identificador único do filho à esquerda
          graph.edge(node_id, left_node_id)
          self.left.visualize_tree(graph)

      # Se houver filho à direita, cria a conexão e faz a recursão
      if self.right is not None:
        if self.right.variaveis is not None:
          right_node_id = str(id(self.right))  # Identificador único do filho à direita
          graph.edge(node_id, right_node_id)
          self.right.visualize_tree(graph)

      #Retorna o grafico parea onde foi chamado
      return graph

#Resolve o modelo e retorna o status e os valores das variáveis
def solve(model):
    status = model.optimize() #Resolve o modelo

    #Se o modelo conseguiu ser resolvido
    if status == OptimizationStatus.OPTIMAL:
      #Separa as variaveis em uma lista de tuplas com o nome dela e seu valor
      variaveis = [(v.name, v.x) for v in model.vars if v.x is not None]

      #E retorna o valor da funcao objetivo e as variaveis que geraram essa solucao
      return model.objective_value, variaveis

    #Caso contrario, retorna uma informacao de No nulo
    return 0,None

#Testa a lista de tuplas do paramentro para ver se elas sao inteiras
#Parametros:
# variaveis -> Lista de tupla das Variaveis
def int_solucion_test(variaveis):
    #Vamos andar por todas as solucoes da lista
    for i in range(len(variaveis)):

      #Verificando se tem algum nao inteiro
      if variaveis[i][1] != 0 and variaveis[i][1] != 1: #Como, o dominio das variaveis e binario. Ele so pode assumir esses 2 valores
        return i #Se tiver, retona o valor do indice da variavel que nao e inteira (A primeira que aparecer)

    #Se nao tiver nenhuma, ele sai do for e retorna -1 avisando que todas sao inteiras
    return -1

#Funcao usada pela Thread para resolver o modelo
#Parametros:
# No -> No que vai guardar as informacoes da geracao do modelo
def thread_modelagem(no,modelt):
  #Pede para o modelo nao mandar informaçoes extra sobre como ele ta resolvendo
  modelt.verbose = 0

  #E pede para resolver
  solucao_thread,variaveis_thread = solve(modelt)

  #Se ou gerar um modelo inviavel
  if variaveis_thread == None:

    #Retorna informacoes de um No nulo
    no.valor_solucao = None
    return #Isso e so pra finalizar a thread

  #Caso contrario, salva as informacoes da solucao no no que foi mandado como parametro
  no.valor_solucao = solucao_thread
  no.variaveis = variaveis_thread

  return #Isso e so pra finalizar a thread

#Aqui perguntara ao usuario qual o arquivo que tera as informacoes do modelo
input_file = input("Insira o nome do arquivo de entrada ")
print() #Isso serve para separar no terminal e ficar organizado

model = Model(sense=MAXIMIZE, solver_name=CBC) #Isso define que sera um problema de maximizacao

#Agora, vamos ler o arquivo e salvar todas as informações iniciais do modelo
with open(input_file, 'r') as arquivo:
  linha = arquivo.readline() #Le a primeira linha

  #Salva os valores da primeira linha
  n_variaveis, n_restricoes = map(int, linha.split()) #Isso converte os valores da primeira linha em inteiros

  #Criacao das Variaveis, como eh binario tem limite inferior(0) e superior(1)
  x = [model.add_var(var_type = CONTINUOUS, lb = 0.0,ub = 1.0, name = f"x_{i+1}") for i in range(n_variaveis)]

  #Agora, vamos ler os coeficientes da funcao objetivo e monta-la
  linha = arquivo.readline()

  #Le todos os coeficientes da funcao objetivo
  coeficientes = [int(valor) for valor in linha.split()]

  #E monta o modelo
  model.objective = xsum(coeficientes[i]*x[i] for i in range(n_variaveis))

  #Agora, vamos montar as restricoes
  for i in range(n_restricoes):
    linha = arquivo.readline()

    #Le todos os coeficientes da restricao que ele esta montando atualmente
    coeficientes = [int(valor) for valor in linha.split()]

    #E monta a restricao
    model += xsum(coeficientes[i]*x[i] for i in range(n_variaveis)) <= coeficientes[n_variaveis]

#Vamos criar algumas variaveis para poder encontrar a solucao inteira do modelo
solve_node = [] #Lista que vai armazenar os nos que irao ser resolvidos agora
running_threads = [] #Lista que vai armazenar as threads que vao executar no momento
solucao_inteira = float('-inf') #Variavel que vai armazenar o valor da solucao inteira
variaveis_solucao_inteira = [] #Lista que vai armazenar as variaveis que geraram a solucao inteira

#E entao vamos criar a raiz da arvore com o modelo inicial e informacoes de um no nulo
Raiz = node(model,0,None)

#E colocar esse no na lista de nos para serem resolvidos
solve_node.append(Raiz)

#E cria uma thread para resolver o no.
#Além de colocar essa Thread na lista de Threads para comecarem a ser executada
running_threads.append(Thread(target=thread_modelagem,args=(Raiz,Raiz.model)))

#E comeca um Loop que vai resolver todos nos possiveis ate chegar ao fim das possibilidades de ramificacao
while True:
  #O loop so vai parar quando nao poder mais ramificar o no
  if len(solve_node) == 0:
    break

  #Coloca todas as Threads pra rodarem
  for t in running_threads:
    t.start()

  #Espera todas as Threads terminarem de executar
  for t in running_threads:
    t.join()

  running_threads.clear()  #E esvazia a lista das threads pois todas foram executadas

  #Testa todos os nos pra ver se tem que abrir ou nao
  for n in solve_node:
    solve_node.remove(n) #Tira o no da lista

    #Teste 1 de saida: Resultado Inviavel
    if n.variaveis == None or n.valor_solucao == None:

      #Se entrou aqui, o no e inutil, pois gerou uma solucao inviavel
      #Entao, nao vai precisar ser ramificado
      n.valor_solucao = None
      continue

    #Teste 2 de saida: Se a solucao gerou inteiro ou nao
    indice = int_solucion_test(n.variaveis) #Coloca o no pra ser testado na funcao

    if indice == -1:
      #Se entrou aqui, quer dizer que o no gerou uma solucao inteira
      #Ele nao vai precisar ser ramificado
      #E so precisa testar se gerou uma solucao melhor que a ja encontrada
      if n.valor_solucao > solucao_inteira:
        #Se for melhor que a encontrada, salva o valor da solucao e as variaveis que geraram a solucao
        solucao_inteira = n.valor_solucao
        variaveis_solucao_inteira = n.variaveis

    else:
      #Se entrou aqui, quer dizer que o no nao gerou uma solucao inteira e vai precisar ser ramificado
      modelo = n.model

      #Copia o modelo do no atual para 2 ramificacoes
      model1,model2 = modelo.copy(),modelo.copy()

      #Pra cada modelo, adiciona uma restricao que retira o valor quebrado (Sem retirar solucoes inteira)
      model1 += x[indice] <= 0
      model2 += x[indice] >= 1

      #E cada filho fica com 1 modelo
      n.left = node(model1,0,None)
      n.right = node(model2,0,None)

      #Coloca esses 2 nos na lista de nos para serem resolvidos
      solve_node.append(n.left)
      solve_node.append(n.right)

      #E cria uma Thread pra resolver cada no
      running_threads.append(Thread(target=thread_modelagem,args=(n.left,n.left.model)))
      running_threads.append(Thread(target=thread_modelagem,args=(n.right,n.right.model)))

#Logo apos o loop, mostra ao usuario o valor da solucao inteira
print(f"A solucao Inteira encontrada = {solucao_inteira}")
print("Gerado pelas variaveis")
#E mostra as variaveis que geraram a solucao
for v in variaveis_solucao_inteira:
  print(f"{v[0]} = {v[1]:.2f}")

#E salva em uma imagem (Com formato .png) a arvore dos nos que foram gerados
graph = Raiz.visualize_tree()
graph.render("binary_tree", format="png", cleanup=True)