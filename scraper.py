# backend/scraper.py

import asyncio
import re
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

async def scrape_emails_from_google_maps(query: str):
    emails_found = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Recherche Google
        await page.goto(f"https://www.google.com/search?q={query}", timeout=60000)
        await page.wait_for_timeout(3000)

        # Cliquer sur l'onglet "Maps" ou "Lieux"
        try:
            maps_link = await page.query_selector('a[href*="maps.google."]') or \
                        await page.query_selector('a:has-text("Maps")') or \
                        await page.query_selector('a:has-text("Lieux")')

            if maps_link:
                await maps_link.click()
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(3000)
        except:
            pass  # s'il n'y a pas de maps

        # Trouver les cartes de lieux (Google Maps)
        cards = await page.query_selector_all('a:has-text("site web")')

        site_urls = []
        for card in cards:
            try:
                await card.scroll_into_view_if_needed()
                href = await card.get_attribute("href")
                if href:
                    site_urls.append(href)
            except:
                continue

        # Multithread-like: scraping parallèle des sites extraits
        async def scrape_site(url):
            try:
                new_context = await browser.new_context()
                new_page = await new_context.new_page()
                responses = []
                new_page.on("response", lambda r: responses.append(r))
                await new_page.goto(url, timeout=30000)

                emails = set(await extract_emails_from_html(new_page))
                for r in responses:
                    res_emails = await extract_emails_from_response(r)
                    emails.update(res_emails)

                await new_context.close()
                return emails
            except:
                return set()

        tasks = [scrape_site(u) for u in site_urls]
        results = await asyncio.gather(*tasks)

        for result in results:
            emails_found.update(result)

        await browser.close()

    return list(emails_found)

async def extract_emails_from_text(text):
    return list(set(re.findall(EMAIL_REGEX, text)))

async def extract_emails_from_response(response):
    try:
        content_type = response.headers.get("content-type", "")
        if 'application/json' in content_type:
            data = await response.json()
            return await extract_emails_from_text(json.dumps(data))
        elif 'text' in content_type:
            text = await response.text()
            return await extract_emails_from_text(text)
    except:
        return []
    return []  

async def extract_emails_from_html(page):
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")
    return await extract_emails_from_text(soup.get_text())

async def scrape_emails_from_url(url):
    emails_found = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        responses = []
        page.on("response", lambda r: responses.append(r))
        await page.goto(url, wait_until="networkidle", timeout=60000)

        html_emails = await extract_emails_from_html(page)
        emails_found.update(html_emails)

        for response in responses:
            emails_in_response = await extract_emails_from_response(response)
            emails_found.update(emails_in_response)

        await browser.close()

    return list(emails_found)