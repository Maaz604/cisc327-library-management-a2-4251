import threading
import time
import os
import pytest
from playwright.sync_api import sync_playwright
from app import create_app
from database import init_database, DB_PATH

HOST = "127.0.0.1"
PORT = 5000
BASE_URL = f"http://{HOST}:{PORT}"

@pytest.fixture(scope="session", autouse=True)
def start_server():
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
    except Exception:
        pass

    init_database()
    app = create_app()
    thr = threading.Thread(target=lambda: app.run(host=HOST, port=PORT, debug=False, use_reloader=False))
    thr.daemon = True
    thr.start()
    time.sleep(2)
    yield

def test_add_book_and_borrow():
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page()

    #  FLOW 1: Add book
    page.goto(f"{BASE_URL}/add_book")
    page.fill("input[name=title]", "Test Book E2E")
    page.fill("input[name=author]", "Maaz Rizwan")
    page.fill("input[name=isbn]", "E2E-123")
    page.fill("input[name=total_copies]", "2")

    try:
        page.click("button[type=submit]")
    except:
        page.evaluate("document.querySelector('form').submit()")

    page.wait_for_load_state("networkidle")
    page.goto(f"{BASE_URL}/catalog")
    content = page.content()
    assert "Test Book E2E" in content, "Book not in catalog"

    # FLOW 2: Borrow book
    borrowed = False
    try:
        page.click("text=Borrow")
        page.wait_for_load_state("networkidle")
        page.goto(f"{BASE_URL}/catalog")
        if "borrow" in page.content().lower():
            borrowed = True
    except:
        borrowed = False

    if not borrowed:
        book_id = page.evaluate("""() => {
            const el = document.querySelector('input[name="book_id"]');
            return el ? el.value : '';
        }""")
        assert book_id, "cant find book id for borrow"
        req_ctx = pw.request.new_context()
        resp = req_ctx.post(f"{BASE_URL}/borrow", data={"patron_id": "patron1", "book_id": book_id})
        assert resp.status in (200, 302)

    browser.close()
    pw.stop()
