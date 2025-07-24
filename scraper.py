# backend/scraper.py

import asyncio
import re
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

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