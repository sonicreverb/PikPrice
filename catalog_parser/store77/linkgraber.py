from bs4 import BeautifulSoup

HOST = "https://store77.net"


def get_links(html, outputfile):
    soup = BeautifulSoup(html, "html.parser")
    for product_div in soup.find_all("div", class_="blocks_product_fix_w"):
        link = product_div.find("h2", class_="bp_text_info bp_width_fix").find("a").get("href")
        outputfile.write(HOST + link + "\n")


# file = open("html catalog/apple iphones.html", "r", encoding='UTF-8').read()
# with open("links/apple iphones.txt", "w", encoding="UTF-8") as output:
#     get_links(file, output)
#

file = open("html catalog/apple/apple macbooks.html", "r", encoding='UTF-8').read()
with open("links/apple/apple macbooks.txt", "w", encoding="UTF-8") as output:
    get_links(file, output)
