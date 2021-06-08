import requests  # Importa a biblioteca "requests", necessária para obter as informações das páginas
from requests.utils import requote_uri  # Importa a função "requote_uri" da biblioteca "requests", pra ficar mais facil de usar, essa função simplesmente converte o texto em URI sem isso os caracteres especiais, espaçamentos, etc... Vão dar problema no URL
import re  # Importa a biblioteca que lida com Regex(Expressões Regulares)
import html as html_lib

# Variavel que lista os sites que vão ser usados... Ainda não usei ela do jeito certo!
permsites = ["https://todamateria.com.br/", "https://mundoeducacao.uol.com.br/", "https://escolakids.uol.com.br/", "https://somatematica.com.br/"]
# Variavel com o url de busca padrão do google
search_url = "https://www.google.com/search?q="
search_args = "site:"  # Variavel com os parâmetros de busca

#* --------------------------- Tratamento da Página --------------------------- #

# Função que pega a primeira ocorrencia da pesquisa no google!(Aí eu me lembrei do botão "Estou com sorte" '-', vou ver qual a melhor opção!)
def get_url_from_google(html):
    # Variavel com a Pattern do Regex que procura pelo url da página destino nos resultados, básicamente ela procura por 'url?q="$conteudo"' sendo "$conteudo" o link ps: Existe a API do google, mas ela é paga, tem até uma versão free, mas limita a quantidade de buscas então optei pela gambiarra!
    regex_url = "(url\?q=)[\'\"]?([^\'\">]+)\/[\'\"]?([^\'\">]+)"
    # Função que faz a busca no string através do pattern
    res = re.search(regex_url, html)
    if (res):  # Verifica se foi encontrado uma correspondencia se não o valor da variável é None(Nulo)
        # A função "span" retorna uma tupla com os indices de Começo e Fim da correspondencia encontrada!
        start, end = res.span()

        # Aqui eu separo a string adicionando ao indice 6(porque eu não preciso da parte 'url?q=' e o tamanho dela é exatamente 6) ela só foi usada para encontrar a url certa!
        url = html[start+6:end]
        # Procura pelo valor "&amp;" que corresponde ao caractere "&" quando codificado em URI esse é o exato ponto de separação do URL do google para o URL do site destino
        start, end = re.search("&amp;", url).span()
        # Aqui eu separo o url da posição 0 até a de inicio  encontrada anteriormente
        url = url[:start]

        return url  # Retorno o url encontrado!
    else:  # Caso seja nulo, ou a página do google não retornou o esperado, ou nenhum resultado foi encontrado!
        return "Nada Encontrado!"  # Retorno a informação de que nada foi encontrado!

# Função para remover todas as Tags html do documento
def remove_tags(html):
    #! regex_string = "<\/?[^(br)]?>"
    regex_pattern = "<\/?(br|p).*\/?>"
    text = re.sub(regex_pattern, "%?br?%", html)
    regex_pattern = "<\/?.*?>" # Pattern para identificar tags
    text = re.sub(regex_pattern, "", text) # Faz a substituição das ocorrencias pelo valor string vazio
    regex_pattern = "%\?(br)\?%"
    text = re.sub(regex_pattern, "<br>", text)
    regex_pattern = "%\?(p)\?%"
    text = re.sub(regex_pattern, "<p>", text)
    return text

def remove_script_tags(html):
    regex_pattern = "<script.*<\/script.*>"
    return re.sub(regex_pattern, "", html)

def clear_text(text):
    return remove_tags(remove_script_tags(html_lib.unescape(re.sub("\s{2,}", "", text))))

# Função para separar todos os paragrafos do documento html!
def get_paragraphs(tags, paragraphs):
    regex_string = "<p>?[.\s\S]*?<\/p>" # Pattern para identificar as tags de paragrafo e seu conteudo

    for p in re.findall(regex_string, tags): #Encontra todas as ocorrencias e separa numa lista que é varrida pelo laço "for"
        paragraphs.append(clear_text(p)) # Chama a função remove_tags e adiciona o retorno na lista paragraphs
    return paragraphs

# Separa o html em divs/sections/articles para melhor classificação de importancia no futuro!
def get_page_content(page):
    encode = page.encoding
    content = page.content.decode()
    regex_string = "(<(div|section|article|meta).*?>[.\s\S]*?<\/(div|section|article|meta)>)"

    paragraphs = []
    section_tags = re.findall(regex_string, content)
    for tag in section_tags:
        content = tag[0]
        paragraphs = get_paragraphs(content, paragraphs)

    regex_string = "<(script|title)"
    if (len(paragraphs) == 0):
        for tag in section_tags:
            # if (not(re.search(regex_string, tag[0]))):
            tag_clean = clear_text(tag[0]);
            # if (tag_clean != ""):
            paragraphs.append(tag[0])
    
    return paragraphs

def get_page_by_url(url):
    url = requote_uri(url)  # Converte o valor em URI
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
    res = requests.get(url, headers=headers)  # Acessa a página e pega o conteúdo

    html = res.content.decode()  # Pega o html
    find_url = get_url_from_google(html)
    find = get_page_content(requests.get(find_url))

    return (find_url, find, html)

#* -------------------------- Inicialização da Função ------------------------- #
def main(params):
    # Separei essa parte em pequenas camadas pra ficar mais compreensivel!
    # Forma a URL de busca
    url = "{}{}{} {}".format(search_url, search_args,
                             permsites[0], params["perg"])

    find_url, find, html = get_page_by_url(url)

    print(find)

    # Retorna o Json para o Watson!
    return {'message': find[0] if (len(find) > 0) else "Não encontrei uma resposta!", 'fonte_url': find_url, 'quest': params["perg"]}


print("\n\n\n")
# Simula a interação com o Watson, nas IDEs essa parte é desnecessária para a implementação!
print(main({"perg": "O que é universo?"}))
