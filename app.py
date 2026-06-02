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
        try:
            page.goto("https://www.jotform.com/login", wait_until="networkidle", timeout=60000)
        except Exception as e:
            log.info(f"Goto timed out: {e}")
        page.wait_for_timeout(3000)
        page.screenshot(path="/tmp/login_debug.png")
        log.info(f"Page title: {page.title()}")
        log.info(f"Page URL: {page.url}")

        page.wait_for_selector('#username', timeout=30000)
        page.fill('#username', os.environ["JOTFORM_EMAIL"])
        page.wait_for_selector('#password', timeout=30000)
        page.fill('#password', os.environ["JOTFORM_PASSWORD"])
        page.click('button:has-text("Log in")')
        page.wait_for_load_state("networkidle", timeout=60000)
        page.wait_for_timeout(5000)
        page.screenshot(path="/tmp/after_login.png")
        log.info(f"After login URL: {page.url}")
        log.info("Opening form builder...")
        page.goto(f"https://www.jotform.com/build/{os.environ['JOTFORM_FORM_ID']}", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)
        page.screenshot(path="/tmp/formbuilder.png")

        log.info("Closing popups...")
        try:
            page.click('[aria-label="Close"]', timeout=5000)
        except:
            pass
        try:
            page.keyboard.press("Escape")
        except:
            pass
        page.wait_for_timeout(2000)

        log.info("Clicking widget...")
        page.evaluate("document.querySelector('#id_122').click()")
        page.wait_for_timeout(2000)

        log.info("Opening widget settings...")
        page.click('button:has-text("Widget Settings")')
        page.wait_for_timeout(2000)
        page.screenshot(path="/tmp/widgetsettings.png")

        log.info("Removing existing file...")
        page.click('text=Remove file')
        page.wait_for_timeout(2000)

        log.info("Uploading new file...")
        page.wait_for_selector('input[type="file"]', timeout=30000)
        page.set_input_files('input[type="file"]', local_excel_path)
        page.wait_for_timeout(3000)

        log.info("Clicking UPDATE...")
        page.click('button:has-text("UPDATE")')
        page.wait_for_timeout(3000)

        browser.close()
        log.info("JotForm widget updated.")

if __name__ == "__main__":
    log.info("Starting update...")
    excel_path = download_sheet_as_excel()
    update_jotform_widget(excel_path)
    log.info("All done!")
