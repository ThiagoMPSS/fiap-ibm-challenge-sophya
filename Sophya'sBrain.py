import requests  # Importa a biblioteca "requests", necessária para obter as informações das páginas
from requests.utils import requote_uri  # Importa a função "requote_uri" da biblioteca "requests", pra ficar mais facil de usar, essa função simplesmente converte o texto em URI sem isso os caracteres especiais, espaçamentos, etc... Vão dar problema no URL
import re  # Importa a biblioteca que lida com Regex(Expressões Regulares)
import html

# Variavel que lista os sites que vão ser usados... Ainda não usei ela do jeito certo!
permsites = ["https://escolakids.uol.com.br/", "www.somatematica.com.br"]
# Variavel com o url de busca padrão do google
search_url = "https://www.google.com/search?q="
search_args = "site:"  # Variavel com os parâmetros de busca

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
    regex_string = "<\/?.*?>" # Pattern para identificar tags
    text = re.sub(regex_string, "", html) # Faz a substituição das ocorrencias pelo valor string vazio

    return text

# Função para separar todos os paragrafos do documento html!
def get_paragraphs(tags, paragraphs):
    regex_string = "<p>?[.\s\S]*?<\/p>" # Pattern para identificar as tags de paragrafo e seu conteudo

    for p in re.findall(regex_string, tags): #Encontra todas as ocorrencias e separa numa lista que é varrida pelo laço "for"
        html_conv = html.unescape(p) # Converte os códigos especiais HTML para unicode
        paragraphs.append(remove_tags(html_conv)) # Chama a função remove_tags e adiciona o retorno na lista paragraphs
    return paragraphs

# Separa o html em divs/sections/articles para melhor classificação de importancia no futuro!
def get_page_content(html):
    content = html.text
    regex_string = "(<(div|section|article).*?>[.\s\S]*?<\/(div|section|article)>)"

    paragraphs = []
    section_tags = re.findall(regex_string, content)
    for tag in section_tags:
        content = tag[0]
        paragraphs = get_paragraphs(content, paragraphs)

    return paragraphs

# Função de inicio da função da IBM Cloud
def main(params):
    # Separei essa parte em pequenas camadas pra ficar mais compreensivel!
    # Forma a URL de busca
    url = "{}{}{} {}".format(search_url, search_args,
                             permsites[0], params["perg"])
    url = requote_uri(url)  # Converte o valor em URI
    res = requests.get(url)  # Acessa a página e pega o conteúdo

    html = res.text  # Pega o html
    find_url = get_url_from_google(html)
    find = get_page_content(requests.get(find_url))

    # Retorna o Json para o Watson!
    return {'message': find[0], 'fonte_url': find_url, 'quest': params["perg"]}


print("\n\n\n")

# Simula a interação com o Watson, nas IDEs essa parte é desnecessária para a implementação!
print(main({"perg": "o que é soma?"}))
