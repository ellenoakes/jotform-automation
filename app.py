import os, logging
from playwright.sync_api import sync_playwright
import requests

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def download_sheet_as_excel():
    publish_url = os.environ["GOOGLE_SHEET_PUBLISH_URL"].strip()
    resp = requests.get(publish_url)
    resp.raise_for_status()
    local_path = "/tmp/widget_data.xlsx"
    with open(local_path, "wb") as f:
        f.write(resp.content)
    log.info("Google Sheet downloaded as Excel.")
    return local_path

def update_jotform_widget(local_excel_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )
        page = browser.new_page()

        log.info("Logging into JotForm...")
        page.goto("https://www.jotform.com/login", wait_until="networkidle", timeout=60000)
        page.fill('input[name="username"]', os.environ["JOTFORM_EMAIL"])
        page.fill('input[name="password"]', os.environ["JOTFORM_PASSWORD"])
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle", timeout=60000)

        log.info("Opening form builder...")
        page.goto(f"https://www.jotform.com/build/{os.environ['JOTFORM_FORM_ID']}", wait_until="networkidle", timeout=60000)
        page.screenshot(path="/tmp/login_debug.png")

        log.info("Clicking widget...")
        page.click('[data-type="control_spreadsheet"]')
        page.wait_for_selector('input[type="file"]', timeout=60000)
        page.set_input_files('input[type="file"]', local_excel_path)
        page.wait_for_timeout(3000)

        page.keyboard.press("Control+S")
        page.wait_for_timeout(3000)

        browser.close()
        log.info("JotForm widget updated.")

if __name__ == "__main__":
    log.info("Starting update...")
    excel_path = download_sheet_as_excel()
    update_jotform_widget(excel_path)
    log.info("All done!")
