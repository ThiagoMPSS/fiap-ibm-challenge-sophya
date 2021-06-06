import requests # Importa a biblioteca "requests", necessária para obter as informações
                # das páginas
from requests.utils import requote_uri # Importa a função "requote_uri" da biblioteca
                                       # "requests", pra ficar mais facil de usar,
                                       # essa função simplesmente converte o texto em URI
                                       # sem isso os caracteres especiais, espaçamentos, etc...
                                       # vão dar problema no URL
import re # Importa a biblioteca que lida com Regex(Expressões Regulares)

permsites = ["www.somatematica.com.br"] # Variavel que lista os sites que vão
                                        # ser usados... Ainda não usei ela do jeito certo!
search_url = "https://www.google.com/search?q=" # Variavel com o url de busca padrão do google
search_args = "site:" # Variavel com os parâmetros de busca

#Função que pega a primeira ocorrencia da pesquisa no google!(Aí eu me lembrei do botão
#"Estou com sorte" '-', vou ver qual a melhor opção!)
def getURLFromGoogle(html):
  regex_url = "(url\?q=)[\'\"]?([^\'\">]+)\/[\'\"]?([^\'\">]+)" # Variavel com a Pattern do
    # Regex que procura pelo url da página destino nos resultados, básicamente ela procura
    # por 'url?q="$conteudo"' sendo "$conteudo" o link
    # ps: Existe a API do google, mas ela é paga, tem até uma versão free,
    # mas limita a quantidade de buscas então optei pela gambiarra!
  res = re.search(regex_url, html) # Função que faz a busca no string através do pattern
  if (res): # Verifica se foi encontrado uma correspondencia se não o valor da variável é
            # None(Nulo)
    start, end = res.span() # A função "span" retorna uma tupla com os indices de
                            # Começo e Fim da correspondencia encontrada!

    url = html[start+6:end] # Aqui eu separo a string adicionando ao indice 6(porque eu
      # não preciso da parte 'url?q=' e o tamanho dela é exatamente 6) ela só foi usada
      # para encontrar a url certa!
    start, end = re.search("&amp;", url).span() # Procura pelo valor "&amp;" que
      # corresponde ao caractere "&" quando codificado em URI esse é o exato ponto de
      # separação do URL do google para o URL do site destino
    url = url[:start] # Aqui eu separo o url da posição 0 até a de inicio
                      # encontrada anteriormente

    return url # Retorno o url encontrado!
  else: # Caso seja nulo, ou a página do google não retornou o esperado, ou nenhum
        # resultado foi encontrado!
    return "Nada Encontrado!" # Retorno a informação de que nada foi encontrado!

# Função de inicio da função da IBM Cloud
def main(params):
    #Separei essa parte em pequenas camadas pra ficar mais compreensivel!
    url = "{}{}{} {}".format(search_url, search_args, permsites[0], params["perg"]) # Forma a URL de busca
    url = requote_uri(url) # Converte o valor em URI
    print(url + "\n\n\n\n")
    res = requests.get(url) # Acessa a página e pega o conteúdo

    html = res.text # Pega o html
    find = getURLFromGoogle(html)


    return { 'message': find, 'quest': params["perg"] } # Retorna o Json para o Watson!
 
print(main({ "perg": "o que são variaveis?" })) #Simula a interação com o Watson, nas IDEs
  #essa parte é desnecessária para a implementação!