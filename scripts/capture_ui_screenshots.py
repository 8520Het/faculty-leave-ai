"""
Capture live application screenshots using Playwright for official report figures.
"""

import asyncio
from playwright.async_api import async_playwright
import os

OUTPUT_DIR = r"c:\Users\HP\Desktop\faculty-leave-ai\docs\figures"
FORM_CONFLICT_ID = "b4f1791a-8219-4ec4-9169-2f22c5443fa0"
FORM_VALID_ID = "cfee775b-761f-4f65-8670-bea68159b4eb"

async def capture_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1.5
        )
        page = await context.new_page()

        # 1. Login
        print("Navigating to login...")
        await page.goto("http://127.0.0.1:5173/login", wait_until="networkidle")
        await page.locator("#facultyEmail").fill("vipul.dabhi@ddu.ac.in")
        await page.locator("#password").fill("admin123")
        await page.locator('button[type="submit"]').click()
        await page.wait_for_timeout(1500)

        # 2. Figure 4.6: HOD Overview Dashboard
        print("Capturing Figure 4.6: HOD Dashboard...")
        await page.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(OUTPUT_DIR, "fig_4_6_hod_dashboard.png"))

        # 3. Figure 4.7: Master Timetable Ingestion Panel
        print("Capturing Figure 4.7: Timetable Panel...")
        await page.goto("http://127.0.0.1:5173/admin/timetable", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(OUTPUT_DIR, "fig_4_7_timetable_panel.png"))

        # 4. Figure 4.8: Faculty Teaching Commitment Desk (/my-schedule)
        print("Capturing Figure 4.8: Faculty Schedule...")
        await page.goto("http://127.0.0.1:5173/my-schedule", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(OUTPUT_DIR, "fig_4_8_faculty_schedule.png"))

        # 5. Figure 4.9: AI Vision Document Upload
        print("Capturing Figure 4.9: Upload Pipeline...")
        await page.goto("http://127.0.0.1:5173/upload", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(OUTPUT_DIR, "fig_4_9_upload_pipeline.png"))

        # 6. Figure 4.10: Leave Review Desk with Red Warnings
        print("Capturing Figure 4.10: Leave Review Red Alerts...")
        await page.goto(f"http://127.0.0.1:5173/review/{FORM_CONFLICT_ID}", wait_until="networkidle")
        await page.wait_for_timeout(1200)
        await page.screenshot(path=os.path.join(OUTPUT_DIR, "fig_4_10_leave_review_red_alerts.png"))

        # 7. Figure 4.11: Substitute Notification Desk
        print("Capturing Figure 4.11: Substitute Notification...")
        await page.goto("http://127.0.0.1:5173/notifications", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(OUTPUT_DIR, "fig_4_11_substitute_notification.png"))

        await browser.close()
        print("All UI screenshots captured successfully in", OUTPUT_DIR)

if __name__ == "__main__":
    asyncio.run(capture_all())
