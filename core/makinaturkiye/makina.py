from requests_html import HTMLSession



class MakinaBot:

    def __init__(self):
        self.session = HTMLSession()


    def get_page_products(self, url):
        products = []

        r = self.session.get(url)
        urls = r.html.find('#product-container .product-list-mt__inner > a[class*=mt__link]')
        urls = [u.attrs['href'] for u in urls][:20]
        for url in urls:
            r = self.session.get(url)
            res = {}
            res['url'] = url
            res['title'] = r.html.find('h1.product-detail__title', first=True).text
            res['main_image'] = 'https:' + r.html.find('#myCarousel .item.active img', first=True).attrs['src'].replace(
                '200x150', '400x300')
            specs = r.html.find('.urun-bilgi-tablo tr')
            for s in specs:
                key = s.find('td[class*=tabletitle]', first=True).text
                value = s.find('td[class*=tablevalue]', first=True).text
                res[key] = value

            res['price'] = r.html.find('.product-detail__price', first=True).text
            price_desc = r.html.find('.product-detail__kdv', first=True)
            res['price desc'] = price_desc and price_desc.text or ''

            res['phone'] = r.html.find('[href*=tel]', first=True).text.replace(' ', '')
            res['whatsapp'] = '+' + \
                              r.html.find('[href*="whatsapp.com"]', first=True).attrs['href'].split('phone=')[1].split(
                                  '&')[0]
            images = r.html.find('#kresim a > img')
            for i, image in enumerate(images, 1):
                res[f'image {i}'] = 'https:' + image.attrs['src'].replace('200x150', '400x300')
            print(res)
            products.append(res)

        return products



if __name__ == '__main__':
    bot = MakinaBot()
    bot.get_page_products('https://www.makinaturkiye.com/baski-kagit-matbaa-makinalari-ve-ekipmanlari-c-115466?page=1')
