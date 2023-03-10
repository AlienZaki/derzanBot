import logging
import traceback
from requests_html import HTMLSession
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from core.models import Product, ProductImage
except:
    import os, django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "derzanBot.settings")
    django.setup()
    from core.models import Product, ProductImage


class MakinaScraper:

    def __init__(self, host='localhost:8000', max_workers=10):
        self.session = HTMLSession()
        self.host = host
        logging.basicConfig(
            level=logging.DEBUG,
            datefmt='%Y-%m-%d %H:%M:%S',
            format='%(asctime)s %(levelname)s %(message)s',
            # filename='logs.log'
        )
        self.session.headers['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        self.executor = ThreadPoolExecutor(max_workers=max_workers)


    def get_product_details(self, product_url):
        try:
            r = self.session.get(product_url)
            # print(r.status_code)
            data = {'vendor': 'Makina', 'language': 'tr'}
            features = r.html.find('.urun-bilgi-tablo tr')
            features_keys = {
                'İlan No': 'code',
                'Kategori': 'category',
                'Marka': 'brand',
                'Ürün Tipi': 'model_type',
                'Ürün Durumu': 'condition',
                'Menşei': 'origin',
                'Teslim Durumu': 'delivery_status',
                'Kısa Detay': 'guarantee',
            }
            # auto getting features
            for f in features:
                key = f.find('td[class*=tabletitle]', first=True).text.replace(':', '').strip()
                value = f.find('td[class*=tablevalue]', first=True).text
                if key and key in features_keys:
                    data[features_keys[key]] = value

            # data['Vendor URL'] = url
            data['name'] = r.html.find('h1.product-detail__title', first=True).text
            data['code'] = int(data['code'].replace('#', ''))
            data['category'] = 'Industrial Machinery///' + data['category']
            price = r.html.find('.product-detail__price', first=True)
            currency = price.find('i', first=True)
            data['currency'] = currency and currency.attrs['class'][1].replace('fa-', '').replace('-', ' ') or ''
            data['price'] = currency and int(price.find('span')[-1].text.replace('.', '')) or 0
            price_desc = r.html.find('.product-detail__kdv', first=True)
            data['price_description'] = price_desc and price_desc.text or ''
            phone = r.html.find('div[class*=telefon] > a', first=True)
            data['phone'] = phone and phone.text.replace(' ', '') or ''
            whatsapp = r.html.find('[href*="whatsapp.com"]', first=True)
            whatsapp = whatsapp and '+' + whatsapp.attrs['href'].split('phone=')[1].split('&')[0] or ''
            data['whatsapp'] = whatsapp
            data['description'] = r.html.find('#aciklama', first=True).html.replace('\n', '').strip().replace(
                '//s.makina', 'https://s.makina')
            images = ['http:' + img.attrs['src'].replace('s.makinaturkiye.com', self.host) for img in r.html.find('#kresim a > img')]
            data['images'] = images

            # print(res)
            return data
        except Exception as e:
            traceback.print_exc()
            print('=> ERROR:', product_url)

    def get_product_links(self, page_url):
        r = self.session.get(page_url)
        urls = r.html.find('#product-container .product-list-mt__inner > a[class*=mt__link]')
        products_urls = [u.attrs['href'] for u in urls]
        # print(len(products_urls))
        return products_urls

    def get_category_products(self, category_url):
        r = self.session.get(category_url)
        last_page = r.html.find('#listing-container .listbottombar > div')
        last_page = last_page and int(last_page[-1].text.split()[1]) or 1

        # get category pagination
        pagination = [f'{category_url}?page={i}' for i in range(1, last_page+1)]
        logging.info(f'Pages found: {len(pagination)}')


        # get product links from pagination
        futures = []
        product_links = []
        for page in pagination:
            futures.append(self.executor.submit(self.get_product_links, page))
        for future in as_completed(futures):
            product_links.extend(future.result())
        logging.info(f'Product links found: {len(product_links)}')


        # get products from pagination
        # product_urls = []
        # for page in pagination:
        #     product_urls.extend(self.get_product_links(page))
        # logging.info(f'Products found: {len(product_urls)}')

        return product_links

    def get_categories(self):
        r = self.session.get('https://www.makinaturkiye.com/urun-kategori-c-0')
        categories = [c.attrs['href'] for c in r.html.find('div[id*=heading] > a[href*=http]')]
        logging.info(f'Categories: {len(categories)}')
        return categories


    # @profile
    def run(self):
        cats = self.get_categories()
        for cat in cats[:1]:
            category_products = self.get_category_products(cat)
            futures = []
            products_data = []
            for product in category_products[:]:
                futures.append(self.executor.submit(self.get_product_details, product))
            for i, future in enumerate(as_completed(futures), 1):
                data = future.result()
                print(data)
                products_data.append(data)

                # Export
                if i % 10 == 0 or i == len(futures):
                    print('Saving...')
                    # print(products_results)
                    # create a list of Product objects to insert

                    # create a list of Product and ProductImage objects to insert
                    products = []
                    images = []

                    for data in products_data:
                        # create the Product object
                        # print('=>', data)
                        product = Product(
                            vendor=data['vendor'],
                            language=data['language'],
                            name=data['name'],
                            code=data['code'],
                            category=data['category'],
                            brand=data.get('brand'),
                            model_type=data.get('model_type'),
                            condition=data.get('condition'),
                            origin=data.get('origin'),
                            delivery_status=data.get('delivery_status'),
                            guarantee=data.get('guarantee'),
                            currency=data.get('currency'),
                            price=data.get('price'),
                            price_description=data.get('price_description'),
                            phone=data.get('phone'),
                            whatsapp=data.get('whatsapp'),
                            description=data.get('description'),
                        )
                        products.append(product)

                    products_data = []
                    # bulk insert the products into the database
                    Product.objects.bulk_create(products, ignore_conflicts=True)

                    # iterate over the saved products and create the ProductImage objects
                    for product in products:
                        for image_url in data.get('images', []):
                            image = ProductImage(product_id=product.code, image=image_url)
                            images.append(image)

                    # bulk insert the images into the database
                    ProductImage.objects.bulk_create(images, ignore_conflicts=True)
                print('Saved!')

            logging.info(f'Products data scraped: {len(products_data)}')



if __name__ == '__main__':
    bot = MakinaScraper(max_workers=10)
    bot.run()
