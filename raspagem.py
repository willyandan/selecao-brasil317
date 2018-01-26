import requests, pymongo
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient

#estabelecendo conexão com o BD
print("Conectando com banco de dados")
client =  MongoClient("mongodb://admin:123@gastos-shard-00-00-82h1e.mongodb.net:27017,gastos-shard-00-01-82h1e.mongodb.net:27017,gastos-shard-00-02-82h1e.mongodb.net:27017/test?ssl=true&replicaSet=gastos-shard-0&authSource=admin")
db = client.gasto
orgaos = db.orgaos

#removendo dados antigos(para não ficar repetindo os mesmos dados)
orgaos.remove({})

#função para pegar os orgãos
def getOrgao(html):
    #colhendo dados da pagina
    soup = bs(html, 'html.parser')
    divTable = soup.find(id='listagem')

    #verificando se pagina tem table para retirar os dados
    if not divTable:
        return False

    #guardando informações da página
    table = divTable.table.findAll('tr')
    for tr in table[1::]:
        td = tr.findAll('td')
        orgao = {}
        orgao["cod"] = td[0].text.strip()
        orgao["nome"] = td[1].text.strip()
        orgao["gasto_total"] = float(td[2].text.strip().replace('.','').replace(',','.'))
        print("Pegando entidades subordinadas do orgão:", orgao["nome"])

        #Pegando dados das entidades
        orgao["entidades"] = getEntidade(orgao["cod"])

        #inserindo dados na collecion
        orgaos.insert(orgao)
    return True

#Pegando entidades subordinadas do orgão
def getEntidade(cod):
    j=0
    entidades = []
    while True:
        #acessando dados da entidade subordinadas
        j+=1
        ent_url = "http://transparencia.gov.br/PortalComprasDiretasOEOrgaoSubordinado.asp?Ano=2017&CodigoOS=%s&Pagina=%i"
        html = requests.get(ent_url%(cod, j))

        #vendo se pagina existe
        if html.status_code != 200:
            break

        #colhendo informações da pagina
        soup = bs(html.content, 'html.parser')
        divTable = soup.find(id='listagem')

        #verificando se pagina tem table para retirar os dados
        if not divTable:
            return False

        #guardando dados da entidade em uma array
        table = divTable.table.findAll('tr')
        for tr in table[1::]:
            td = tr.findAll('td')
            entidade = {}
            entidade["nome"] = td[1].text.strip()
            entidade["gasto"] = float(td[2].text.strip().replace('.','').replace(',','.'))
            entidades.append(entidade)

        #retornando dados para o orgao
        return entidades

#navegando pelas páginas
i=0;
while(True):
    i+=1
    url = "http://transparencia.gov.br/PortalComprasDiretasOEOrgaoSuperior.asp?Ano=2017&Ordem=1&Pagina=%i"
    html = requests.get(url%(i))

    #verificando se página existe
    if html.status_code != 200:
        break

    #pegando dados da página
    res = getOrgao(html.content)
    if not res:
        print("Por algum erro foi impossível achar pegar os dados da página")
        break
    
#mostrando dados do banco
for org in orgaos.find({}):
    print("Código:", org["cod"])
    print("Nome:", org["nome"])
    print("Gasto Total:", org["gasto_total"])
    print("Entidades subordinadas")
    for entidade in org["entidades"]:
        print(" "*5,"Nome:",entidade["nome"])
        print(" "*5,"Entidade:",entidade["gasto"], end="\n\n")
    print("="*40)
    
