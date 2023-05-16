
import requests
from bs4 import BeautifulSoup
import json

class Parser:
    def __init__(self):
        self.dict_gm = {}
        self.lst_text = []
        self.headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                              " Chrome/110.0.0.0 YaBrowser/23.3.3.719 Yowser/2.5 Safari/537.36"
            }

    def get_page(self):
        """
        Парсит страницу с пожеланиями и формирует json
        :return: JSON файл, где внешние ключи - номер страницы
        внутренние ключи - номер записи.
        dict.values = text

        """
        x = 1
        while x <= 20:
            if x == 1:
                url = f"https://pozdravok.com/pozdravleniya/lyubov/dobroe-utro/korotkie/proza.htm"
            else:
                url = f"https://pozdravok.com/pozdravleniya/lyubov/dobroe-utro/korotkie/proza-{x}.htm"
            r = requests.get(url=url, headers=self.headers)
            soup = BeautifulSoup(r.text, "html.parser")
            themes = soup.find_all('p', class_='sfst')
            dct_id = {}
            for theme in themes:
                id = str(theme)[str(theme).index("_") + 1: str(theme).index("_") + 3].replace('"', "")
                dct_id[id] = {
                    "text": theme.text
                }
            self.dict_gm[x] = dct_id
            x += 1

    def output_json(self):
        with open("parser_json.json", 'w') as f:
            json.dump(self.dict_gm, f, indent=4, ensure_ascii=False)

    def get_page_lst(self):
        x = 1
        while x <= 20:
            if x == 1:
                url = f"https://pozdravok.com/pozdravleniya/lyubov/dobroe-utro/korotkie/proza.htm"
            else:
                url = f"https://pozdravok.com/pozdravleniya/lyubov/dobroe-utro/korotkie/proza-{x}.htm"
            r = requests.get(url=url, headers=self.headers)
            soup = BeautifulSoup(r.text, "html.parser")
            themes = soup.find_all('p', class_='sfst')
            for theme in themes:
                self.lst_text.append(theme.text)
            x += 1

    def output_txt(self):
        with open('parser_list.txt', 'w', encoding='utf-8') as f:
            f.write("Z ".join(i for i in self.lst_text))



if __name__ == "__main__":
    parser_lst = Parser()
    parser_lst.get_page_lst()
    parser_lst.output_txt()
