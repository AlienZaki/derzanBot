# tasks.py
from celery import shared_task
from core.makinaturkiye.makina import MakinaScraper
from core.vivense.vivense import VivenseScraper
import time


@shared_task()
def vivense_scraper_task(host, force_refresh, max_workers):
    print('Task Started...')
    VivenseScraper(host, max_workers=max_workers).run(force_refresh)
    print('Task Finished.')


@shared_task()
def makina_scraper_task(host, force_refresh, max_workers):
    print('Task Started...')
    MakinaScraper(host, max_workers=max_workers).run(force_refresh)
    print('Task Finished.')


