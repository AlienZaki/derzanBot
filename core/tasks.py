# tasks.py
from celery import shared_task
from core.makinaturkiye.test import run
from core.makinaturkiye.exporter import export_products_to_XML
import time


@shared_task()
def mytask():
    print('Task Started...')
    time.sleep(5)
    print('Task Finished')


@shared_task()
def scrape_products():
    print('Task Started...')
    products = run()
    export_products_to_XML(products)
    print('Task Finished')
    # return products

