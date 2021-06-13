import requests  # Importa a biblioteca "requests", necessária para obter as informações das páginas
from requests.utils import requote_uri  # Importa a função "requote_uri" da biblioteca "requests", pra ficar mais facil de usar, essa função simplesmente converte o texto em URI sem isso os caracteres especiais, espaçamentos, etc... Vão dar problema no URL
import re  # Importa a biblioteca que lida com Regex(Expressões Regulares)
import html as html_lib
import math

# Simula a header do bot da google!
headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
# Variavel que lista os sites que vão ser usados... Ainda não usei ela do jeito certo!
permsites = ["ebiografia.com", "todamateria.com.br", "escolakids.uol.com.br", "somatematica.com.br", "sobiologia.com.br", "sohistoria.com.br",
             "sogeografia.com.br", "soportugues.com.br"]
# Variavel com o url de busca padrão do google
pesquisa_url = "https://www.google.com/search?q="
pesquisa_args = "site:"  # Variavel com os parâmetros de busca
whitelist = ["definicao", "resumo-secao", "post-sub-title", "conteudo-texto", "post_internal_text", "content",
             "post__item__internal__body__description__abstract"] # Whitelist de conteúdo, como classes mais usadas, ou ids, names, ...
blacklist = ["clique", "saber", "entenda", "conheça", "saiba", "conheça", "acesse", "que", "copyright"] # Blacklist de conteúdo, para identificar conteúdo irrelevante que possa passar pelos outros filtros
resposta_tam_min = 140 #Tamanho minimo da resposta, para poder pegar mais paragrafos se for necessário


# Função para remover todas as Tags html do documento
def remove_tags(html):
    #! regex_string = "<\/?[^(br)]?>"
    regex_pattern = "<\/?.*?>" # Pattern para identificar tags
    text = html.replace("<br>", "%br%") # Substitui a tag <br> para que não seja removida durante o tratamento
    text = re.sub(regex_pattern, "", text) # Faz a substituição das ocorrencias pelo valor string vazio
    text = re.sub("(<br>)+", "<br>", text.replace("%br%", "<br>")) # Volta a tag <br> ao normal e remove os excesso da mesma
    return text

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

def remove_acentos(texto):
    comAcentos = "ÄÅÁÂÀÃäáâàãÉÊËÈéêëèÍÎÏÌíîïìÖÓÔÒÕöóôòõÜÚÛüúûùÇç";
    semAcentos = "AAAAAAaaaaaEEEEeeeeIIIIiiiiOOOOOoooooUUUuuuuCc";
    # Percorre todos os caracteres da variavel "comAcentos" e substitui pelo correspondente "semAcentos"
    for i in range(len(comAcentos)):
        texto = texto.replace(comAcentos[i], semAcentos[i])
    return texto

#* ---------------------------- Pesquisa no google ---------------------------- #
def ler_pagina_google(html:str):
    # Variavel com a Pattern do Regex que procura pelo url da página destino nos resultados, básicamente ela procura por 'url?q="$conteudo"' sendo "$conteudo" o link ps: Existe a API do google, mas ela é paga, tem até uma versão free, mas limita a quantidade de buscas então optei pela gambiarra!
    regex_url = "(url\?q=)[\'\"]?([^\'\">]+)\/[\'\"]?([^\'\">]+)"
    # Função que faz a busca no string através do pattern
    resposta_regex = re.search(regex_url, html)
    if (resposta_regex):  # Verifica se foi encontrado uma correspondencia se não o valor da variável é None(Nulo)
        # A função "sp|span.*ma tupla com os indices de Começo e Fim da correspondencia encontrada!
        start, end = resposta_regex.span()

        # Aqui eu separo a string adicionando ao indice 6(porque eu não preciso da parte 'url?q=' e o tamanho dela é exatamente 6) ela só foi usada para encontrar a url certa!
        url = html[start+6:end]
        # Procura pelo valor "&amp;" que corresponde ao caractere "&" quando codificado em URI esse é o exato ponto de separação do URL do google para o URL do site destino
        start, end = re.search("&amp;", url).span()
        # Aqui eu separo o url da posição 0 até a de inicio  encontrada anteriormente
        url = url[:start]

        return url  # Retorno o url encontrado!
    else:  # Caso seja nulo, ou a página do google não retornou o esperado, ou nenhum resultado foi encontrado!
        return False  # Retorno a informação de que nada foi encontrado!

