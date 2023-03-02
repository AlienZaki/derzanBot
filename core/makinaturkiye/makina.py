import logging
import traceback
from requests_html import HTMLSession
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from core.models import Product, ProductImage, Task
    from django.db import transaction
    from django.core.paginator import Paginator
except:
    import os, django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "derzanBot.settings")
    django.setup()
    from core.models import Product, ProductImage, Task
    from django.db import transaction
    from django.core.paginator import Paginator


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
            data = {'url': product_url, 'vendor': 'Makina', 'language': 'tr'}
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

            price = currency and price.find('span')[-1].text.replace('.', '').replace(',', '') or 0
            price = price.split('-')[-1] if price and '-' in price else price
            data['price'] = int(price)

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
    def run(self, force_refresh=False):

        product_links = []

        if force_refresh:
            # get products from categories
            cats = self.get_categories()
            for cat in cats[:]:
                links = self.get_category_products(cat)
                product_links.extend(links)
                Task.objects.bulk_create([Task(product_url=i) for i in links], ignore_conflicts=True)


        # get products from db
        product_links = Task.objects.all().filter(status=0)

        chunk_size = 1000
        paginator = Paginator(product_links, per_page=chunk_size)

        for page_num in range(1, paginator.num_pages + 1):
            print('=> PAGE:', page_num)
            page = paginator.page(page_num)

            futures = []
            for product in page[:]:
                futures.append(self.executor.submit(self.get_product_details, product.product_url))


            products_data = []
            for i, future in enumerate(as_completed(futures), 1):
                print('OK')
                product_details = future.result()
                products_data.append(product_details)

                # Export
                if i % 25 == 0 or i == len(futures):
                    temp_products_data = products_data
                    products_data = []
                    print('Saving...')
                    # create a list of Product and ProductImage objects to insert
                    product_list = []
                    product_image_list = []

                    for data in temp_products_data:
                        # create the Product objects
                        # print('=>', data)
                        product = Product(
                            vendor=data['vendor'],
                            url=data['url'],
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
                        product_list.append(product)

                        # create the ProductImage objects
                        for image_url in data['images']:
                            product_image = ProductImage(product=product, image=image_url)
                            product_image_list.append(product_image)

                    # Store data
                    with transaction.atomic():
                        # bulk create the objects
                        Product.objects.bulk_create(product_list, ignore_conflicts=True)
                        ProductImage.objects.bulk_create(product_image_list, ignore_conflicts=True)

                        # update the Task status to 1 where the Task.product_url matches the product url
                        Task.objects.filter(product_url__in=[p.url for p in product_list]).update(status=1)
                        print('Saved!')



if __name__ == '__main__':
    bot = MakinaScraper(host='165.22.19.183', max_workers=1)
    bot.run(force_refresh=False)
    # res = bot.get_product_details('https://www.makinaturkiye.com/netmak-fr-2000-s-freze-makinasi-p-213063')
    # print(res)
