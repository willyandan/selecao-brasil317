import requests
from bs4 import BeautifulSoup as bs

orgaos = []
def getOrgao(html):
    soup = bs(html, 'html.parser')
    divTable = soup.find(id='listagem')
    if not divTable:
        return False
    table = divTable.table.findAll('tr')
    for tr in table[1::]:
        td = tr.findAll('td')
        orgao = {}
        orgao["cod"] = td[0].text.strip()
        orgao["nome"] = td[1].text.strip()
        orgao["gasto_total"] = float(td[2].text.strip().replace('.','').replace(',','.'))
        print("Pegando entidades do orgão:", orgao["nome"])
        orgao["entidades"] = getEntidade(orgao["cod"])
        orgaos.append(orgao)
    return True

def getEntidade(cod):
    j=0
    entidades = []
    while True:
        j+=1
        ent_url = "http://transparencia.gov.br/PortalComprasDiretasOEOrgaoSubordinado.asp?Ano=2017&CodigoOS=%s&Pagina=%i"
        html = requests.get(ent_url%(cod, j))
        if html.status_code != 200:
            break
        soup = bs(html.content, 'html.parser')
        divTable = soup.find(id='listagem')
        if not divTable:
            return False
        table = divTable.table.findAll('tr')
        for tr in table[1::]:
            td = tr.findAll('td')
            entidade = {}
            entidade["nome"] = td[1].text.strip()
            entidade["gasto"] = float(td[2].text.strip().replace('.','').replace(',','.'))
            entidades.append(entidade)
        return entidades
i=0;
while(True):
    i+=1
    url = "http://transparencia.gov.br/PortalComprasDiretasOEOrgaoSuperior.asp?Ano=2017&Ordem=1&Pagina=%i"
    html = requests.get(url%(i))
    if html.status_code != 200:
        break
    res = getOrgao(html.content)
    if not res:
        break
print(orgaos)
