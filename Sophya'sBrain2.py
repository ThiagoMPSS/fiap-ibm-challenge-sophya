import requests  # Importa a biblioteca "requests", necessária para obter as informações das páginas
from requests.utils import requote_uri  # Importa a função "requote_uri" da biblioteca "requests", pra ficar mais facil de usar, essa função simplesmente converte o texto em URI sem isso os caracteres especiais, espaçamentos, etc... Vão dar problema no URL
import re  # Importa a biblioteca que lida com Regex(Expressões Regulares)
import html as html_lib

# Simula a header do navegador Chrome no Windows
headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
# Variavel que lista os sites que vão ser usados... Ainda não usei ela do jeito certo!
permsites = ["todamateria.com.br", "escolakids.uol.com.br", "somatematica.com.br", "sobiologia.com.br", "sohistoria.com.br",
             "sogeografia.com.br", "soportugues.com.br"]
# Variavel com o url de busca padrão do google
pesquisa_url = "https://www.google.com/search?q="
pesquisa_args = "site:"  # Variavel com os parâmetros de busca
whitelist = ["definicao", "resumo-secao", "post-sub-title", "conteudo-texto", "post_internal_text", "content",
             "post__item__internal__body__description__abstract"] # Whitelist de conteúdo, como classes mais usadas, ou ids, names, ...
blacklist = ["clique aqui", "clique para", "saber mais", "entenda", "conheça mais", "saiba", "conheça", "acesse este"] # Blacklist de conteúdo, para identificar conteúdo irrelevante que possa passar pelos outros filtros

# Função para remover todas as Tags html do documento
def remove_tags(html):
    #! regex_string = "<\/?[^(br)]?>"
    regex_pattern = "<\/?.*?>" # Pattern para identificar tags
    text = re.sub(regex_pattern, "", html) # Faz a substituição das ocorrencias pelo valor string vazio
    return text

def remove_script_tags(html):
    regex_pattern = "<script.*<\/script.*>"
    return re.sub(regex_pattern, "", html)

# Limpa o texto
def limpar_texto(texto):
    # Operação condicional para identificar o tipo do parametro passado
    if (type(texto) == str):
        return html_lib.unescape(re.sub("\s{2,}", "", re.sub("['\"\/\t]", "", re.sub("[\r\n]", "<br>", re.sub("<br>", "\n", texto).strip()))))
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
    headers_googlebot = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'} # Simula a header do bot da google!
    res = requests.get(url, headers=headers_googlebot)  # Acessa a página e pega o conteúdo

    html = res.content.decode()  # Pega o html em bytes e decodifica para utf8
    url_encontrado = ler_pagina_google(html)

    return (url_encontrado, html)
#* -------------------------- Fim pesquisa no google -------------------------- #
#* ----------------- Inicio do tratamento na página encontrada ---------------- #
def tratar_pagina_encontrada(url:str):
    res = requests.get(url, headers=headers) # Abre a página
    html = res.content.decode() # Decodifica
    meta_tags = buscar_meta_tags(html)
    return (html, meta_tags)

def separar_paragrafos(html:str):
    regex_string = "<p>?[.\s\S]*?<\/p>" # Pattern para identificar as tags de paragrafo e seu conteudo
    paragrafos = []

    for p in re.findall(regex_string, html): #Encontra todas as ocorrencias e separa numa lista que é varrida pelo laço "for"
        paragrafos.append(limpar_texto(p)) # Chama a função remove_tags e adiciona o retorno na lista paragraphs
    return paragrafos

def checar_black_list(texto:str):
    for v in blacklist:
        if (v.lower() in texto.lower()):
            return True
    
    return False

def buscar_tags_whitelist(html:str):
    t = []
    for s in whitelist:
        regex_pattern = "<(div|article|section).+class=\"{}\".*?>([\s\S]+)<\/.*(div|article|section).*>".format(s)
        tag = re.findall(regex_pattern, html, flags=re.M)
        regex_pattern = "<(div|article|section).+id=\"{}\".*?>([\s\S]+)<\/.*(div|article|section).*>".format(s)
        tag2 = re.findall(regex_pattern, html, flags=re.M)
        tag.extend(tag2)
        if (len(tag) > 0):
            t.extend(tag)
    resposta = ""
    if (len(t) > 0):
        resposta = t[0][1]
    paragrafos = separar_paragrafos(resposta)
    respostas = [remove_tags(paragrafo) for paragrafo in paragrafos]
    return ("whitelist-tag", respostas[0])

def buscar_meta_tags(html:str):
    regex_pattern = "<meta name=(.+) content=(.+).*>"
    meta_tags = re.findall(regex_pattern, html) # Encontra todas as tags meta e retorna em forma de tuplas
    regex_pattern = "<meta property=(.+) content=(.+).*>"
    teste = re.findall(regex_pattern, html)
    meta_tags.extend(teste) # Encontra todas as tags meta e retorna em forma de tuplas
    meta_tags = limpar_texto(meta_tags)
    meta_tags = dict(meta_tags) # Transforma as tuplas em dicionarios
    return meta_tags

def verifica_meta_tags(meta_tags:dict): # Busca a meta tag description e checa se o conteudo não está na blacklist
    metodo = "meta-tag"
    description = ""
    if ("og:description" in meta_tags.keys()):
        description = meta_tags["og:description"]
    elif ("description" in meta_tags.keys()):
        description = meta_tags["description"]

    if (description.endswith("...")):
        description = ""
    return (metodo, description if not(checar_black_list(description)) else "")

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

    pergunta = requote_uri("\"{}\"".format(params["perg"]))
    # Forma a URL de busca
    url = "{}{} {}".format(pesquisa_url, pergunta, sites)

    url_encontrado, html = buscar_no_google(url)
    html_encontrado, meta_tags = tratar_pagina_encontrada(url_encontrado)

    metodo, meta_description = verifica_meta_tags(meta_tags)
    if (len(meta_description) == 0):
        metodo, meta_description = buscar_tags_whitelist(html_encontrado)

    # Retorna o Json para o Watson!
    return {
                'messagem': meta_description if (len(meta_description) > 0) else "Não encontrei uma resposta!",
                'metodo': metodo,
                'url_busca': url,
                'fonte_url': url_encontrado,
                'pergunta': params["perg"]
           }
    #! return {'message': find[0] if (len(find) > 0) else "Não encontrei uma resposta!", 'fonte_url': find_url, 'quest': params["perg"]}


print("\n\n\n")
# Simula a interação com o Watson, nas IDEs, essa parte é desnecessária para a implementação!
print(main({"perg": "Como fazer uma macarronada"}))