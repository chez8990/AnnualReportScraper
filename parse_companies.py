from bs4 import BeautifulSoup as bs
import pandas as pd

def main(hkexnewsPath, savePath):
    with open(hkexnewsPath, 'r') as f:
        html = f.read()

    bsobj = bs(html, 'html.parser')

    companies = []

    for li in bsobj.find('ul', attrs={'class':'mega-lci-company-list'}).find_all('li'):
        try:
            stockCode = li.find('div', attrs={'class':'mega-lci-stockcode'}).text
            stockName = li.find('div', attrs={'class':'mega-lci-companyname'}).text
            stockRow = [stockCode, stockName]
            companies.append(stockRow)
        except:
            pass
    companies = pd.DataFrame(companies, columns=['Stock Code', 'Stock Name'])
    companies.to_csv(savePath, index=None)



HKEXNEWS_HTML = 'hkexnews.html'
SAVE_PATH = 'companies.csv'

if __name__ == '__main__':
    main(HKEXNEWS_HTML, SAVE_PATH)