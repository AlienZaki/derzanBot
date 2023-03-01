# tasks.py
from celery import shared_task
from core.makinaturkiye.makina import MakinaScraper
from core.makinaturkiye.exporter import export_products_to_XML
import time


@shared_task()
def mytask():
    print('Task Started...')
    time.sleep(5)
    print('Task Finished')


@shared_task()
def scrape_products(host, force_refresh):
    print('Task Started...')
    MakinaScraper(host).run(force_refresh)
    print('Task Finished.')
    # return products

