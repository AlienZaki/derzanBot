import os
from pathlib import Path
import xml.etree.ElementTree as ET
import pytz
from datetime import datetime
from django.conf import settings


try:
    directory_path = os.path.join(settings.MEDIA_ROOT, 'products')
except:
    directory_path = os.path.join('products')
if not os.path.exists(directory_path):
    os.makedirs(directory_path)
file_path = os.path.join(directory_path, 'makina.xml')
# input(file_path)


def create_new_XML(file_path=file_path):
    # create the root element
    root = ET.Element("Root")

    # create last update element
    tz = pytz.timezone('Europe/Istanbul')
    current_time = datetime.now(tz).strftime('%d-%m-%Y %I:%M %p')
    last_update = ET.SubElement(root, "Last_update")
    last_update.text = current_time

    # create the products element
    products = ET.SubElement(root, "Products")

    # Save the updated XML file
    with open(file_path, 'wb') as f:
        f.write(ET.tostring(root))
    print('Saved:', file_path)


def append_products(products_data, file_path=file_path):
    if not os.path.exists(file_path):
        create_new_XML(file_path)

    # Load the existing XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    for p in products_data:
        # Append the new product to the 'Products' element
        new_product = ET.SubElement(root.find('Products'), 'Product')
        ET.SubElement(new_product, 'Vendor').text = p['Vendor']
        ET.SubElement(new_product, 'Language').text = p['Language']
        ET.SubElement(new_product, 'Productname').text = p['Product name']
        ET.SubElement(new_product, 'Productcode').text = p['Product code']
        ET.SubElement(new_product, 'Category').text = p.get('Category', '')
        ET.SubElement(new_product, 'Brand').text = p.get('Brand', '')
        ET.SubElement(new_product, 'Modeltype').text = p.get('Model type', '')
        ET.SubElement(new_product, 'Origin').text = p.get('Origin', '')
        ET.SubElement(new_product, 'Delivery_status').text = p.get('Delivery status', '')
        ET.SubElement(new_product, 'Guarantee').text = p.get('Guarantee', '')
        ET.SubElement(new_product, 'Currency').text = p.get('Currency', '')
        ET.SubElement(new_product, 'Price').text = p.get('Price', '')
        ET.SubElement(new_product, 'Price_Description').text = p['Price desc']
        ET.SubElement(new_product, 'Phone').text = p.get('Phone', '')
        ET.SubElement(new_product, 'Whatsapp').text = p.get('Whatsapp', '')
        ET.SubElement(new_product, 'Description').text = p['Description']
        images = ET.SubElement(new_product, 'Images')
        for i, image_url in enumerate(p['Images'], 1):
            img = ET.SubElement(images, f'image{i}')
            img.text = image_url

    # Update the 'Last_update' element with the current date and time
    last_update = root.find('Last_update')
    tz = pytz.timezone('Europe/Istanbul')
    last_update.text = datetime.now(tz).strftime('%d-%m-%Y %I:%M %p')

    # Write the updated XML file
    tree.write(file_path)
    print('Saved!')
def export_products_to_XML(products_data, file_path=file_path):
    # create the root element
    root = ET.Element("Root")

    # create last update element
    tz = pytz.timezone('Europe/Istanbul')
    current_time = datetime.now(tz).strftime('%d-%m-%Y %I:%M %p')
    last_update = ET.SubElement(root, "Last_update")
    last_update.text = current_time

    # create the products element
    products = ET.SubElement(root, "Products")


    for p in products_data:
        # Create a new product element
        new_product = ET.SubElement(products, 'Product')

        # Add the sub-elements to the new product element
        ET.SubElement(new_product, 'Vendor').text = p['Vendor']
        ET.SubElement(new_product, 'Language').text = p['Language']
        ET.SubElement(new_product, 'Productname').text = p['Product name']
        ET.SubElement(new_product, 'Productcode').text = p['Product code']
        ET.SubElement(new_product, 'Category').text = p.get('Category', '')
        ET.SubElement(new_product, 'Brand').text = p.get('Brand', '')
        ET.SubElement(new_product, 'Modeltype').text = p.get('Model type', '')
        ET.SubElement(new_product, 'Origin').text = p.get('Origin', '')
        ET.SubElement(new_product, 'Delivery_status').text = p.get('Delivery status', '')
        ET.SubElement(new_product, 'Guarantee').text = p.get('Guarantee', '')
        ET.SubElement(new_product, 'Price').text = p.get('Price', '')
        ET.SubElement(new_product, 'Price_Description').text = p['Price desc']
        ET.SubElement(new_product, 'Phone').text = p.get('Phone', '')
        ET.SubElement(new_product, 'Whatsapp').text = p.get('Whatsapp', '')
        ET.SubElement(new_product, 'Description').text = p['Description']
        images = ET.SubElement(new_product, 'Images')
        for i, image_url in enumerate(p['Images'], 1):
            img = ET.SubElement(images, f'image{i}')
            img.text = image_url


    # Add the new product to the root element
    # root.find('Products').append(new_product)


    # Save the updated XML file
    # tree = ET.ElementTree(root)
    # tree.write(path, encoding='utf-8')

    # Save the updated XML file
    with open(file_path, 'wb') as f:
        f.write(ET.tostring(root))
    print('Saved:', file_path)



