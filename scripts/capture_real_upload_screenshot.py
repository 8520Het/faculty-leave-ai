"""
Capture authentic screenshot of Faculty uploading the handwritten leave form photo
with file preview, applicant details, and the 5-step AI pipeline stepper.
"""

import asyncio
from playwright.async_api import async_playwright
import os

OUTPUT_DIR = r"c:\Users\HP\Desktop\faculty-leave-ai\docs\figures"
LEAVE_IMAGE = r"C:\Users\HP\.gemini\antigravity\brain\1be44bb8-b1b4-4bcb-a686-c047913a8256\.user_uploaded\media_1792504093342_f0e6911b.jpg"

async def capture_upload():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 950},
            device_scale_factor=1.5
        )
        page = await context.new_page()

        # Login with correct password
        print("Logging in...")
        await page.goto("http://127.0.0.1:5173/login", wait_until="networkidle")
        await page.locator("#facultyEmail").fill("sandeep.suthar@ddu.ac.in")
        await page.locator("#facultyPassword").fill("password123")
        await page.locator('button[type="submit"]').click()
        await page.wait_for_timeout(1200)

        # Navigate to /upload
        print("Navigating to /upload...")
        await page.goto("http://127.0.0.1:5173/upload", wait_until="networkidle")
        await page.wait_for_timeout(800)

        # Set the handwritten form file
        file_input = page.locator("input[type='file']")
        if await file_input.count() > 0 and os.path.exists(LEAVE_IMAGE):
            print("Setting input file with real handwritten leave form...")
            await file_input.set_input_files(LEAVE_IMAGE)
            await page.wait_for_timeout(2500)

        # Scroll to show file dropzone with preview and submit button
        await page.evaluate("window.scrollTo({ top: 180, behavior: 'smooth' })")
        await page.wait_for_timeout(1000)

        out_path = os.path.join(OUTPUT_DIR, "fig_4_9_upload_pipeline.png")
        await page.screenshot(path=out_path)
        print(f"Captured authentic upload screenshot to {out_path} ({os.path.getsize(out_path)} bytes)")

        # Also capture Review Desk with physical leave form visible
        print("Navigating to review desk...")
        await page.goto("http://127.0.0.1:5173/review/b4f1791a-8219-4ec4-9169-2f22c5443fa0", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        # Scroll to show both the scanned physical document side-by-side with conflict rows
        await page.evaluate("window.scrollTo({ top: 380, behavior: 'smooth' })")
        await page.wait_for_timeout(1000)
        out_review = os.path.join(OUTPUT_DIR, "fig_4_10_leave_review_red_alerts.png")
        await page.screenshot(path=out_review)
        print(f"Captured updated review desk screenshot to {out_review} ({os.path.getsize(out_review)} bytes)")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_upload())
