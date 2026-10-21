import asyncio
import json
import os
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path
from playwright.async_api import async_playwright
import imageio_ffmpeg

PROJECT_ROOT = Path(__file__).parent.parent
DEMO_DIR = PROJECT_ROOT / "demo_output_multi"
AUDIO_MASTER = PROJECT_ROOT / "user_voiceover_master.mp3"
VIDEO_VOICEOVER = PROJECT_ROOT / "faculty_leave_ai_user_voiceover_demo.mp4"
VIDEO_CLEAN = PROJECT_ROOT / "faculty_leave_ai_demo_clean.mp4"

DB_PATH = PROJECT_ROOT / "data" / "faculty_leave.db"
IMAGE_CONFLICT = PROJECT_ROOT / "data" / "demo_inputs" / "leave_form_conflict.jpg"
IMAGE_VALID = PROJECT_ROOT / "data" / "demo_inputs" / "leave_form_valid.jpg"

FORM_CONFLICT_ID = "d1c697bc-bd26-45c4-861f-18e193576afa"
FORM_VALID_ID = "cfee775b-761f-4f65-8670-bea68159b4eb"

# Target durations in seconds measured from the generated scene audios:
# Total = ~252s (4m 12s)
SCENE_DURATIONS = {
    1: 41.3,
    2: 43.8,
    3: 17.9,
    4: 18.0,
    5: 36.7,
    6: 22.8,
    7: 29.3,
    8: 22.9,
    9: 19.7,
}