def buscar_no_google(url:str):
    url = requote_uri(url)  # Converte o valor em URI
    res = requests.get(url, headers=headers)  # Acessa a página e pega o conteúdo

    html = res.content.decode()  # Pega o html em bytes e decodifica para utf8
    url_encontrado = ler_pagina_google(html)

    return (url_encontrado, html)
#* -------------------------- Fim pesquisa no google -------------------------- #
#* ----------------- Inicio do tratamento na página encontrada ---------------- #
def buscar_melhor_correspondencia(texto:list, pergunta:str):
    regex_pattern = "(\w+[^\s]\w+)"
    # Separa as palavras da pergunta e verifica se não estão na Blacklist
    palavras_frases = [s if (not(checar_blacklist(s.lower()))) else "" for s in re.findall(regex_pattern, remove_acentos(pergunta))]
    
    # Adiciona frases para a váriavel
    frases = []
    for i in range(len(palavras_frases)): # Percorre todos os itens da váriavel "palavras_frases"
        p = palavras_frases[i]
        if (len(p) == 0):
            continue
        ultima_frase = p # Variavel que armazena a ultima frase adicionada
        for i2 in range(i + 1, len(palavras_frases)):
            p2 = palavras_frases[i2]
            if (len(p2) == 0):
                continue
            ultima_frase = "{} {}".format(ultima_frase, p2)
            frases.append(ultima_frase)
    palavras_frases.extend(frases) # Extende a lista palavras_frases com os itens da lista frases

    # Classifica os itens por quantidade de correspondencia
    classificacoes = {}
    for p in palavras_frases:
        if (len(p) == 0):
            continue
        regex_pattern = "[^\w]({})[^\w]".format(remove_acentos(p)) # Pattern Regex responsavel por identificar a palavra/frase
        for i in range(len(texto)):
            s = texto[i]
            NaBlacklist = False 
            #Verifica se a palavra está na Blacklist
            for p2 in s.split(" "):
                if (p2.lower() in blacklist):
                    NaBlacklist = True
            if (NaBlacklist): # Se estiver na Blacklist ele ignora essa palavra e pula para a proxima
                continue # Ignora o resto do código e vai para o proximo item do loop

            if (re.search(regex_pattern, s, flags=re.IGNORECASE)): # Busca a palavra
                classificacoes[i] = 1 if not (i in classificacoes.keys()) else classificacoes[i] + 1 # Adiciona +1 nas classificações para o item se a palavra foi encontrada
    

    classificacoes = dict(sorted(classificacoes.items(), key=lambda x: x[0])) # Ordena as classificações em ordem crescente pelas keys do dictionary
    classificacoes = sorted(classificacoes.items(), key=lambda x: x[1], reverse=True) # Ordena as classificações em ordem decrescente pelos values do dictionary
    melhor_classificacao = classificacoes[0] if (len(classificacoes) > 0) else [0, 0] # Pega a melhor classificação que TEORICAMENTE estaria na primeira posição e se classificações estiver vazio ele retorna um valor padrão
    resposta = texto[melhor_classificacao[0]]
    regex_pattern = "\W$" # Pattern responsavel por identificar se a palavra termina com uma pontuação
    if (len(resposta) < resposta_tam_min): # Verifica se o paragrafo tem o tamanho minimo
        for i in range(melhor_classificacao[0] + 1, melhor_classificacao[0] + 4): # Se não tiver o tamanho minimo ele adiciona no maximo 4 novos paragrafos
            s = texto[i]
            if (re.search(regex_pattern, s)): # Verifica se a palavra termina com uma pontuação
                resposta = "{}<br>{}".format(resposta, s)
                break

    return resposta if (melhor_classificacao[1] > 0) else ""

