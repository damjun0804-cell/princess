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
        "last_live_start": "방송 기록 없음",
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

        # 1. 백엔드 REST API 응답 가로채기 (가장 정확한 데이터 원천)
        def handle_response(response):
            url = response.url
            try:
                # 유저 기본 프로필 API
                if f"/users/{USER_ID}/" in url and response.status == 200:
                    res_json = response.json()
                    results = res_json.get("results", [])
                    user_data = results[0] if results else res_json
                    
                    if user_data.get("nickname"):
                        captured_data["nickname"] = user_data.get("nickname")
                    if user_data.get("profile_url"):
                        captured_data["profile_img"] = user_data.get("profile_url")
                    
                    # fancount 키 및 fan_count 키 모두 검증
                    fc = user_data.get("fancount") or user_data.get("fan_count")
                    if fc is not None:
                        captured_data["fan_count"] = int(fc)
                        
                    if user_data.get("description"):
                        captured_data["notice"] = user_data.get("description")

                # 공지사항 탭 API
                elif f"/users/{USER_ID}/notice/" in url and response.status == 200:
                    res_json = response.json()
                    notice_list = res_json.get("results", [])
                    if notice_list and notice_list[0].get("contents"):
                        captured_data["notice"] = notice_list[0].get("contents")

                # 라이브 상태 API
                elif f"/users/{USER_ID}/live/" in url and response.status == 200:
                    res_json = response.json()
                    results = res_json.get("results", [])
                    if results:
                        live_data = results[0]
                        engine_status = live_data.get("engine", {}).get("host", "")
                        captured_data["is_live"] = (engine_status == "connected") or live_data.get("is_live", False)
                        
                        created_str = live_data.get("created", "")
                        if created_str:
                            try:
                                dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                                captured_data["last_live_start"] = dt.astimezone(KST).strftime("%Y-%m-%d %H:%M")
                            except ValueError:
                                captured_data["last_live_start"] = created_str

            except Exception as e:
                print(f"[API Intercept Error] {e}")

        page.on("response", handle_response)

        try:
            # DOM 및 네트워크 대기
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(6000)

            # 2. API 수신 실패 시 HTML DOM 요소 직접 파싱 (Fallback)
            
            # [이미지] 프로필 이미지태그 추출
            if not captured_data["profile_img"]:
                img_el = page.query_selector("img[src*='spooncast.net']")
                if img_el:
                    captured_data["profile_img"] = img_el.get_attribute("src")

            # [팬 수] "팬 103" 문구 파싱
            if captured_data["fan_count"] == 0:
                body_text = page.inner_text("body")
                match = re.search(r"팬\s*([\d,]+)", body_text)
                if match:
                    captured_data["fan_count"] = int(match.group(1).replace(",", ""))

            # [닉네임] H1 또는 상단 프로필 헤더 텍스트
            if captured_data["nickname"] == "Rose":
                header_el = page.query_selector("h1") or page.query_selector("h2")
                if header_el:
                    txt = header_el.inner_text().strip()
                    if txt:
                        captured_data["nickname"] = txt

            # [공지사항/소개글] 소개글 텍스트 영역 탐색
            if captured_data["notice"] in ["등록된 공지사항이 없습니다.", "103"]:
                # 메인 본문 컨테이너 탐색
                container = page.query_selector("main")
                if container:
                    lines = [line.strip() for line in container.inner_text().split("\n") if line.strip()]
                    for i, line in enumerate(lines):
                        if "팬" in line and i + 1 < len(lines):
                            target_text = lines[i + 1]
                            if not target_text.isdigit() and len(target_text) > 1:
                                captured_data["notice"] = target_text
                                break

        except Exception as e:
            print(f"[Page Load Error] {e}")

        browser.close()

    # 데이터 저장
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(captured_data, f, ensure_ascii=False, indent=4)
        print("Updated Result:", captured_data)

if __name__ == "__main__":
    fetch_spoon_data()