def reset_demo_database():
    """Sets pristine database state for both conflict and valid forms."""
    print("Resetting database state for comprehensive demo...")
    if not DB_PATH.exists():
        print("Database not found!")
        return

    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    # 1. Reset notifications for Sunil K. Vithlani
    c.execute("UPDATE email_previews SET status='SENT' WHERE substitute_name LIKE '%Sunil%' OR to_email LIKE '%vithlani%'")

    # 2. Reset conflict form d1c697bc-bd26-45c4-861f-18e193576afa
    c.execute("UPDATE leave_forms SET status='NEEDS_REVIEW', applicant_name='Prof. Sandeep R. Suthar' WHERE id=?", (FORM_CONFLICT_ID,))

    # Row 1: Sem 5 Div F (invalid timing 11:30-14:30, subject 2000S, Room 26)
    c.execute("SELECT payload_json FROM assignment_rows WHERE form_id=? AND row_number=1", (FORM_CONFLICT_ID,))
    r1 = c.fetchone()
    if r1:
        d1 = json.loads(r1[0])
        d1["parsed"] = {
            "semester": 5, "division": "F", "day": 6, "month": "AUG",
            "start_time": "11:30", "end_time": "14:30", "room": "26",
            "subject": "2000S", "staff": "Prof. Archana N. Vyas"
        }
        d1["timetable"] = {
            "semester": 5, "division": "F", "start_time": "11:30", "end_time": "14:30",
            "room": "26", "subject": "2000S", "normal_faculty": "Prof. Sandeep R. Suthar"
        }
        d1["substitute"] = {
            "name": "Archana N. Vyas", "email": "archana.vyas@ddu.ac.in", "department": "IT"
        }
        d1["status"] = "MANUAL_REVIEW_REQUIRED"
        d1["requires_review"] = True
        d1["reviewed"] = False
        c.execute("UPDATE assignment_rows SET payload_json=?, status='MANUAL_REVIEW_REQUIRED', requires_review=1, reviewed=0 WHERE form_id=? AND row_number=1",
                  (json.dumps(d1), FORM_CONFLICT_ID))

    # Row 2: Sem 7 Div F (subject C vs AI, Room 2 vs 26)
    c.execute("SELECT payload_json FROM assignment_rows WHERE form_id=? AND row_number=2", (FORM_CONFLICT_ID,))
    r2 = c.fetchone()
    if r2:
        d2 = json.loads(r2[0])
        d2["parsed"] = {
            "semester": 7, "division": "F", "day": 6, "month": "AUG",
            "start_time": "14:30", "end_time": "15:30", "room": "2",
            "subject": "C", "staff": "Prof. Sunil K. Vithlani"
        }
        d2["timetable"] = {
            "semester": 7, "division": "F", "start_time": "14:30", "end_time": "15:30",
            "room": "2", "subject": "C", "normal_faculty": "Prof. Sandeep R. Suthar"
        }
        d2["substitute"] = {
            "name": "Sunil K. Vithlani", "email": "sunil.vithlani@ddu.ac.in", "department": "IT"
        }
        d2["status"] = "MANUAL_REVIEW_REQUIRED"
        d2["requires_review"] = True
        d2["reviewed"] = False
        c.execute("UPDATE assignment_rows SET payload_json=?, status='MANUAL_REVIEW_REQUIRED', requires_review=1, reviewed=0 WHERE form_id=? AND row_number=2",
                  (json.dumps(d2), FORM_CONFLICT_ID))

    # 3. Setup valid form cfee775b-761f-4f65-8670-bea68159b4eb
    c.execute("UPDATE leave_forms SET status='NEEDS_REVIEW', applicant_name='Prof. Sandeep R. Suthar' WHERE id=?", (FORM_VALID_ID,))
    c.execute("DELETE FROM assignment_rows WHERE form_id=? AND row_number > 2", (FORM_VALID_ID,))

    # Valid Row 1: Sem 7 Div F AI at 14:30-15:30 Room 26
    c.execute("SELECT payload_json FROM assignment_rows WHERE form_id=? AND row_number=1", (FORM_VALID_ID,))
    vr1 = c.fetchone()
    if vr1:
        vd1 = json.loads(vr1[0])
        vd1["parsed"] = {
            "semester": 7, "division": "F", "day": 6, "month": "AUG",
            "start_time": "14:30", "end_time": "15:30", "room": "26",
            "subject": "AI", "staff": "Prof. Sunil K. Vithlani"
        }
        vd1["timetable"] = {
            "semester": 7, "division": "F", "start_time": "14:30", "end_time": "15:30",
            "room": "26", "subject": "AI", "normal_faculty": "Prof. Sandeep R. Suthar"
        }
        vd1["substitute"] = {
            "name": "Sunil K. Vithlani", "email": "sunil.vithlani@ddu.ac.in", "department": "IT"
        }
        vd1["status"] = "REVIEWED"
        vd1["requires_review"] = False
        vd1["reviewed"] = True
        c.execute("UPDATE assignment_rows SET payload_json=?, status='REVIEWED', requires_review=0, reviewed=1 WHERE form_id=? AND row_number=1",
                  (json.dumps(vd1), FORM_VALID_ID))

    # Valid Row 2: Sem 7 Div F MLDL Lab at 15:30-17:30 Room Lab 2
    c.execute("SELECT payload_json FROM assignment_rows WHERE form_id=? AND row_number=2", (FORM_VALID_ID,))
    vr2 = c.fetchone()
    if vr2:
        vd2 = json.loads(vr2[0])
        vd2["parsed"] = {
            "semester": 7, "division": "F", "day": 6, "month": "AUG",
            "start_time": "15:30", "end_time": "17:30", "room": "Lab 2",
            "subject": "MLDL", "staff": "Prof. Sunil K. Vithlani"
        }
        vd2["timetable"] = {
            "semester": 7, "division": "F", "start_time": "15:30", "end_time": "17:30",
            "room": "Lab 2", "subject": "MLDL", "normal_faculty": "Prof. Sandeep R. Suthar"
        }
        vd2["substitute"] = {
            "name": "Sunil K. Vithlani", "email": "sunil.vithlani@ddu.ac.in", "department": "IT"
        }
        vd2["status"] = "REVIEWED"
        vd2["requires_review"] = False
        vd2["reviewed"] = True
        c.execute("UPDATE assignment_rows SET payload_json=?, status='REVIEWED', requires_review=0, reviewed=1 WHERE form_id=? AND row_number=2",
                  (json.dumps(vd2), FORM_VALID_ID))

    conn.commit()
    conn.close()
    print("Database reset completed successfully.")


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


