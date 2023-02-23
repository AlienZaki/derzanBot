import logging, time
from requests_html import HTMLSession
from concurrent.futures import ThreadPoolExecutor as Pool
from .exporter import export_products_to_XML
import traceback




logging.basicConfig(
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s %(levelname)s %(message)s',
    # filename='logs.log'
)
session = HTMLSession()
host = '127.0.0.1:8000'


def get_categories_urls():
    r = session.get('https://www.makinaturkiye.com/urun-kategori-c-0')
    category_urls = [c.attrs['href'] for c in r.html.find('div[id*=heading] > a[href*=http]')]
    logging.info(f'Categories: {len(category_urls)}')
    return category_urls


def scrape_product_details(url):
    try:
        r = session.get(url)
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


        res['Category'] = 'industrial machinery///' + res['Category']

        res['Price'] = r.html.find('.product-detail__price', first=True).text
        price_desc = r.html.find('.product-detail__kdv', first=True)
        res['Price desc'] = price_desc and price_desc.text or ''

        res['Phone'] = r.html.find('[href*=tel]', first=True).text.replace(' ', '')
        whatsapp = r.html.find('[href*="whatsapp.com"]', first=True)
        whatsapp = whatsapp and '+' + whatsapp.attrs['href'].split('phone=')[1].split('&')[0] or ''
        res['Whatsapp'] = whatsapp

        res['Description'] = r.html.find('#aciklama', first=True).html.replace('\n', '').strip()
        images = r.html.find('#kresim a > img')

        res['Images'] = []
        for i, image in enumerate(images, 1):
            image_url = 'https:' + image.attrs['src']
            clean_image = image_url #f'https://{host}{remove_image_watermark(image_url)}'
            res['Images'].append(clean_image)


        # print(res)
        return res
    except Exception as e:
        traceback.print_exc()

def get_category_pages_urls(category_url):
    r = session.get(category_url)
    last_page = r.html.find('#listing-container .listbottombar > div')
    last_page = last_page and int(last_page[-1].text.split()[1]) or 1
    # print(last_page)
    page_urls = []
    for i in range(1, last_page+1):
        page = f'{category_url}?page={i}'
        # print(page)
        page_urls.append(page)
    logging.info(f'Pages found: {len(page_urls)}')
    return page_urls


def get_page_products_urls(page_url):
    r = session.get(page_url)
    urls = r.html.find('#product-container .product-list-mt__inner > a[class*=mt__link]')
    products_urls = [u.attrs['href'] for u in urls]
    # print(len(products_urls))
    return products_urls

def run():
    start = time.perf_counter()
    cats = get_categories_urls()
    total_pages = []
    with Pool() as pool:
        for pages in pool.map(get_category_pages_urls, cats[:1]):
            total_pages.extend(pages)
            # print(len(total_pages))

    logging.info(f'Total Pages URLs: {len(total_pages)}')
    stop = time.perf_counter()
    print('Time:', stop - start)

    start = time.perf_counter()
    total_products = []
    with Pool() as pool:
        for products in pool.map(get_page_products_urls, total_pages[:1]):
            total_products.extend(products)
            # print(len(total_products))

    logging.info(f'Total products URLs: {len(total_products)}')
    stop = time.perf_counter()
    print('Time:', stop - start)


    products_results = []
    with Pool() as pool:
        for product in pool.map(scrape_product_details, total_products[:1]):
            products_results.append(product)

    print('Exporting...')
    export_products_to_XML(products_results)


if __name__ == '__main__':
    products = run()
    # print(products)
    from exporter import export_products_to_XML
    export_products_to_XML(products, path='tesst.xml')


