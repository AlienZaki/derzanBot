import requests
from requests_html import HTMLSession
import re


class VivenseScraper:

    def __init__(self):
        self.session = HTMLSession()
        self.session.headers['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'

    def search_nested_dict(self, nested_dict, search_key):
        """Search for all occurrences of a key in a nested dictionary recursively."""
        matches = []
        for key, value in nested_dict.items():
            if key == search_key:
                matches.append(value)
            elif isinstance(value, dict):
                matches.extend(self.search_nested_dict(value, search_key))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        matches.extend(self.search_nested_dict(item, search_key))
        return matches



    def get_categories(self):
        r = requests.get('https://app.vivense.com/menu')
        links = self.search_nested_dict(r.json(), 'link')
        categories = [{'alias': f'{i["alias"]}-c-{i["params"]["vsin"]}', 'url': f'https://www.vivense.com/{i["alias"]}.html'} for i in links if 'vsin' in i["params"]]
        return categories


    def get_category_products(self, category_alias):
        url = f'https://app.vivense.com/Products/listing/search/{category_alias}'
        r = self.session.get(url)
        print(url)
        print(r.json()['size'])


    def test(self):
        currencies = {'TRY': 'TL'}
        r = self.session.get('https://app.vivense.com/products/vsin/LR3-436')
        p = r.json()['items'][0]
        data = {}
        data['name'] = p['title']['tr']
        data['images'] = ['https://img.vivense.com/' + i['newFileName'] for i in p['media']]
        data['category'] = '///'.join([i['title']['tr'] for i in p['breadcrumbs'][1:]])
        data['listing_price'] = p['siteData']['prices'][0]['unitPrice']
        data['price'] = p['siteData']['prices'][0]['generalMarketPrice'] or data['listing_price']
        data['currency'] = currencies[p['siteData']['prices'][0]['currencyCode']]
        attributes = [(a['title']['tr'], a['values'][0]['text']['tr']) for a in p['attributes']]
        return [data]


if __name__ == '__main__':
    bot = VivenseScraper()
    # categories = bot.get_categories()
    # print(categories)
    # for category in categories:
    #     bot.get_category_products(category['alias'])


    print(bot.test())