import requests, os
import random, traceback
import string
from PIL import Image
from django.conf import settings


def remove_image_watermark(image_url):
    try:
        # print(image_url)
        url = image_url.replace('500x375', '400x300').replace('200x150', '400x300')
        # print(url)
        r = requests.get(url, stream=True)
        image = Image.open(r.raw)
        # print(f"Original size : {image.size}")  # 5464x3640
        image = image.resize((500, 375))
        name = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=35))
        # path = f'media/temp/images/{name}.jpg'
        try:
            directory_path = os.path.join(settings.MEDIA_ROOT, 'images')
        except:
            directory_path = os.path.join('images')
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        file_path = os.path.join(directory_path, f'{name}.jpg')
        image.save(file_path)
        return file_path.replace('app/', '')
    except:
        traceback.print_exc()

    # with open(path, 'wb') as f:
    #     f.write(r.content)
    #     return f'/{path}'



if __name__ == '__main__':

    url = 'https://s.makinaturkiye.com/Product/191741/thumbs/xenon_uv_baski_makinesi-22-500x375.jpg'
    d = remove_image_watermark(url)
    print(d)
