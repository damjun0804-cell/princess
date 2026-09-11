import json
import re
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

USER_ID = "9592015"
TARGET_URL = f"https://www.spooncast.net/kr/channel/{USER_ID}/tab/home"
KST = timezone(timedelta(hours=9))

def fetch_spoon_data():
    captured_data = {
        "nickname": "Rose",
        "profile_img": "",
        "fan_count": 0,
        "is_live": False,
        "description": "등록된 자기소개가 없습니다.",
        "notice": "등록된 공지사항이 없습니다.",
        "updated_at": datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ko-KR",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        # 1. API 응답 가로채기
        def handle_response(response):
            url = response.url
            try:
                # 유저 프로필 API
                if f"/users/{USER_ID}/" in url and response.status == 200:
                    res_json = response.json()
                    results = res_json.get("results", [])
                    user_data = results[0] if results else res_json
                    
                    if user_data.get("nickname"):
                        captured_data["nickname"] = user_data.get("nickname")
                    if user_data.get("profile_url"):
                        captured_data["profile_img"] = user_data.get("profile_url")
                    
                    fc = user_data.get("fancount") or user_data.get("fan_count")
                    if fc is not None:
                        captured_data["fan_count"] = int(fc)
                        
                    desc = user_data.get("description", "").strip()
                    if desc:
                        captured_data["description"] = desc

                # 공지사항 API
                elif f"/users/{USER_ID}/notice/" in url and response.status == 200:
                    res_json = response.json()
                    notice_list = res_json.get("results", [])
                    if notice_list and notice_list[0].get("contents"):
                        contents = notice_list[0].get("contents", "").strip()
                        if contents:
                            captured_data["notice"] = contents

                # 라이브 상태 API
                elif f"/users/{USER_ID}/live/" in url and response.status == 200:
                    res_json = response.json()
                    results = res_json.get("results", [])
                    if results:
                        live_data = results[0]
                        engine_status = live_data.get("engine", {}).get("host", "")
                        captured_data["is_live"] = (engine_status == "connected") or live_data.get("is_live", False)

            except Exception as e:
                print(f"[API Intercept Error] {e}")

        page.on("response", handle_response)

        try:
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)

            # 2. DOM 파싱 Fallback (API 실패 시 보완)
            if not captured_data["profile_img"]:
                img_el = page.query_selector("img[src*='spooncast.net']")
                if img_el:
                    captured_data["profile_img"] = img_el.get_attribute("src")

            if captured_data["fan_count"] == 0:
                body_text = page.inner_text("body")
                match = re.search(r"팬\s*([\d,]+)", body_text)
                if match:
                    captured_data["fan_count"] = int(match.group(1).replace(",", ""))

            # DOM에서 자기소개 문구 정밀 파싱
            if captured_data["description"] == "등록된 자기소개가 없습니다.":
                follow_btn = page.query_selector("button:has-text('팔로우')")
                if follow_btn:import json
import re
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

USER_ID = "9592015"
TARGET_URL = f"https://www.spooncast.net/kr/channel/{USER_ID}/tab/home"
KST = timezone(timedelta(hours=9))

def fetch_spoon_data():
    captured_data = {
        "nickname": "Rose",
        "profile_img": "",
        "fan_count": 0,
        "is_live": False,
        "description": "등록된 자기소개가 없습니다.",
        "notice": "등록된 공지사항이 없습니다.",
        "updated_at": datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ko-KR",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        # 1. API 응답 가로채기
        def handle_response(response):
            url = response.url
            try:
                # 유저 프로필 API
                if f"/users/{USER_ID}/" in url and response.status == 200:
                    res_json = response.json()
                    results = res_json.get("results", [])
                    user_data = results[0] if results else res_json
                    
                    if user_data.get("nickname"):
                        captured_data["nickname"] = user_data.get("nickname")
                    if user_data.get("profile_url"):
                        captured_data["profile_img"] = user_data.get("profile_url")
                    
                    fc = user_data.get("fancount") or user_data.get("fan_count")
                    if fc is not None:
                        captured_data["fan_count"] = int(fc)
                        
                    desc = user_data.get("description", "").strip()
                    if desc:
                        captured_data["description"] = desc

                # 공지사항 API
                elif f"/users/{USER_ID}/notice/" in url and response.status == 200:
                    res_json = response.json()
                    notice_list = res_json.get("results", [])
                    if notice_list and notice_list[0].get("contents"):
                        contents = notice_list[0].get("contents", "").strip()
                        if contents:
                            captured_data["notice"] = contents

                # 라이브 상태 API
                elif f"/users/{USER_ID}/live/" in url and response.status == 200:
                    res_json = response.json()
                    results = res_json.get("results", [])
                    if results:
                        live_data = results[0]
                        engine_status = live_data.get("engine", {}).get("host", "")
                        captured_data["is_live"] = (engine_status == "connected") or live_data.get("is_live", False)

            except Exception as e:
                print(f"[API Intercept Error] {e}")

        page.on("response", handle_response)

        try:
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)

            # 2. DOM 파싱 Fallback (API 실패 시 보완)
            if not captured_data["profile_img"]:
                img_el = page.query_selector("img[src*='spooncast.net']")
                if img_el:
                    captured_data["profile_img"] = img_el.get_attribute("src")

            if captured_data["fan_count"] == 0:
                body_text = page.inner_text("body")
                match = re.search(r"팬\s*([\d,]+)", body_text)
                if match:
                    captured_data["fan_count"] = int(match.group(1).replace(",", ""))

            # DOM에서 자기소개 문구 정밀 파싱
            if captured_data["description"] == "등록된 자기소개가 없습니다.":
                follow_btn = page.query_selector("button:has-text('팔로우')")
                if follow_btn:
                    parent = follow_btn.evaluate_handle("el => el.closest('div').parentElement")
                    if parent:
                        lines = [l.strip() for l in parent.as_element().inner_text().split("\n") if l.strip()]
                        exclude_list = ["Rose", "팬", "팔로우하고 팬 되기", "홈", "캐스트", "다시 듣기", "포스트", "팬보드", "팬 랭킹"]
                        for line in lines:
                            if line not in exclude_list and not line.isdigit() and not line.startswith("@"):
                                captured_data["description"] = line
                                break

        except Exception as e:
            print(f"[Page Load Error] {e}")

        browser.close()

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(captured_data, f, ensure_ascii=False, indent=4)
        print("Updated Result:", captured_data)

if __name__ == "__main__":
    fetch_spoon_data()
                    parent = follow_btn.evaluate_handle("el => el.closest('div').parentElement")
                    if parent:
                        lines = [l.strip() for l in parent.as_element().inner_text().split("\n") if l.strip()]
                        exclude_list = ["Rose", "팬", "팔로우하고 팬 되기", "홈", "캐스트", "다시 듣기", "포스트", "팬보드", "팬 랭킹"]
                        for line in lines:
                            if line not in exclude_list and not line.isdigit() and not line.startswith("@"):
                                captured_data["description"] = line
                                break

        except Exception as e:
            print(f"[Page Load Error] {e}")

        browser.close()

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(captured_data, f, ensure_ascii=False, indent=4)
        print("Updated Result:", captured_data)

if __name__ == "__main__":
    fetch_spoon_data()
