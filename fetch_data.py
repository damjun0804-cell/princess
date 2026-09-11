import json
import cloudscraper
from datetime import datetime

USER_ID = "9592015"

# 보안 차단을 우회하기 위한 브라우저 세션 생성
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://www.spooncast.net",
    "Referer": f"https://www.spooncast.net/kr/channel/{USER_ID}/tab/home"
}

def fetch_spoon_data():
    # 1. 프로필, 팬 수 수집
    user_api_url = f"https://kr-api.spooncast.net/users/{USER_ID}/"
    res = scraper.get(user_api_url, headers=HEADERS)
    
    if res.status_code != 200:
        print(f"[오류] 프로필 로드 실패 - Status Code: {res.status_code}")
        # 차단 시 기본값 보장
        data_json = {}
    else:
        data_json = res.json()

    results = data_json.get("results", [])
    user_data = results[0] if results else data_json

    nickname = user_data.get("nickname", "Rose")
    profile_img = user_data.get("profile_url", "")
    fan_count = user_data.get("fancount", user_data.get("fan_count", 0))
    description = user_data.get("description", "")

    # 2. 공지사항 탭 수집
    notice_api_url = f"https://kr-api.spooncast.net/users/{USER_ID}/notice/"
    notice_res = scraper.get(notice_api_url, headers=HEADERS)
    
    notice_text = ""
    if notice_res.status_code == 200:
        notice_json = notice_res.json()
        notice_list = notice_json.get("results", [])
        if notice_list:
            notice_text = notice_list[0].get("contents", "")

    # 공지사항 없을 경우 소개글로 대체
    if not notice_text:
        notice_text = description if description else "등록된 공지사항이 없습니다."

    # 3. 최근 방송 정보 수집
    live_api_url = f"https://kr-api.spooncast.net/users/{USER_ID}/live/"
    live_res = scraper.get(live_api_url, headers=HEADERS)
    
    is_live = False
    last_live_start = "방송 기록 없음"

    if live_res.status_code == 200:
        live_json = live_res.json()
        live_results = live_json.get("results", [])
        if live_results:
            live_data = live_results[0]
            engine_status = live_data.get("engine", {}).get("host", "")
            is_live = (engine_status == "connected") or live_data.get("is_live", False)
            
            created_str = live_data.get("created", "")
            if created_str:
                try:
                    dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                    last_live_start = dt.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    last_live_start = created_str

    output_data = {
        "nickname": nickname,
        "profile_img": profile_img,
        "fan_count": fan_count,
        "is_live": is_live,
        "last_live_start": last_live_start,
        "notice": notice_text,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":

    fetch_spoon_data()
