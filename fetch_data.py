import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

USER_ID = "9592015"
TARGET_URL = f"https://www.spooncast.net/kr/channel/{USER_ID}/tab/home"

def fetch_spoon_data():
    captured_data = {
        "nickname": "Rose",
        "profile_img": "",
        "fan_count": 0,
        "is_live": False,
        "last_live_start": "방송 기록 없음",
        "notice": "등록된 공지사항이 없습니다.",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with sync_playwright() as p:
        # 헤드리스 브라우저 실행
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ko-KR"
        )
        page = context.new_page()

        # 스푼라디오 네트워크 요청 수신(Interception)
        def handle_response(response):
            url = response.url
            try:
                # 1. 프로필 & 팬 수 데이터 수집
                if f"/users/{USER_ID}/" in url and response.status == 200:
                    json_res = response.json()
                    results = json_res.get("results", [])
                    user_data = results[0] if results else json_res
                    
                    captured_data["nickname"] = user_data.get("nickname", "Rose")
                    captured_data["profile_img"] = user_data.get("profile_url", "")
                    captured_data["fan_count"] = user_data.get("fancount", user_data.get("fan_count", 0))
                    
                    desc = user_data.get("description", "")
                    if desc:
                        captured_data["notice"] = desc

                # 2. 공지사항 데이터 수집
                elif f"/users/{USER_ID}/notice/" in url and response.status == 200:
                    json_res = response.json()
                    notice_list = json_res.get("results", [])
                    if notice_list:
                        captured_data["notice"] = notice_list[0].get("contents", captured_data["notice"])

                # 3. 라이브/방송 정보 수집
                elif f"/users/{USER_ID}/live/" in url and response.status == 200:
                    json_res = response.json()
                    results = json_res.get("results", [])
                    if results:
                        live_data = results[0]
                        engine_status = live_data.get("engine", {}).get("host", "")
                        captured_data["is_live"] = (engine_status == "connected") or live_data.get("is_live", False)
                        
                        created_str = live_data.get("created", "")
                        if created_str:
                            try:
                                dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                                captured_data["last_live_start"] = dt.strftime("%Y-%m-%d %H:%M")
                            except ValueError:
                                captured_data["last_live_start"] = created_str
            except Exception as e:
                print(f"Network intercept error: {e}")

        page.on("response", handle_response)

        # 페이지 이동 및 네트워크 완료 대기
        try:
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000) # 추가 비동기 로딩 대기
        except Exception as e:
            print(f"Page load timeout or error: {e}")

        browser.close()

    # 결과 데이터 data.json 저장을 위해 실행
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(captured_data, f, ensure_ascii=False, indent=4)
        print("Updated data.json:", captured_data)

if __name__ == "__main__":

    fetch_spoon_data()
