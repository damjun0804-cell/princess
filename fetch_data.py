import json
import requests
from datetime import datetime

USER_ID = "9592015"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def fetch_spoon_data():
    # 1. 프로필, 팬 수, 프로필 소개글 수집
    user_api_url = f"https://kr-api.spooncast.net/users/{USER_ID}/"
    user_res = requests.get(user_api_url, headers=HEADERS)
    
    if user_res.status_code != 200:
        raise Exception(f"사용자 정보 로드 실패: {user_res.status_code}")
    
    user_json = user_res.json()
    # API 응답 구조 예외 처리
    if "results" in user_json and len(user_json["results"]) > 0:
        user_data = user_json["results"][0]
    else:
        user_data = user_json
    
    nickname = user_data.get("nickname", "Rose")
    profile_img = user_data.get("profile_url", "")
    
    # 팬 수 필드명 처리 (fancount 또는 fan_count)
    fan_count = user_data.get("fancount", user_data.get("fan_count", 0))
    
    # 프로필 상단 자기소개글 추출
    profile_bio = user_data.get("description", "")

    # 2. 공지사항 탭 게시글 수집
    notice_api_url = f"https://kr-api.spooncast.net/users/{USER_ID}/notice/"
    notice_res = requests.get(notice_api_url, headers=HEADERS)
    
    notice_text = ""
    if notice_res.status_code == 200:
        notice_json = notice_res.json()
        notice_list = notice_json.get("results", [])
        if notice_list:
            notice_text = notice_list[0].get("contents", "")
            
    # 공지사항 탭이 비어있을 경우 프로필 자기소개글로 대체
    if not notice_text and profile_bio:
        notice_text = profile_bio
    elif not notice_text:
        notice_text = "등록된 공지사항이 없습니다."

    # 3. 최근 방송 정보 및 방송 진행 여부 수집
    live_api_url = f"https://kr-api.spooncast.net/users/{USER_ID}/live/"
    live_res = requests.get(live_api_url, headers=HEADERS)
    
    is_live = False
    last_live_start = "방송 기록 없음"
    
    if live_res.status_code == 200:
        live_json = live_res.json()
        results = live_json.get("results", [])
        if results:
            live_data = results[0]
            engine_status = live_data.get("engine", {}).get("host", "")
            is_live = (engine_status == "connected") or live_data.get("is_live", False)
            
            created_str = live_data.get("created", "")
            if created_str:
                try:
                    dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                    last_live_start = dt.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    last_live_start = created_str

    # JSON 데이터 생성
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
