import csv
from requests_html import HTMLSession
from .utils import *



class MakinaBot:

    def __init__(self, host='localhost:8000'):
        self.session = HTMLSession()
        self.host = host

    def scrape_product_page(self, url):
        r = self.session.get(url)
        res = {'Vendor': 'Makina', 'Language': 'tr'}
        res['Vendor URL'] = url
        res['Product name'] = r.html.find('h1.product-detail__title', first=True).text
        # image_url = 'https:' + r.html.find('#myCarousel .item.active img', first=True).attrs['src']
        # image = remove_image_watermark(image_url)
        # res['main_image'] = image

        features = r.html.find('.urun-bilgi-tablo tr')
        features_keys = {
            'İlan No': 'Product code',
            'Kategori': 'Category',
            'Marka': 'Brand',
            'Ürün Tipi': 'Model type',
            # 'Ürün Durumu': '',
            'Menşei': 'Origin',
            'Teslim Durumu': 'Delivery status',
            # 'Konum': '',
            'Kısa Detay': 'Guarantee',
            # 'Satış Detayı': '',
        }
        for f in features:
            key = f.find('td[class*=tabletitle]', first=True).text.replace(':', '').strip()
            value = f.find('td[class*=tablevalue]', first=True).text

            if key and key in features_keys:
                res[features_keys[key]] = value

        res['Price'] = r.html.find('.product-detail__price', first=True).text
        price_desc = r.html.find('.product-detail__kdv', first=True)
        res['Price desc'] = price_desc and price_desc.text or ''

        res['Phone'] = r.html.find('[href*=tel]', first=True).text.replace(' ', '')
        res['Whatsapp'] = '+' + \
                          r.html.find('[href*="whatsapp.com"]', first=True).attrs['href'].split('phone=')[1].split(
                              '&')[0]

        res['Description'] = r.html.find('#aciklama', first=True).html.replace('\n', '').strip()
        images = r.html.find('#kresim a > img')
        clean_images = []
        for i, image in enumerate(images, 1):
            image_url = 'https:' + image.attrs['src']
            clean_image = f'https://{self.host}{remove_image_watermark(image_url)}'
            clean_images.append(clean_image)

        res['Images'] = ' , '.join(clean_images)
        print(res)
        return res

    def get_page_products(self, url):
        products = []
        r = self.session.get(url)
        urls = r.html.find('#product-container .product-list-mt__inner > a[class*=mt__link]')
        products_urls = [u.attrs['href'] for u in urls]
        for url in products_urls[:5]:
            res = self.scrape_product_page(url)
            products.append(res)

        self.export_to_csv(products)
        return products

    def export_to_csv(self, list_dict):
        field_names = list_dict[0].keys()
        # print(field_names)
        with open(f'media/temp/export/data.csv', 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(list_dict)



if __name__ == '__main__':
    bot = MakinaBot()
    bot.get_page_products('https://www.makinaturkiye.com/baski-kagit-matbaa-makinalari-ve-ekipmanlari-c-115466?page=1')
