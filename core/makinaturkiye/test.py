import logging, time
from requests_html import HTMLSession
from concurrent.futures import ThreadPoolExecutor as Pool




logging.basicConfig(
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s %(levelname)s %(message)s',
    # filename='logs.log'
)
session = HTMLSession()


def get_categories_urls():
    r = session.get('https://www.makinaturkiye.com/urun-kategori-c-0')
    category_urls = [c.attrs['href'] for c in r.html.find('div[id*=heading] > a[href*=http]')]
    logging.info(f'Categories: {len(category_urls)}')
    return category_urls


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

def func():
    start = time.perf_counter()
    cats = get_categories_urls()
    total_pages = []
    with Pool() as pool:
        for pages in pool.map(get_category_pages_urls, cats):
            total_pages.extend(pages)
            # print(len(total_pages))

    logging.info(f'Total Pages URLs: {len(total_pages)}')
    stop = time.perf_counter()
    print('Time:', stop - start)

    start = time.perf_counter()
    total_products = []
    with Pool() as pool:
        for products in pool.map(get_page_products_urls, total_pages[:100]):
            total_products.extend(products)
            # print(len(total_products))

    logging.info(f'Total products URLs: {len(total_products)}')
    stop = time.perf_counter()
    print('Time:', stop - start)

    return total_products


if __name__ == '__main__':
    func()
