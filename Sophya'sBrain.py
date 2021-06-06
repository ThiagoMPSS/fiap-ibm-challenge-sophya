import requests
from requests.utils import requote_uri
import re

# permsites = ["(www\.)(somatematica\.)(com\.)(br)\/(faq)[\'\"]?([^\'\" >]+)"]
permsites = ["(www\.)(somatematica\.)(com\.)(br)"]
search_url = "https://www.google.com/search?q="
search_args = "site:https://brainly.com.br/"

def getURLFromGoogle(html):
  regex_url = "(url\?q=)[\'\"]?([^\'\">]+)\/[\'\"]?([^\'\">]+)"
  res = re.search(regex_url, html)
  if (res):
    start, end = res.span()

    url = html[start+6:end]
    start, end = re.search("&amp;", url).span()
    url = url[:start]

    # print(html)
    return url
  else:
    print(res)
    return "Nada Encontrado!\n" + html

def main(params):
    # res = requote_uri("{}{}".format(search_url, search_args))
    res = requests.get(requote_uri("{}{} {}".format(search_url, search_args, params["perg"])))

    find = getURLFromGoogle(res.text)


    return { 'message': find, 'quest': params["perg"] }
 
print(main({ "perg": "o que são variaveis?" }))