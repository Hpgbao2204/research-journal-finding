import requests
from bs4 import BeautifulSoup
import json
import os
import sys
from urllib.parse import quote_plus

def scrape_cfp(query_keyword):
    print(f"[*] Bắt đầu crawl dữ liệu từ WikiCFP cho từ khóa: '{query_keyword}'...")
    
    # URL tìm kiếm của WikiCFP. Thêm &year=t để lấy các hội nghị ở thời điểm hiện tại/tương lai
    url = f"http://www.wikicfp.com/cfp/servlet/tool.search?q={quote_plus(query_keyword)}&year=t" 
    
    # Headers mô phỏng trình duyệt để bypass hệ thống chống DDoS của WikiCFP
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Referer": "http://www.wikicfp.com/"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[!] Lỗi khi truy cập WikiCFP: {e}")
        return
        
    # Phân tích cú pháp HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results = []
    processed_ids = set()
    
    # Bước 3: Đọc HTML (Bóc tách dữ liệu)
    # Tại WikiCFP, tên viết tắt của Event nằm trong các thẻ <a> trỏ tới link 'event.showcfp'
    links = soup.find_all('a', href=lambda h: h and 'event.showcfp' in h)
    
    for link in links:
        href = link.get('href')
        
        # Lọc trùng lặp event (trên WikiCFP có thể có nhiều link copy trỏ về cùng 1 event)
        event_id = href.split('eventid=')[1].split('&')[0] if 'eventid=' in href else None
        if not event_id or event_id in processed_ids:
            continue
            
        processed_ids.add(event_id)
        
        acronym = link.text.strip()
        detail_link = f"http://www.wikicfp.com{href}"
        
        # Lấy dòng <tr> chứa thẻ <a> hiện tại
        row1 = link.find_parent('tr')
        if not row1:
            continue
            
        # Cột (td) thứ 2 của row1 chứa Tên đầy đủ của Hội nghị / Tạp chí
        tds1 = row1.find_all('td')
        full_name = tds1[1].text.strip() if len(tds1) > 1 else ""
        
        # Dòng <tr> ngay phía dưới chứa thông tin: When, Where, Deadline
        row2 = row1.find_next_sibling('tr')
        deadline = "N/A"
        if row2:
            tds2 = row2.find_all('td')
            # Thông thường cấu trúc là: Khi nào (0) | Ở đâu (1) | Deadline (2)
            if len(tds2) >= 3:
                deadline = tds2[2].text.strip()
            elif len(tds2) == 2:
                deadline = tds2[1].text.strip()
        
        results.append({
            "Acronym": acronym,
            "Name": full_name,
            "Deadline": deadline,
            "Link": detail_link
        })
        
    # Bước 4: Đóng gói JSON
    os.makedirs("output", exist_ok=True)
    output_path = "output/cfp_results.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        
    print(f"[*] Crawl thành công {len(results)} Call for Papers.")
    print(f"[*] Dữ liệu đã được đóng gói và lưu tại: {output_path}")

if __name__ == "__main__":
    # Cài đặt tham số đầu vào query_keyword (Mặc định là "Blockchain" nếu không có param)
    keyword = sys.argv[1] if len(sys.argv) > 1 else "Blockchain"
    scrape_cfp(keyword)
