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
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ko-KR",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        # 1. API 응답 가로채기 (프로필 및 이미지용)
        def handle_response(response):
            url = response.url
            try:
                if f"/users/{USER_ID}/" in url and response.status == 200:
                    json_res = response.json()
                    results = json_res.get("results", [])
                    user_data = results[0] if results else json_res
                    
                    if user_data.get("nickname"):
                        captured_data["nickname"] = user_data.get("nickname")
                    if user_data.get("profile_url"):
                        captured_data["profile_img"] = user_data.get("profile_url")
            except Exception:
                pass

        page.on("response", handle_response)

        try:
            # 페이지 접속 및 완전한 로딩 대기
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000) # 5초간 화면 렌더링 유지

            # 2. DOM 화면 요소 직접 추출 (팬 수)
            body_text = page.inner_text("body")
            
            # "팬 103" 또는 "팬 1,024" 형태 패턴 정규식 탐색
            fan_match = re.search(r"팬\s*([\d,]+)", body_text)
            if fan_match:
                fan_str = fan_match.group(1).replace(",", "")
                captured_data["fan_count"] = int(fan_str)

            # 3. DOM 화면 요소 직접 추출 (소개글 / 공지사항)
            # 스푼 프로필 상단 또는 탭 내부 텍스트 추출 시도
            try:
                # 프로필 하단 소개글 영역 셀렉터 탐색
                notice_element = page.query_selector("main") or page.query_selector("body")
                if notice_element:
                    all_text = notice_element.inner_text()
                    lines = [line.strip() for line in all_text.split("\n") if line.strip()]
                    
                    # "팬 XXX" 다음 줄에 나오는 문장을 소개글/공지사항으로 인식
                    for i, line in enumerate(lines):
                        if "팬" in line and i + 1 < len(lines):
                            next_line = lines[i + 1]
                            if next_line and not next_line.startswith("http") and len(next_line) > 1:
                                captured_data["notice"] = next_line
                                break
            except Exception as e:
                print(f"DOM text parse error: {e}")

            # 4. 라이브 상태 확인 (화면에 ON AIR 표시 여부)
            if "LIVE" in body_text or "ON AIR" in body_text or "방송 중" in body_text:
                captured_data["is_live"] = True

        except Exception as e:
            print(f"Page execution error: {e}")

        browser.close()

    # 결과 데이터 저장
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(captured_data, f, ensure_ascii=False, indent=4)
        print("Updated data.json:", captured_data)

if __name__ == "__main__":

    fetch_spoon_data()
