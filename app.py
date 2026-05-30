@@ -17,24 +17,28 @@ def download_sheet_as_excel():
    log.info("Google Sheet downloaded as Excel.")
    return local_path

def update_jotform_widget(local_excel_path):
def update_jotform_widget(local_excel_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
        page = browser.new_page()

        log.info("Logging into JotForm...")
        page.goto("https://www.jotform.com/login")
        page.goto("https://www.jotform.com/login", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector('input[name="email"]', timeout=60000)
        page.fill('input[name="email"]', os.environ["JOTFORM_EMAIL"])
        page.wait_for_selector('input[name="password"]', timeout=60000)
        page.fill('input[name="password"]', os.environ["JOTFORM_PASSWORD"])
        page.wait_for_selector('button[type="submit"]', timeout=60000)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=60000)

        log.info("Opening form builder...")
        page.goto(f"https://www.jotform.com/build/{os.environ['JOTFORM_FORM_ID']}")
        page.wait_for_load_state("networkidle", timeout=30000)
        page.goto(f"https://www.jotform.com/build/{os.environ['JOTFORM_FORM_ID']}", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)

        page.click('[data-type="control_spreadsheet"]')
        page.wait_for_selector('input[type="file"]', timeout=10000)
        page.wait_for_selector('input[type="file"]', timeout=60000)
        page.set_input_files('input[type="file"]', local_excel_path)
        page.wait_for_timeout(3000)
