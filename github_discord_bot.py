import os
import requests
from bs4 import BeautifulSoup

# --- CẤU HÌNH HỆ THỐNG ---
# Dán URL Webhook bạn vừa copy ở Bước 1 vào đây
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')

# Chọn ngôn ngữ (Ví dụ: 'java', 'python', 'go' hoặc để trống '' để lấy tổng hợp)
LANGUAGE = 'java' 
URL = f"https://github.com/trending/{LANGUAGE}" if LANGUAGE else "https://github.com/trending"

def get_github_trending():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(URL, headers=headers)
        if response.status_code != 200:
            print(f"Không thể truy cập GitHub. Mã lỗi: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        repos = []
        articles = soup.find_all('article', class_='Box-row')
        
        # Lấy top 5 kho lưu trữ nổi bật nhất
        for article in articles[:5]: 
            title_box = article.find('h2', class_='h3')
            repo_name = title_box.text.strip().replace('\n', '').replace(' ', '') if title_box else "Unknown"
            repo_link = f"https://github.com/{repo_name}"
            
            desc_p = article.find('p', class_='col-9')
            description = desc_p.text.strip() if desc_p else "Không có mô tả."
            
            stars_div = article.find('div', class_='f6')
            stars_today = "N/A"
            if stars_div:
                span_today = stars_div.find('span', class_='d-inline-block float-sm-right')
                if span_today:
                    stars_today = span_today.text.strip()

            repos.append({
                'name': repo_name,
                'link': repo_link,
                'desc': description,
                'stars_today': stars_today
            })
            
        return repos
    except Exception as e:
        print(f"Đã xảy ra lỗi khi cào dữ liệu: {e}")
        return []

def send_discord_webhook(content):
    """Gửi dữ liệu đến Discord thông qua Webhook"""
    payload = {
        "content": content,
        "username": "GitHub Trending AI", # Bạn có thể đổi tên hiển thị của Bot tại đây
        "avatar_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" # Icon GitHub
    }
    
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code in [200, 204]:
        return True
    else:
        print(f"Lỗi gửi Discord: {response.status_code}, {response.text}")
        return False

def main():
    print("Đang quét GitHub Trending...")
    trending_list = get_github_trending()
    
    if not trending_list:
        print("Không tìm thấy dữ liệu xu hướng.")
        return

    # Định dạng tin nhắn bằng Markdown của Discord
    lang_title = LANGUAGE.upper() if LANGUAGE else "ALL LANGUAGES"
    
    # Sử dụng khối lệnh (Block) hoặc chữ đậm để làm nổi bật tiêu đề
    message = f"## 🚀 GITHUB TRENDING BẢN TIN [{lang_title}] 🚀\n\n"
    
    for idx, repo in enumerate(trending_list, 1):
        message += f"### {idx}. **{repo['name']}**\n"
        message += f"> 📝 *Mô tả:* {repo['desc']}\n"
        message += f"> ⭐ *Xu hướng:* `{repo['stars_today']}`\n"
        message += f"🔗 [Xem trên GitHub]({repo['link']})\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
    # Gửi đến Discord
    if send_discord_webhook(message):
        print("Gửi thông báo đến Discord thành công!")
    else:
        print("Gửi thông báo thất bại.")

if __name__ == "__main__":
    main()