def tratar_pagina_encontrada(url:str):
    res = requests.get(url, headers=headers) # Abre a página
    encode = res.encoding
    html = res.content.decode(encode) # Decodifica
    meta_tags = buscar_meta_tags(html)
    return (html, meta_tags)

def separar_paragrafos(html:str):
    regex_pattern = "<p>?[.\s\S]*?<\/p>" # Pattern para identificar as tags de paragrafo e seu conteudo
    paragrafos = []

    for p in re.findall(regex_pattern, html): #Encontra todas as ocorrencias e separa numa lista que é varrida pelo laço "for"
        paragrafos.append(limpar_texto(p)) # Chama a função remove_tags e adiciona o retorno na lista paragraphs
    return paragrafos

def checar_blacklist(texto:str):
    for v in blacklist:
        if (v.lower() in texto.lower()):
            return True
    
    return False

def buscar_tags_whitelist(html:str, pergunta:str):
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
    melhor_correspondencia = buscar_melhor_correspondencia(respostas, pergunta)
    return ("whitelist-tag", melhor_correspondencia if (len(melhor_correspondencia) > 0) else respostas[0])

def buscar_meta_tags(html:str):
    regex_pattern = "<meta name=(.+) content=(.+).*>"
    meta_tags = re.findall(regex_pattern, html) # Encontra todas as tags meta e retorna em forma de tuplas
    regex_pattern = "<meta property=(.+) content=(.+).*>"
    teste = re.findall(regex_pattern, html)
    meta_tags.extend(teste) # Encontra todas as tags meta e retorna em forma de tuplas
    meta_tags = limpar_texto(meta_tags)
    meta_tags = dict(meta_tags) # Transforma as tuplas em dicionarios
    return meta_tags

def verificar_meta_tags(meta_tags:dict): # Busca a meta tag description e checa se o conteudo não está na blacklist
    metodo = "meta-tag"
    description = ""
    if ("og:description" in meta_tags.keys()):
        description = meta_tags["og:description"]
    elif ("description" in meta_tags.keys()):
        description = meta_tags["description"]

    if (description.endswith("...")):
        description = ""
    return (metodo, description if not(checar_blacklist(description)) else "")

#* ------------------ Fim do tratamento na página encontrada ------------------ #
#* ------------------------- Inicio função matematica ------------------------- #
def resolve_equacao_segundo_grau(a, b, c):
    delta = (b**2)-4*a*c # Encontra o Delta
    if (delta < 0):
        return 'Essa equação não tem raíz'

    x1 = (-b+math.sqrt(delta))/(2*a) # Pega o resultado x1
    x2 = (-b-math.sqrt(delta))/(2*a) # Pega o resultado x2
    if (a == 0):
        return 'A não pode ser 0'
    else:
        return 'As raízes da equação são {:.2f} e {:.2f}'.format(x1, x2)

