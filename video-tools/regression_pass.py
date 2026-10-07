"""Cross-cutting regression pass: every main route, in all 3 languages,
in both themes, checking for console errors and that the page actually
rendered something meaningful (not a blank/crashed screen).
"""
from playwright.sync_api import sync_playwright

BASE = "http://localhost:5173"
ROUTES = ["/", "/chat", "/profile", "/benefits", "/settings", "/login", "/register"]
LANGUAGES = ["en", "hi", "ta"]
THEMES = ["light", "dark"]

results = []
all_errors = []

with sync_playwright() as p:
    browser = p.chromium.launch()

    for language in LANGUAGES:
        for theme in THEMES:
            ctx = browser.new_context(viewport={"width": 1280, "height": 800})
            page = ctx.new_page()
            page_errors = []
            page.on("pageerror", lambda e: page_errors.append(str(e)))
            page.on("console", lambda m: page_errors.append(f"console.error: {m.text}") if m.type == "error" else None)

            page.goto(BASE + "/", wait_until="networkidle")
            page.evaluate(f"localStorage.setItem('bn_language', JSON.stringify('{language}'))")
            page.evaluate(f"localStorage.setItem('bn_theme', JSON.stringify('{theme}'))")

            for route in ROUTES:
                page.goto(BASE + route, wait_until="networkidle")
                page.wait_for_timeout(150)
                body_text = page.inner_text("body")
                has_content = len(body_text.strip()) > 20
                has_react_root = page.locator("#root").count() > 0
                results.append(
                    {
                        "language": language,
                        "theme": theme,
                        "route": route,
                        "has_content": has_content,
                        "has_root": has_react_root,
                    }
                )

            if page_errors:
                all_errors.append({"language": language, "theme": theme, "errors": page_errors})

            ctx.close()

    browser.close()

print(f"\n{'='*60}")
print(f"Checked {len(results)} (route x language x theme) combinations")
failed = [r for r in results if not r["has_content"] or not r["has_root"]]
if failed:
    print(f"FAILED ({len(failed)}):")
    for f in failed:
        print(f"  {f}")
else:
    print("All pages rendered content successfully.")

print(f"\nConsole/page errors across {len(LANGUAGES) * len(THEMES)} sessions: {len(all_errors)}")
for e in all_errors:
    print(f"  {e}")

print("=" * 60)
if failed or all_errors:
    raise SystemExit(1)
print("REGRESSION PASS: ALL CLEAR")