if __name__ == '__main__':
    products = [
        {'Vendor': 'Makina', 'Language': 'tr',
         'Vendor URL': 'https://www.makinaturkiye.com/xenon-uv-baski-makinesi-xenon-uv-printing-machine-p-191741',
         'Product name': 'Xenon UV Baskı Makinesi / Xenon UV Printing Machine', 'Product code': '#00191741',
         'Category': 'UV Baskı Makinası', 'Brand': 'Xenon Lazer', 'Model type': 'Satılık', 'Origin': 'Türkiye',
         'Delivery status': 'Stokta Var', 'Guarantee': '1 Yıl Garantili', 'Price': '13.000',
         'Price desc': '+KDV Min. Sipariş 1 Adet', 'Phone': '+902125505565', 'Whatsapp': '+905444384024',
         'Description': '<div id="aciklama" class="clearfix tab-pane fade in active"><p><h2><strong>Xenon Lazer\xa0</strong></h2><h2><strong>Xenon UV Baskı Makinesi / Xenon UV Printing Machine</strong></h2><p>\xa0UV BASKI MAKİNESİ TEKNİK ÖZELLİKLERİ</p><table cellspacing="0"><tbody><tr><td><p>BASKI ALANI</p></td><td><p>:</p></td><td><p>90 x 60cm</p></td></tr><tr><td><p>BASKI YUKSEKLİĞİ\xa0 \xa0</p></td><td><p>:</p></td><td><p>15CM</p></td></tr><tr><td><p>BASKI PROGRAMI\xa0 \xa0</p></td><td><p>:</p></td><td><p>PHOTO PRINT</p></td></tr><tr><td><p>BASKI KAFASI</p></td><td><p>:</p></td><td><p>3 ADET TX800</p></td></tr><tr><td><p>RENK SIRALAMASI</p></td><td><p>:</p></td><td><p>CMYKLCLM+W+V</p><p>(6 ANA RENK + BEYAZ + LAK )</p></td></tr><tr><td><p>TABLA SİSTEMİ\xa0 \xa0 \xa0 \xa0</p></td><td><p>:</p></td><td><p>VAKUMLU TABLA</p></td></tr><tr><td><p>BOYA TANK\xa0 \xa0 \xa0 \xa0 \xa0 \xa0</p></td><td><p>:</p></td><td><p>BOYA DONMA ÖNLEYİCİ ÇALKALAMA SİSTEMİ</p></td></tr><tr><td><p>UYARI SİSTEMİ</p></td><td><p>:</p></td><td><p>BOYA BİTİŞ UYARI SİSTEMİ</p></td></tr><tr><td><p>LED LAMBA SAYISI</p></td><td><p>:</p></td><td><p>3 ADET</p></td></tr><tr><td><p>MALZEME YÜKSEKLİK\xa0AYARI</p></td><td><p>:</p></td><td><p>\xa0</p><p>OTOMATİK</p><p>\xa0</p></td></tr></tbody></table><p>\xa0</p><p>\xa0UV PRINTING MACHINE TECHNICAL SPECIFICATIONS</p><div><table border="1" cellspacing="0"><tbody><tr><td><p>PRINT AREA</p></td><td><p>:</p></td><td><p>90 x 60cm</p></td></tr><tr><td><p>PRINT HEIGHT\xa0 \xa0</p></td><td><p>:</p></td><td><p>15CM</p></td></tr><tr><td><p>PRINT PROGRAM\xa0 \xa0</p></td><td><p>:</p></td><td><p>PHOTO PRINT</p></td></tr><tr><td><p>PRINT HEAD</p></td><td><p>:</p></td><td><p>3 PCS TX800</p></td></tr><tr><td><p>COLOR RANKING</p></td><td><p>:</p></td><td><p>CMYKLCLM+W+V</p><p>(6 MAIN COLOR + WHITE + LACQUER )</p></td></tr><tr><td><p>TABLE SYSTEM\xa0 \xa0 \xa0 \xa0</p></td><td><p>:</p></td><td><p>VACUUM TABLE</p></td></tr><tr><td><p>PAINT TANK\xa0 \xa0 \xa0 \xa0 \xa0 \xa0</p></td><td><p>:</p></td><td><p>PAINT ANTI-FROST RINSE SYSTEM</p></td></tr><tr><td><p>WARNING SYSTEM</p></td><td><p>:</p></td><td><p>PAINT FINISH WARNING SYSTEM</p></td></tr><tr><td><p>NUMBER OF LED LAMPS</p></td><td><p>:</p></td><td><p>3 PIECES</p></td></tr><tr><td><p>MATERIAL HEIGHT\xa0\xa0ADJUSTMENT</p></td><td><p>:</p></td><td><p>\xa0</p><p>AUTOMATIC</p><p>\xa0</p></td></tr></tbody></table></div></p></div>',
         'Images': 'https://127.0.0.1:8000/media/temp/images/SB6u6CQWyyYloC2N4egirjlZHeYO2Aah19x.jpg , https://127.0.0.1:8000/media/temp/images/S71iX9um8wXRh2TQbGFdf62lRd1MrTHnAVd.jpg , https://127.0.0.1:8000/media/temp/images/ahG8VKebhknJ3VI4Grle5UkoDTlKP8zdSGp.jpg , https://127.0.0.1:8000/media/temp/images/oUzAHxD9ef2JsGbH8ThvGqDBpIdtxjOZ3Nm.jpg , https://127.0.0.1:8000/media/temp/images/IQ9t6cwEWiCpqsWSb6tvZ9alSzpkQJcHbf9.jpg , https://127.0.0.1:8000/media/temp/images/8vp4JkICr5LElOYZ8ORV9aFEvjWiZsOe15C.jpg , https://127.0.0.1:8000/media/temp/images/Kr5G2dAmtQlzVYDtc3kzrvtMu13j2XlDJtR.jpg , https://127.0.0.1:8000/media/temp/images/ZZvuk6u2a2uHXLM2MqF0OLaqy1rt85z5XXr.jpg'
         }
    ]
    #
    # export_products_to_XML(products, file_path='file.xml')
    # remove_all_products(file_path='file.xml')