import logging
import traceback, time
from requests_html import HTMLSession
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent

ua = UserAgent()

try:
    from core.models import Product, ProductImage, ProductURL, Vendor
    from django.db import transaction
    from django.core.paginator import Paginator
except:
    import os, django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "derzanBot.settings")
    django.setup()
    from core.models import Product, ProductImage, ProductURL, Vendor
    from django.db import transaction
    from django.core.paginator import Paginator
    from django.db.models import Count


class VivenseScraper:

    def __init__(self, host='localhost:8000', max_workers=10, proxy=False):
        self.session = HTMLSession()
        self.host = host
        logging.basicConfig(
            level=logging.DEBUG,
            datefmt='%Y-%m-%d %H:%M:%S',
            format='%(asctime)s %(levelname)s %(message)s',
            # filename='logs.log'
        )
        self.session.headers['user-agent'] = ua.google
        self.proxies = {
            'http': 'http://brd-customer-hl_61f716b8-zone-derzan:ki4qr40s46qg@zproxy.lum-superproxy.io:22225',
            'https': 'https://brd-customer-hl_61f716b8-zone-derzan:ki4qr40s46qg@zproxy.lum-superproxy.io:22225'
        }
        self.proxy = proxy
        self.update_session_proxy()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # create vendor if not exist
        vendor_name = 'Vivense'
        vendor_website = 'https://www.vivense.com'

        try:
            self.vendor = Vendor.objects.get(name=vendor_name)
        except Vendor.DoesNotExist:
            self.vendor = Vendor.objects.create(name=vendor_name, website=vendor_website)

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

    def update_session_proxy(self):
        if self.proxy:
            self.session = HTMLSession()
            self.session.headers['user-agent'] = ua.google
            self.session.proxies = self.proxies
    def save_products(self, products):
        print('Saving...')
        # create a list of Product and ProductImage objects to insert
        product_list = []
        product_image_list = []
        product_variants_list = []

        for data in products:
            # create the Product objects
            # print('=>', data)
            product = Product(
                id=f'{self.vendor}_{data["code"]}',
                vendor=self.vendor,
                variant_group=data['variant_group'],
                variant_key=data['variant_key'],
                variant_value=data['variant_value'],
                url=data['url'],
                name=data['name'],
                code=data['code'],
                category=data['category'],
                currency=data.get('currency'),
                price=data.get('price'),
                discounted_price=data.get('discounted_price'),
                description=data.get('description'),

            )
            product_list.append(product)

            # create the ProductImage objects
            for image_url in data['images']:
                product_image_list.append(ProductImage(product_id=product.pk, url=image_url))


        # Store data
        with transaction.atomic():
            # bulk create the objects
            try:
                Product.objects.bulk_create(product_list, ignore_conflicts=True)
            except Exception:
                traceback.print_exc()
                print(product_list[0].url)

            ProductImage.objects.bulk_create(product_image_list, ignore_conflicts=True)

            # update the Task status to 1 where the Task.product_url matches the product url
            self.vendor.products_urls.filter(url__in=[p.url for p in product_list]).update(status=1)
            print('Saved!')


    def get_attribute_value(self, type, values):
        if type == 'color':
            value = values[0][type] and values[0][type]['title'] and values[0][type]['title']['tr']
        elif type == 'text':
            value = values[0][type] and values[0][type]['tr']
        elif type == 'boolean':
            value = values[0][type]
            value = 'Evet' if value else 'Hayır'
        elif type == 'numberDouble':
            value = values[0][type]
            value = int(value) if value.is_integer() else value
        else:
            value = None
        return value

    def parse_product_data(self, p):
        currencies = {'TRY': 'TL'}
        data = {}
        data['name'] = p['title']['tr']
        data['code'] = p['vsin']
        data['url'] = f'https://app.vivense.com/products/vsin/{p["vsin"]}'
        data['variant_group'] = p['variantId']
        data['variant_key'] = p['variantGroup'] and p['variantGroup']['groups'][0]['attribute']['title']['tr']
        attribute_type = p['variantGroup'] and p['variantGroup']['groups'][0]['attribute']['attributeType']
        data['variant_value'] = p['variantGroup'] and [self.get_attribute_value(type=attribute_type, values=i['attributeValues']) for i in p['variantGroup']['groups'][0]['products'] if i['product']['vsin'] == p['vsin']]
        data['variant_value'] = data['variant_value'] and data['variant_value'][0]
        data['category'] = '///'.join([i['title']['tr'] for i in p['breadcrumbs'][1:]])
        data['discounted_price'] = p['siteData']['prices'][0]['unitPrice']
        data['price'] = p['siteData']['prices'][0]['generalMarketPrice'] or data['discounted_price']
        data['currency'] = currencies[p['siteData']['prices'][0]['currencyCode']]
        data['images'] = ['https://img.vivense.com/' + i['newFileName'] for i in p['media']]


        # print(p)
        attributes = []
        for a in p['attributes']:
            key = a['title']['tr']

            value = a['values'] and a['values'][0] and self.get_attribute_value(type=a['type'], values=a['values'])
            if value:
                attributes.append((key, value))
            # print(key, a['type'], value)

        attributes_html = '\n'.join([f'<tr><th>{key}</th><td>{value}</td></tr>' for key, value in attributes])
        data['description'] = f"""<div class="panel-body" style="display: block;">
                                        <table class="table">
                                            <tbody id="producttables" class="desctab">
                                                {attributes_html}
                                            </tbody>
                                        </table>
                                    </div><br>"""
        elements = ''
        for item in p["dimensions"]:
            title = item["title"] and item["title"]["tr"] or ''
            width = item['widthCm'] and f"{item['widthCm']} cm"
            height = item['heightCm'] and f"{item['heightCm']} cm"
            length = item['lengthCm'] and f"{item['lengthCm']} cm"
            weight = item['weightKg'] and f"{item['weightKg']} kg"
            radius = item['radiusCm'] and f"{item['radiusCm']} cm"
            diameter = item['diameterCm'] and f"{item['diameterCm']} cm"
            elements += f"""<tr><th>{title}</th>"""
            if width: elements += f'<td>{width}</td>'
            if height: elements += f'<td>{height}</td>'
            if length: elements += f'<td>{length}</td>'
            if weight: elements += f'<td>{weight}</td>'
            if radius: elements += f'<td>{radius}</td>'
            if diameter: elements += f'<td>{diameter}</td>'
            elements += '</tr>'

        data['description'] += f"""
                <div class="panel panel-default custom-panel" id="part87">
                    <div class="panel-heading pd-productsize open">Ürün Boyutları</div>
                    <div class="panel-body nopadding" style="display: block;">
                        <table class="table product-feature">
                            <thead><tr><th class="main-header">&nbsp;</th><th>Genişlik</th><th>Derinlik</th><th>Yükseklik</th></tr></thead>
                            <tbody>
                                {elements}
                            </tbody>
                        </table>
                    </div>
                </div>
                """

        return data

    def get_product_details_by_vsin(self, vsin):
        try:
            r = self.session.get(f'https://app.vivense.com/products/vsin/{vsin}')
            data = r.json()['items'][0]
            return self.parse_product_data(data)
        except Exception:
            traceback.print_exc()
            print('ERROR:', url)
    def get_product_details(self, url):
        try:
            self.update_session_proxy()
            r = self.session.get(url)
            if r.status_code == 200:
                data = r.json()['items'][0]
                # get variant and only for the first group
                vsins = data['variantGroup'] and [p['product']['vsin'] for p in data['variantGroup']['groups'][0]['products']]
                if vsins:
                    return [self.get_product_details_by_vsin(vsin) for vsin in vsins]
                else:
                    return [self.parse_product_data(data)]
            else:
                print(r.text)
                print('ERROR:', url)
        except Exception:
            traceback.print_exc()
            print('ERROR:', url)

    def get_product_links(self, page_url):
        products_urls = []
        try:
            r = self.session.get(page_url)
            if r.status_code == 200:
                products_urls = [f'https://app.vivense.com/products/vsin/{i["vsin"]}' for i in r.json()['items']]
            return products_urls
        except Exception:
            traceback.print_exc()
            print('ERROR URL:', page_url)
            return products_urls

    def get_category_products(self, category_url):
        r = self.session.get(category_url)
        size = r.json()['size']
        last_page = size // 32

        # get category pagination
        pagination = [f'{category_url}?page={i}' for i in range(1, last_page + 1)]
        logging.info(f'Pages found: {len(pagination)}')

        # get product links from pagination
        futures = []
        product_links = []
        for page in pagination:
            futures.append(self.executor.submit(self.get_product_links, page))
        for future in as_completed(futures):
            product_links.extend(future.result())
        logging.info(f'Product links found: {len(product_links)}')
        return product_links

    def get_categories(self):
        r = self.session.get('https://app.vivense.com/menu')
        links = self.search_nested_dict(r.json(), 'link')
        categories = [f'https://app.vivense.com/Products/listing/search/{i["alias"]}-c-{i["params"]["vsin"]}'
                      for i in links if 'vsin' in i["params"]]
        return categories

    def flush_products_from_db(self):
        # Update product urls and delete all products
        product_links = []
        print('=> Deleteting Products URLS...')
        self.vendor.products_urls.all().delete()
        print('=> Deleting Products...')
        self.vendor.products.all().delete()

        # get products from categories
        cats = self.get_categories()
        for i, cat in enumerate(cats, 1):
            print(f'=> Categories: [{i}/{len(cats)}]')
            links = self.get_category_products(cat)
            product_links.extend(links)
            self.vendor.products_urls.bulk_create([ProductURL(url=i, vendor=self.vendor, status=0)
                                                   for i in links], ignore_conflicts=True)

    def run(self, force_refresh=False):
        if force_refresh:
            self.flush_products_from_db()

        # get products from db
        product_links = self.vendor.products_urls.filter(status=0).all()
        total_products = product_links.count()
        counter = 0
        print('=> Prodcuts:', total_products)

        chunk_size = 1000
        paginator = Paginator(product_links, per_page=chunk_size)

        for page_num in range(1, paginator.num_pages + 1):
            print('=> PAGE:', page_num)
            page = paginator.page(page_num)

            futures = []
            for product in page[:]:
                futures.append(self.executor.submit(self.get_product_details, product.url))

            products_data = []
            # for i, product in enumerate(page, 1):
            #     product_details = self.get_product_details(product.product_url)

            for i, future in enumerate(as_completed(futures), 1):
                counter += 1
                print(f'=> Products [{counter}/{total_products}]')
                product_details = future.result()
                if product_details and product_details:
                    products_data.extend(product_details)
                    # print(product_details)
                    print('OK')

                # Export
                if i % 100 == 0 or i == len(futures):  # len(page)
                    temp = products_data.copy()
                    products_data = []
                    self.save_products(temp)


if __name__ == '__main__':
    bot = VivenseScraper(max_workers=10, proxy=True)
    bot.run(force_refresh=True)

    # bot.vendor.products_urls.filter(status=1).update(status=0)
    # bot.vendor.products.all().delete()




    # products = bot.get_product_details('https://app.vivense.com/products/vsin/AE3-450')
    # for p in products:
    #     print(p)
    # bot.save_products(products)