async def record_all_scenes():
    reset_demo_database()

    if DEMO_DIR.exists():
        shutil.rmtree(DEMO_DIR)
    DEMO_DIR.mkdir(parents=True, exist_ok=True)

    print("Launching Chromium 1080p full walkthrough recording...")
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
        page.on("dialog", lambda dialog: dialog.accept())

        # =====================================================================
        # SCENE 1: Introduction & HOD Login (41.3s total)
        # Login screen: 00:00 - 00:30 (30.0s)
        # Dashboard screen: 00:30 - 00:41.3 (11.3s)
        # =====================================================================
        print(">>> SCENE 1: Introduction & HOD Login (Login: 0-30s, Dashboard: 30-41.3s)")
        t0 = time.time()
        await page.goto("http://127.0.0.1:5173/login", wait_until="networkidle")
        await inject_helpers(page)
        await show_badge(page, 1, "Head of Department Overview & Secure Login")

        # Keep login screen clean until t = 26.5s
        wait_until_typing = max(0, 26.5 - (time.time() - t0))
        await page.wait_for_timeout(int(wait_until_typing * 1000))

        # Typing email
        email_input = page.locator("#facultyEmail")
        await email_input.click()
        await email_input.type("vipul.dabhi@ddu.ac.in", delay=35)

        # Typing password
        pwd_input = page.locator("#facultyPassword")
        await pwd_input.click()
        await pwd_input.type("password123", delay=40)

        # Ensure submit is clicked at exactly t = 30.0s
        wait_until_submit = max(0, 30.0 - (time.time() - t0))
        await page.wait_for_timeout(int(wait_until_submit * 1000))

        # Click Sign In at exactly 00:30
        submit_btn = page.locator("button[type='submit']")
        await submit_btn.click()
        await page.wait_for_url("http://127.0.0.1:5173/")
        await inject_helpers(page)
        await show_badge(page, 1, "Head of Department Dashboard — Dr. Vipul K. Dabhi")

        # Show dashboard from 00:30 to 00:41.3
        wait_until_scene2 = max(0, 41.3 - (time.time() - t0))
        await page.wait_for_timeout(int(wait_until_scene2 * 1000))

        # =====================================================================
        # SCENE 2: Admin Command Desk & Timetable Master (43.8s)
        # =====================================================================
        print(">>> SCENE 2: Admin Command Desk & Timetable Ingestion (43.8s)")
        t0 = time.time()
        admin_link = page.locator("a[href='/admin']").first
        await admin_link.click()
        await page.wait_for_url("http://127.0.0.1:5173/admin")
        await inject_helpers(page)
        await show_badge(page, 2, "Timetable Ingestion & Image-Wise Grouping")
        await page.wait_for_timeout(3000)

        # Scroll to Preset area
        await page.evaluate("window.scrollTo({ top: 380, behavior: 'smooth' })")
        await page.wait_for_timeout(2500)

        # Click Load Preset: Sem 7 Div F
        preset_btn = page.locator("button:has-text('Load Preset: Sem 7 Div F')").first
        if await preset_btn.count() > 0:
            await preset_btn.click()
            await page.wait_for_timeout(4000)

            # Click Commit & Save to Database
            commit_btn = page.locator("button:has-text('Commit & Save to Database')").first
            if await commit_btn.count() > 0:
                await commit_btn.click()
                await page.wait_for_timeout(4000)

        # Scroll down to Committed Department Timetables (Image-Wise)
        await page.evaluate("window.scrollTo({ top: 880, behavior: 'smooth' })")
        await page.wait_for_timeout(3000)

        # Expand slots grid for first timetable
        view_slots_btn = page.locator("button:has-text('View Slots Grid')").first
        if await view_slots_btn.count() > 0:
            await view_slots_btn.click()
            await page.wait_for_timeout(3500)

        await page.evaluate("window.scrollTo({ top: 1250, behavior: 'smooth' })")

        elapsed = time.time() - t0
        rem = max(0, SCENE_DURATIONS[2] - elapsed)
        await page.wait_for_timeout(int(rem * 1000))

        # =====================================================================
        # SCENE 3: Applicant Portal & My Schedule (17.9s)
        # =====================================================================
        print(">>> SCENE 3: Applicant Portal & Personalized Schedule (17.9s)")
        t0 = time.time()
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
        await show_badge(page, 3, "Applicant Portal — Personalized Schedule (Prof. Sandeep R. Suthar)")
        await page.wait_for_timeout(3000)

        await page.evaluate("window.scrollTo({ top: 380, behavior: 'smooth' })")

        elapsed = time.time() - t0
        rem = max(0, SCENE_DURATIONS[3] - elapsed)
        await page.wait_for_timeout(int(rem * 1000))

        # =====================================================================
        # SCENE 4: Scanned Leave Form Upload & AI Pipeline (18.0s)
        # =====================================================================
        print(">>> SCENE 4: Scanned Leave Form Upload & AI Pipeline (18.0s)")
        t0 = time.time()
        await page.goto("http://127.0.0.1:5173/upload", wait_until="networkidle")
        await inject_helpers(page)
        await show_badge(page, 4, "Document Upload & AI Vision OCR Pipeline")
        await page.wait_for_timeout(2500)

        # Set physical conflict leave form image
        file_input = page.locator("input[type='file']")
        if await file_input.count() > 0 and IMAGE_CONFLICT.exists():
            await file_input.set_input_files(str(IMAGE_CONFLICT))
            await page.wait_for_timeout(2500)

        # Scroll to submit button and click Upload & Run OCR Scan
        await page.evaluate("window.scrollTo({ top: 400, behavior: 'smooth' })")
        await page.wait_for_timeout(1500)

        elapsed = time.time() - t0
        rem = max(0, SCENE_DURATIONS[4] - elapsed)
        await page.wait_for_timeout(int(rem * 1000))

        # =====================================================================
        # SCENE 5: Leave Form Review & Red Warning Alerts (36.7s)
        # =====================================================================
        print(">>> SCENE 5: Leave Form Review & Red Warning Alerts (36.7s)")
        t0 = time.time()
        review_url = f"http://127.0.0.1:5173/review/{FORM_CONFLICT_ID}"
        await page.goto(review_url, wait_until="networkidle")
        await inject_helpers(page)
        await show_badge(page, 5, "Timetable Discrepancy Engine & Red Warning Alerts")
        await page.wait_for_timeout(4000)

        # Scroll to show scanned physical document side-by-side
        await page.evaluate("window.scrollTo({ top: 300, behavior: 'smooth' })")
        await page.wait_for_timeout(4500)

        # Scroll to top Red Conflict Banner
        await page.evaluate("window.scrollTo({ top: 580, behavior: 'smooth' })")
        await page.wait_for_timeout(7000)

        # Scroll to Row 1 & Row 2 red conflict cards
        await page.evaluate("window.scrollTo({ top: 960, behavior: 'smooth' })")

        elapsed = time.time() - t0
        rem = max(0, SCENE_DURATIONS[5] - elapsed)
        await page.wait_for_timeout(int(rem * 1000))

        # =====================================================================
        # SCENE 6: Real-Time Inline Corrections & Dispatch (22.8s)
        # =====================================================================
        print(">>> SCENE 6: Inline Correction & Notification Dispatch (22.8s)")
        t0 = time.time()
        await show_badge(page, 6, "Real-Time Inline Correction & Notification Dispatch")

        # Focus Row 2 Subject input (change 'C' to 'AI')
        subject_inputs = page.locator("input[placeholder='e.g. AJT']")
        if await subject_inputs.count() >= 2:
            row2_sub = subject_inputs.nth(1)
            await row2_sub.click()
            await row2_sub.fill("")
            await row2_sub.type("AI", delay=60)
            await page.wait_for_timeout(1000)

        # Focus Row 2 Room input (change '2' to '26')
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
            await page.wait_for_timeout(4000)

        # Show success confirmation and dispatched email cards
        await page.evaluate("window.scrollTo({ top: 200, behavior: 'smooth' })")

        elapsed = time.time() - t0
        rem = max(0, SCENE_DURATIONS[6] - elapsed)
        await page.wait_for_timeout(int(rem * 1000))

        # =====================================================================
        # SCENE 7: Substitute Perspective & One-Click Acknowledgment (29.3s)
        # =====================================================================
        print(">>> SCENE 7: Substitute Faculty Perspective (29.3s)")
        t0 = time.time()
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
        await show_badge(page, 7, "Substitute Faculty Inbox & One-Click Acknowledgment (Prof. Sunil K. Vithlani)")
        await page.wait_for_timeout(6000)

        # Click Acknowledge Substitution
        ack_btn = page.locator("button:has-text('Acknowledge Substitution')").first
        if await ack_btn.count() > 0:
            await ack_btn.click()
            await page.wait_for_timeout(4000)

        elapsed = time.time() - t0
        rem = max(0, SCENE_DURATIONS[7] - elapsed)
        await page.wait_for_timeout(int(rem * 1000))

        # =====================================================================
        # SCENE 8: Clean / Valid Form Upload & Zero Conflicts (22.9s)
        # =====================================================================
        print(">>> SCENE 8: Valid Leave Form Upload & Zero Conflicts (22.9s)")
        t0 = time.time()
        # Switch back to applicant
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
        valid_review_url = f"http://127.0.0.1:5173/review/{FORM_VALID_ID}"
        await page.goto(valid_review_url, wait_until="networkidle")
        await inject_helpers(page)
        await show_badge(page, 8, "Clean Leave Form — 100% Timetable Match & Zero Conflicts")
        await page.wait_for_timeout(4000)

        # Scroll to show valid rows (AI at 2:30-3:30 in 26, MLDL Lab at 3:30-5:30 in Lab 2)
        await page.evaluate("window.scrollTo({ top: 400, behavior: 'smooth' })")
        await page.wait_for_timeout(5000)

        await page.evaluate("window.scrollTo({ top: 750, behavior: 'smooth' })")

        elapsed = time.time() - t0
        rem = max(0, SCENE_DURATIONS[8] - elapsed)
        await page.wait_for_timeout(int(rem * 1000))

        # =====================================================================
        # SCENE 9: Executive Dashboard Synchronization & Conclusion (19.7s)
        # =====================================================================
        print(">>> SCENE 9: Executive Dashboard Synchronization & Conclusion (19.7s)")
        t0 = time.time()
        dash_link = page.locator("a[href='/']").first
        await dash_link.click()
        await page.wait_for_url("http://127.0.0.1:5173/")
        await inject_helpers(page)
        await show_badge(page, 9, "Real-Time Dashboard Synchronization & Teaching Continuity")
        await page.wait_for_timeout(4000)

        # Smooth scroll over dashboard stats
        await page.evaluate("window.scrollTo({ top: 350, behavior: 'smooth' })")
        await page.wait_for_timeout(6000)

        await page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")

        elapsed = time.time() - t0
        rem = max(0, SCENE_DURATIONS[9] - elapsed)
        await page.wait_for_timeout(int(rem * 1000))

        print("Automated browser recording completed. Closing browser...")
        await context.close()
        await browser.close()

    # Find the recorded webm file in demo_output_multi
    video_files = list(DEMO_DIR.glob("*.webm"))
    if not video_files:
        raise RuntimeError("No recorded video file found in demo_output_multi")

    raw_video = video_files[0]
    print(f"Recorded raw browser video: {raw_video}")

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Using FFmpeg: {ffmpeg_exe}")

    # =========================================================================
    # EXPORT VIDEO 1: WITH INDIAN VOICE OVER
    # =========================================================================
    print("\n--------------------------------------------------")
    print("Muxing Video 1: WITH INDIAN ACCENT VOICEOVER...")
    print("--------------------------------------------------")
    cmd_voiceover = [
        ffmpeg_exe,
        "-y",
        "-i", str(raw_video),
        "-i", str(AUDIO_MASTER),
        "-filter_complex", "[0:v]tpad=stop_mode=clone:stop_duration=3[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(VIDEO_VOICEOVER)
    ]
    res1 = subprocess.run(cmd_voiceover, capture_output=True, text=True)
    if res1.returncode != 0:
        print("FFmpeg error:", res1.stderr)
        # Fallback without libx264 preset
        fallback1 = [
            ffmpeg_exe, "-y",
            "-i", str(raw_video),
            "-i", str(AUDIO_MASTER),
            "-c:a", "aac",
            "-shortest",
            str(VIDEO_VOICEOVER)
        ]
        subprocess.run(fallback1, check=True)

    print(f"SUCCESS: Video 1 created at: {VIDEO_VOICEOVER}")
    print(f"Size: {VIDEO_VOICEOVER.stat().st_size / (1024*1024):.2f} MB")

    # =========================================================================
    # EXPORT VIDEO 2: CLEAN WALKTHROUGH (NO VOICEOVER / SILENT)
    # =========================================================================
    print("\n--------------------------------------------------")
    print("Rendering Video 2: CLEAN WALKTHROUGH (NO VOICEOVER)...")
    print("--------------------------------------------------")
    cmd_clean = [
        ffmpeg_exe,
        "-y",
        "-i", str(raw_video),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-an",
        "-movflags", "+faststart",
        str(VIDEO_CLEAN)
    ]
    res2 = subprocess.run(cmd_clean, capture_output=True, text=True)
    if res2.returncode != 0:
        print("FFmpeg error:", res2.stderr)
        fallback2 = [
            ffmpeg_exe, "-y",
            "-i", str(raw_video),
            "-an",
            str(VIDEO_CLEAN)
        ]
        subprocess.run(fallback2, check=True)

    print(f"SUCCESS: Video 2 created at: {VIDEO_CLEAN}")
    print(f"Size: {VIDEO_CLEAN.stat().st_size / (1024*1024):.2f} MB")

    print("\n==================================================")
    print("ALL DELIVERABLES COMPLETED SUCCESSFULLY!")
    print(f"Video 1 (Voiceover): {VIDEO_VOICEOVER}")
    print(f"Video 2 (Clean):     {VIDEO_CLEAN}")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(record_all_scenes())
