import asyncio
import json
import os
import shutil
import sqlite3
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright
import imageio_ffmpeg

PROJECT_ROOT = Path(__file__).parent.parent
DEMO_DIR = PROJECT_ROOT / "demo_output"
AUDIO_PATH = PROJECT_ROOT / "demo_audio.mp3"
FINAL_VIDEO_PATH = PROJECT_ROOT / "faculty_leave_ai_demo.mp4"
DB_PATH = PROJECT_ROOT / "data" / "faculty_leave.db"

TARGET_FORM_ID = "c6183ffc-2d49-458b-96d4-8d37c268b131"


def reset_demo_state():
    """Resets the sqlite database to pristine state for recording the demo."""
    print("Resetting database state for demo recording...")
    if not DB_PATH.exists():
        print(f"Database {DB_PATH} not found, skipping reset.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    # 1. Reset email notifications for Sunil K. Vithlani to SENT
    c.execute("UPDATE email_previews SET status='SENT' WHERE substitute_name LIKE '%Sunil%' OR to_email LIKE '%vithlani%'")

    # 2. Reset form status to NEEDS_REVIEW
    c.execute("UPDATE leave_forms SET status='NEEDS_REVIEW' WHERE id=?", (TARGET_FORM_ID,))

    # 3. Reset row 2 of form to have conflict (Subject C, Room 2)
    c.execute("SELECT payload_json FROM assignment_rows WHERE form_id=? AND row_number=2", (TARGET_FORM_ID,))
    row = c.fetchone()
    if row:
        data = json.loads(row[0])
        data["status"] = "REVIEWED"
        data["requires_review"] = True
        data["reviewed"] = False
        data["parsed"]["subject"] = "C"
        data["parsed"]["room"] = "2"
        data["parsed"]["start_time"] = "14:30"
        data["parsed"]["end_time"] = "15:30"
        data["parsed"]["day"] = 6
        data["parsed"]["month"] = "AUG"
        if "timetable" in data and data["timetable"]:
            data["timetable"]["subject"] = "C"
            data["timetable"]["room"] = "2"
            data["timetable"]["start_time"] = "14:30"
            data["timetable"]["end_time"] = "15:30"
        c.execute("UPDATE assignment_rows SET payload_json=?, status='REVIEWED', requires_review=1 WHERE form_id=? AND row_number=2",
                  (json.dumps(data), TARGET_FORM_ID))

    conn.commit()
    conn.close()
    print("Database reset complete.")


async def show_badge(page, phase_num, phase_title):
    """Renders a stylish floating Phase badge in the top right corner."""
    await page.evaluate(f"""
        (() => {{
            let old = document.getElementById('demo-scene-badge');
            if (old) old.remove();
            let b = document.createElement('div');
            b.id = 'demo-scene-badge';
            b.style.position = 'fixed';
            b.style.top = '16px';
            b.style.right = '24px';
            b.style.zIndex = '999999';
            b.style.background = 'linear-gradient(135deg, #1e3a8a, #2563eb)';
            b.style.color = '#ffffff';
            b.style.padding = '8px 18px';
            b.style.borderRadius = '30px';
            b.style.fontFamily = 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
            b.style.fontSize = '13px';
            b.style.fontWeight = '600';
            b.style.boxShadow = '0 6px 20px rgba(0,0,0,0.28)';
            b.style.border = '1px solid rgba(255,255,255,0.35)';
            b.style.display = 'flex';
            b.style.alignItems = 'center';
            b.style.gap = '10px';
            b.style.pointerEvents = 'none';
            b.innerHTML = '<span style="background:rgba(255,255,255,0.22);border-radius:12px;padding:3px 9px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">Phase {phase_num}</span> <span>{phase_title}</span>';
            document.body.appendChild(b);
        }})()
    """)


async def inject_helpers(page):
    """Injects mouse tracking visualizer."""
    await page.evaluate("""
        (() => {
            if (!document.getElementById('cursor-tracker')) {
                let c = document.createElement('div');
                c.id = 'cursor-tracker';
                c.style.position = 'fixed';
                c.style.width = '24px';
                c.style.height = '24px';
                c.style.borderRadius = '50%';
                c.style.border = '2px solid rgba(37, 99, 235, 0.9)';
                c.style.backgroundColor = 'rgba(59, 130, 246, 0.3)';
                c.style.pointerEvents = 'none';
                c.style.zIndex = '9999999';
                c.style.transform = 'translate(-50%, -50%)';
                c.style.transition = 'width 0.15s, height 0.15s, background-color 0.15s';
                document.body.appendChild(c);

                window.addEventListener('mousemove', e => {
                    c.style.left = e.clientX + 'px';
                    c.style.top = e.clientY + 'px';
                });
                window.addEventListener('mousedown', () => {
                    c.style.width = '34px';
                    c.style.height = '34px';
                    c.style.backgroundColor = 'rgba(239, 68, 68, 0.45)';
                });
                window.addEventListener('mouseup', () => {
                    c.style.width = '24px';
                    c.style.height = '24px';
                    c.style.backgroundColor = 'rgba(59, 130, 246, 0.3)';
                });
            }
        })()
    """)


async def record_demo():
    reset_demo_state()

    if DEMO_DIR.exists():
        shutil.rmtree(DEMO_DIR)
    DEMO_DIR.mkdir(parents=True, exist_ok=True)

    print("Launching Chromium 1080p video recording...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-web-security", "--allow-running-insecure-content"]
        )

        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(DEMO_DIR),
            record_video_size={"width": 1920, "height": 1080}
        )

        page = await context.new_page()

        # Automatically accept confirm dialogs
        page.on("dialog", lambda dialog: dialog.accept())

        # =====================================================================
        # SCENE 1: Introduction & HOD Login (Target duration: ~31s)
        # Narration: Welcome to Faculty Leave AI... We begin by logging in as HOD Dr. Vipul K. Dabhi...
        # =====================================================================
        print(">>> SCENE 1: Introduction & HOD Login (31s)")
        await page.goto("http://127.0.0.1:5173/login", wait_until="networkidle")
        await inject_helpers(page)
        await show_badge(page, 1, "Head of Department Overview & Secure Login")
        # Hold on intro login screen while voice explains background context
        await page.wait_for_timeout(9000)

        # Smooth typing email
        email_input = page.locator("#facultyEmail")
        await email_input.click()
        await page.wait_for_timeout(500)
        await email_input.type("vipul.dabhi@ddu.ac.in", delay=40)
        await page.wait_for_timeout(1000)

        # Typing password
        pwd_input = page.locator("#facultyPassword")
        await pwd_input.click()
        await page.wait_for_timeout(500)
        await pwd_input.type("password123", delay=50)
        await page.wait_for_timeout(1500)

        # Click Sign In
        submit_btn = page.locator("button[type='submit']")
        await submit_btn.click()
        await page.wait_for_url("http://127.0.0.1:5173/")
        await inject_helpers(page)
        await show_badge(page, 1, "Head of Department Dashboard — Dr. Vipul K. Dabhi")
        await page.wait_for_timeout(14000)

        # =====================================================================
        # SCENE 2: Admin Panel & Timetable Ingestion (Target duration: ~23s)
        # Narration: On the Admin Desk, department leadership can ingest master timetables...
        # =====================================================================
        print(">>> SCENE 2: Admin Panel & Timetable Ingestion (23s)")
        admin_link = page.locator("a[href='/admin']").first
        await admin_link.click()
        await page.wait_for_url("http://127.0.0.1:5173/admin")
        await inject_helpers(page)
        await show_badge(page, 2, "Timetable Ingestion & Image-Wise Control")
        await page.wait_for_timeout(2500)

        # Scroll to Preset area
        await page.evaluate("window.scrollTo({ top: 380, behavior: 'smooth' })")
        await page.wait_for_timeout(2000)

        # Click Load Preset: Sem 7 Div F
        preset_btn = page.locator("button:has-text('Load Preset: Sem 7 Div F')").first
        if await preset_btn.count() > 0:
            await preset_btn.click()
            await page.wait_for_timeout(3500)

            # Click Commit & Save to Database
            commit_btn = page.locator("button:has-text('Commit & Save to Database')").first
            if await commit_btn.count() > 0:
                await commit_btn.click()
                await page.wait_for_timeout(3500)

        # Scroll down to Committed Department Timetables (Image-Wise)
        await page.evaluate("window.scrollTo({ top: 880, behavior: 'smooth' })")
        await page.wait_for_timeout(2500)

        # Expand slots grid for first timetable
        view_slots_btn = page.locator("button:has-text('View Slots Grid')").first
        if await view_slots_btn.count() > 0:
            await view_slots_btn.click()
            await page.wait_for_timeout(2500)

        await page.evaluate("window.scrollTo({ top: 1250, behavior: 'smooth' })")
        await page.wait_for_timeout(6500)

        # =====================================================================
        # SCENE 3: Switch to Applicant & My Schedule (Target duration: ~14s)
        # Narration: Next, we switch to an applicant faculty member, Prof. Sandeep R. Suthar...
        # =====================================================================
        print(">>> SCENE 3: Applicant Portal & My Schedule (14s)")
        await page.evaluate("""
            sessionStorage.setItem('faculty_user', JSON.stringify({
                id: 3,
                name: 'Prof. Sandeep R. Suthar',
                shortName: 'SRS',
                email: 'sandeep.suthar@ddu.ac.in',
                department: 'Information Technology',
                designation: 'Assistant Professor',
                avatar: '/faculty/10-SRS.jpg',
                role: 'FACULTY'
            }));
        """)
        await page.goto("http://127.0.0.1:5173/my-schedule", wait_until="networkidle")
        await inject_helpers(page)
        await show_badge(page, 3, "Applicant Faculty — Personalized Schedule (Prof. Sandeep R. Suthar)")
        await page.wait_for_timeout(4000)

        await page.evaluate("window.scrollTo({ top: 380, behavior: 'smooth' })")
        await page.wait_for_timeout(10000)

        # =====================================================================
        # SCENE 4: Leave Form Review & Red Conflict Warnings (Target duration: ~32s)
        # Narration: Now, Prof. Suthar uploads a handwritten faculty leave arrangement sheet...
        # =====================================================================
        print(">>> SCENE 4: Leave Form Review & Red Conflict Warnings (32s)")
        target_form_url = f"http://127.0.0.1:5173/review/{TARGET_FORM_ID}"
        await page.goto(target_form_url, wait_until="networkidle")
        await inject_helpers(page)
        await show_badge(page, 4, "Scanned Leave Sheet & AI Discrepancy Engine")
        await page.wait_for_timeout(4000)

        # Scroll to show scanned image alongside OCR
        await page.evaluate("window.scrollTo({ top: 300, behavior: 'smooth' })")
        await page.wait_for_timeout(4000)

        # Scroll to top Red Conflict Banner
        await page.evaluate("window.scrollTo({ top: 580, behavior: 'smooth' })")
        await page.wait_for_timeout(6000)

        # Scroll to Row 1 & Row 2 red conflict boxes
        await page.evaluate("window.scrollTo({ top: 960, behavior: 'smooth' })")
        await page.wait_for_timeout(18000)

        # =====================================================================
        # SCENE 5: Inline Correction & Notification Dispatch (Target duration: ~18s)
        # Narration: Faculty can quickly correct entries inline... Once subject is set to AI and room to 26...
        # =====================================================================
        print(">>> SCENE 5: Inline Correction & Notification Dispatch (18s)")
        await show_badge(page, 5, "Real-Time Inline Correction & Notification Dispatch")

        # Focus Row 2 Subject input (second input with placeholder 'e.g. AJT')
        subject_inputs = page.locator("input[placeholder='e.g. AJT']")
        if await subject_inputs.count() >= 2:
            row2_sub = subject_inputs.nth(1)
            await row2_sub.click()
            await row2_sub.fill("")
            await row2_sub.type("AI", delay=60)
            await page.wait_for_timeout(1000)

        # Focus Row 2 Room input (second input with placeholder 'e.g. 26')
        room_inputs = page.locator("input[placeholder='e.g. 26']")
        if await room_inputs.count() >= 2:
            row2_room = room_inputs.nth(1)
            await row2_room.click()
            await row2_room.fill("")
            await row2_room.type("26", delay=60)
            await page.wait_for_timeout(1500)

        # Scroll up to Save & Notify button
        await page.evaluate("window.scrollTo({ top: 460, behavior: 'smooth' })")
        await page.wait_for_timeout(1500)

        # Click Save All Changes & Notify All Faculty
        save_btn = page.locator("button:has-text('Save All Changes & Notify All Faculty')").first
        if await save_btn.count() > 0:
            await save_btn.click()
            await page.wait_for_timeout(4500)

        # Show success confirmation and dispatched email cards
        await page.evaluate("window.scrollTo({ top: 200, behavior: 'smooth' })")
        await page.wait_for_timeout(9500)

        # =====================================================================
        # SCENE 6: Substitute Perspective (Prof. Sunil K. Vithlani) (Target duration: ~21s)
        # Narration: Now switching to substitute faculty, Prof. Sunil K. Vithlani...
        # =====================================================================
        print(">>> SCENE 6: Substitute Perspective (21s)")
        await page.evaluate("""
            sessionStorage.setItem('faculty_user', JSON.stringify({
                id: 8,
                name: 'Prof. Sunil K. Vithlani',
                shortName: 'SKV',
                email: 'sunil.vithlani@ddu.ac.in',
                department: 'Information Technology',
                designation: 'Assistant Professor',
                avatar: '/faculty/14-SKV.jpg',
                role: 'FACULTY'
            }));
        """)
        await page.goto("http://127.0.0.1:5173/notifications", wait_until="networkidle")
        await inject_helpers(page)
        await show_badge(page, 6, "Substitute Faculty Inbox & One-Click Acknowledgment (Prof. Sunil K. Vithlani)")
        await page.wait_for_timeout(6000)

        # Find and click Acknowledge Substitution button
        ack_btn = page.locator("button:has-text('Acknowledge Substitution')").first
        if await ack_btn.count() > 0:
            await ack_btn.click()
            await page.wait_for_timeout(4000)

        # View acknowledged state
        await page.wait_for_timeout(11000)

        # =====================================================================
        # SCENE 7: Dashboard Synchronization & Summary (Target duration: ~18s)
        # Narration: Back on the dashboard, the entire leave workflow is automatically updated...
        # =====================================================================
        print(">>> SCENE 7: Dashboard Synchronization & Summary (18s)")
        dash_link = page.locator("a[href='/']").first
        await dash_link.click()
        await page.wait_for_url("http://127.0.0.1:5173/")
        await inject_helpers(page)
        await show_badge(page, 7, "Live Dashboard Synchronization & Continuity")
        await page.wait_for_timeout(4000)

        # Smooth scroll over dashboard stats
        await page.evaluate("window.scrollTo({ top: 350, behavior: 'smooth' })")
        await page.wait_for_timeout(6000)

        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
        await page.wait_for_timeout(8000)

        print("Automated browser walk-through complete. Closing browser context...")
        await context.close()
        await browser.close()

    # Find the recorded webm file in demo_output
    video_files = list(DEMO_DIR.glob("*.webm"))
    if not video_files:
        raise RuntimeError("No recorded video file found in demo_output")

    raw_video = video_files[0]
    print(f"Recorded raw video: {raw_video}")

    # FFmpeg binary
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Using FFmpeg: {ffmpeg_exe}")

    # Mux video and audio into MP4
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", str(raw_video),
        "-i", str(AUDIO_PATH),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(FINAL_VIDEO_PATH)
    ]

    print("Encoding final demo video with audio voiceover...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg error:", res.stderr)
        # Fallback encoding without libx264 parameter
        fallback_cmd = [
            ffmpeg_exe,
            "-y",
            "-i", str(raw_video),
            "-i", str(AUDIO_PATH),
            "-c:a", "aac",
            "-shortest",
            str(FINAL_VIDEO_PATH)
        ]
        subprocess.run(fallback_cmd, check=True)

    print("\n==========================================")
    print("SUCCESS! Demo video created at:")
    print(f"{FINAL_VIDEO_PATH}")
    print(f"Size: {FINAL_VIDEO_PATH.stat().st_size / (1024*1024):.2f} MB")
    print("==========================================")


if __name__ == "__main__":
    asyncio.run(record_demo())