def resolve_conta_matematica(expressao:str):
    expressao = expressao.replace("–", "-")
    equacao2grau_regex = "([+-]?\d*?x²)(\W\d*?x)?(\W\d*)?=0" # Pattern Regex responsavel por identificar uma equação do segundo grau
    t = ""
    if (re.search(equacao2grau_regex, expressao, flags=re.IGNORECASE)):
        expressao = expressao.replace("X", "x")
        equacao2grau_regex = "([+-]?\d*?x²)" # Identifica o atributo A
        regex = re.search(equacao2grau_regex, expressao)
        regex_inicio = 0
        regex_fim = regex.span()[1]
        a = expressao[:regex_fim].replace("x²", "")
        a = a if (len(a) > 0 and re.search("\d", a)) else ("{}{}".format(a, "1")) # Verifica se a letra está sózinha e adiciona o numero "1" se for o caso

        equacao2grau_regex = "(?:[+-]?\d*?x²)(\W\d*?x)?" # Identifica o atributo B
        regex = re.search(equacao2grau_regex, expressao).span(1)
        regex_inicio = regex[0]
        regex_fim = regex[1]
        b = expressao[regex_inicio:regex_fim].replace("x", "")
        b = b if (len(b) > 0 and re.search("\d", b)) else ("{}{}".format(b, "1") if (regex[0] > -1) else "0")# Verifica se a letra está sózinha e adiciona o numero "1" se for o caso, e se B não existir ele resulta num "0"

        equacao2grau_regex = "(?:[+-]?\d*?x²)(?:\W\d*?x)?(\W\d*)?=0" # Identifica o atributo C
        regex = re.search(equacao2grau_regex, expressao).span(1)
        regex_inicio = regex[0]
        regex_fim = regex[1]
        c = expressao[regex_inicio:regex_fim] if (regex[0] > -1) else "0" # Se C não existir ele resulta "0"

        # Converte em inteiros
        a = int(a)
        b = int(b)
        c = int(c)
        return resolve_equacao_segundo_grau(a, b, c)

    else:
        expressao = expressao.replace("x", "*")
        if (re.search("[^-|*|+|x|\/](\()", expressao)):
            expressao = re.sub("(\()", "*(", expressao)
        return str(eval(expressao)) # Compila a String, retorna o resultado da conta e converte para String
#!MathRegex = (\d+(?:[x|*|+|\/|(|-]\d)+\)?)
#!NumberRegex = ([-|*|+|x|\d|\/|(|)|\.|,]+)

#* --------------------------- Fim função matematica -------------------------- #
#* -------------------------- Inicialização da Função ------------------------- #
def main(params):
    retorno_falso = {
                        'resposta': "false"
                    }
    try:
        # Separei essa parte em pequenas camadas pra ficar mais compreensivel!
        #Gera o string com os sites para o filtro no google
        pergunta = params["perg"]
        tipo = "pesquisa"
        if (len(params) > 1):
            tipo = params["tipo"]

        if (tipo == "conta_matematica"):
            pergunta = re.sub("\s", "", pergunta.lower())
            resposta = resolve_conta_matematica(pergunta)
            return {
                        'mensagem': resposta if (resposta) else "",
                        'formula': pergunta,
                        'resposta': "true"
                   }
        else:
            sites = ""
            for site in permsites:
                if (sites == ""):
                    sites = "site:{}".format(site)
                else:
                    sites = "{} OR site:{}".format(sites, site)

            pergunta_uri = requote_uri("\"{}\"".format(pergunta))
            # Forma a URL de busca
            url = "{}{} {}".format(pesquisa_url, pergunta_uri, sites)

            url_encontrado, html = buscar_no_google(url)
            if (url_encontrado == False):
                return retorno_falso

            html_encontrado, meta_tags = tratar_pagina_encontrada(url_encontrado)

            # metodo, meta_description = verifica_meta_tags(meta_tags)
            # if (len(meta_description) == 0):
            metodo, meta_description = buscar_tags_whitelist(html_encontrado, pergunta)

            # Retorna o Json para o Watson!
            return {
                        'mensagem': meta_description if (len(meta_description) > 0) else "",
                        'metodo': metodo,
                        'url_busca': url,
                        'fonte_url': url_encontrado,
                        'pergunta': params["perg"],
                        'resposta': "true"
                }
    except:
        return retorno_falso

print("\n\n\n")
# Simula a interação com o Watson, nas IDEs, essa parte é desnecessária para a implementação!
print(main({
                "perg": "Quem descobriu a energia eletrica?",
                # "tipo": "conta_matematica"
           }))