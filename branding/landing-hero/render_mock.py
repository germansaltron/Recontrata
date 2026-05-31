import pathlib
from playwright.sync_api import sync_playwright

url = pathlib.Path("eval_mock.html").resolve().as_uri()
with sync_playwright() as p:
    br = p.chromium.launch(headless=True)
    pg = br.new_page(viewport={"width": 390, "height": 820}, device_scale_factor=2)
    pg.goto(url, wait_until="networkidle")
    pg.wait_for_timeout(900)
    h = pg.evaluate("() => document.querySelector('.max-w-lg').getBoundingClientRect().height")
    print("content height", round(h))
    pg.set_viewport_size({"width": 390, "height": int(h) + 8})
    pg.wait_for_timeout(200)
    pg.screenshot(path="eval_screen.png")
    br.close()
print("screen captured")
