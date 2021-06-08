import requests  # Importa a biblioteca "requests", necessária para obter as informações das páginas
from requests.utils import requote_uri  # Importa a função "requote_uri" da biblioteca "requests", pra ficar mais facil de usar, essa função simplesmente converte o texto em URI sem isso os caracteres especiais, espaçamentos, etc... Vão dar problema no URL
import re  # Importa a biblioteca que lida com Regex(Expressões Regulares)
import html as html_lib

# Variavel que lista os sites que vão ser usados... Ainda não usei ela do jeito certo!
permsites = ["https://todamateria.com.br/", "https://mundoeducacao.uol.com.br/", "https://escolakids.uol.com.br/", "https://somatematica.com.br/"]
# Variavel com o url de busca padrão do google
pesquisa_url = "https://www.google.com/search?q="
pesquisa_args = "site:"  # Variavel com os parâmetros de busca
whitelist = ["definicao", ""] # Whitelist de conteúdo, como classes mais usadas, ou ids, names, ...
blacklist = ["clique aqui", "saber mais", "entenda"] # Blacklist de conteúdo, para identificar conteúdo irrelevante que possa passar pelos outros filtros

# Limpa o texto
def limpar_texto(texto):
    # Operação condicional para identificar o tipo do parametro passado
    if (type(texto) == str):
        return html_lib.unescape(re.sub("\s{2,}", "", re.sub("['\"\/]", "", texto)))
    elif (type(texto) == list):
        if (len(texto) > 0):
            if (type(texto[0]) == tuple): # Se forem tuplas dentro da lista ele percorre a lista e limpa os dois valores da tupla, apagando os que forem desnecessários
                ret = []
                for (k, v) in texto:
                    ret.append((limpar_texto(k), limpar_texto(v)))
                return ret
            else: # Se for uma lista ele chama a funcão de novo pra cada string dentro dela
                return [limpar_texto(valor) for valor in texto] # Lambda do loop "For" para deixar o código mais compacto
    
    return texto # No caso de não entrar em nenhuma das condições anteriores ele retorna o mesmo valor

#* ---------------------------- Pesquisa no google ---------------------------- #
def ler_pagina_google(html:str):
    # Variavel com a Pattern do Regex que procura pelo url da página destino nos resultados, básicamente ela procura por 'url?q="$conteudo"' sendo "$conteudo" o link ps: Existe a API do google, mas ela é paga, tem até uma versão free, mas limita a quantidade de buscas então optei pela gambiarra!
    regex_url = "(url\?q=)[\'\"]?([^\'\">]+)\/[\'\"]?([^\'\">]+)"
    # Função que faz a busca no string através do pattern
    resposta_regex = re.search(regex_url, html)
    if (resposta_regex):  # Verifica se foi encontrado uma correspondencia se não o valor da variável é None(Nulo)
        # A função "span" retorna uma tupla com os indices de Começo e Fim da correspondencia encontrada!
        start, end = resposta_regex.span()

        # Aqui eu separo a string adicionando ao indice 6(porque eu não preciso da parte 'url?q=' e o tamanho dela é exatamente 6) ela só foi usada para encontrar a url certa!
        url = html[start+6:end]
        # Procura pelo valor "&amp;" que corresponde ao caractere "&" quando codificado em URI esse é o exato ponto de separação do URL do google para o URL do site destino
        start, end = re.search("&amp;", url).span()
        # Aqui eu separo o url da posição 0 até a de inicio  encontrada anteriormente
        url = url[:start]

        return url  # Retorno o url encontrado!
    else:  # Caso seja nulo, ou a página do google não retornou o esperado, ou nenhum resultado foi encontrado!
        return "Nada Encontrado!"  # Retorno a informação de que nada foi encontrado!

def buscar_no_google(url:str):
    url = requote_uri(url)  # Converte o valor em URI
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'} # Simula a header do bot da google!
    res = requests.get(url, headers=headers)  # Acessa a página e pega o conteúdo

    html = res.content.decode()  # Pega o html em bytes e decodifica para utf8
    url_encontrado = ler_pagina_google(html)

    return (url_encontrado, html)
#* -------------------------- Fim pesquisa no google -------------------------- #
#* ----------------- Inicio do tratamento na página encontrada ---------------- #
def tratar_pagina_encontrada(url:str):
    res = requests.get(url) # Abre a página
    html = res.content.decode() # Decodifica
    meta_tags = buscar_meta_tags(html)
    return (meta_tags)

def checar_black_list(texto:str):
    for v in blacklist:
        if (v.lower() in texto.lower()):
            return True
    
    return False

def buscar_meta_tags(html:str):
    regex_pattern = "<meta name=(.+) content=(.+).*>"
    meta_tags = re.findall(regex_pattern, html) # Encontra todas as tags meta e retorna em forma de tuplas
    meta_tags = limpar_texto(meta_tags)
    meta_tags = dict(meta_tags) # Transforma as tuplas em dicionarios
    return meta_tags

def verifica_meta_tags(meta_tags:dict): # Busca a meta tag description e checa se o conteudo não está na blacklist
    if ("description" in meta_tags.keys()):
        description = meta_tags["description"]
        return description if not(checar_black_list(description)) else ""
    return ""

#* ------------------ Fim do tratamento na página encontrada ------------------ #
#* -------------------------- Inicialização da Função ------------------------- #
def main(params):
    # Separei essa parte em pequenas camadas pra ficar mais compreensivel!
    #Gera o string com os sites para o filtro no google
    sites = ""
    for site in permsites:
        if (sites == ""):
            sites = "site:{}".format(site)
        else:
            sites = "{} OR site:{}".format(sites, site)

    # Forma a URL de busca
    url = "{}{} {}".format(pesquisa_url, params["perg"], sites)

    url_encontrado, html = buscar_no_google(url)
    meta_tags = tratar_pagina_encontrada(url_encontrado)
    meta_description = verifica_meta_tags(meta_tags)

    # Retorna o Json para o Watson!
    return {'message': meta_description if (len(meta_description) > 0) else "Não encontrei uma resposta!", 'fonte_url': url_encontrado, 'quest': params["perg"]}
    #! return {'message': find[0] if (len(find) > 0) else "Não encontrei uma resposta!", 'fonte_url': find_url, 'quest': params["perg"]}


print("\n\n\n")
# Simula a interação com o Watson, nas IDEs, essa parte é desnecessária para a implementação!
print(main({"perg": "O que é função?"}))