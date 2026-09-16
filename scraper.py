import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

def fetch_google_jobs():
    """Menarik data dari Google Jobs (Paling Lengkap)"""
    if not SERPAPI_KEY:
        print("INFO: SERPAPI_KEY tidak ditemukan. Melewati Google Jobs.")
        return []
        
    print("Menarik data dari Google Jobs...")
    url = f"https://serpapi.com/search.json?engine=google_jobs&q=lowongan+kerja+ketapang&hl=id&gl=id&api_key={SERPAPI_KEY}"
    jobs = []
    
    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            data = res.json().get("jobs_results", [])
            for item in data:
                apply_link = item.get("related_links", [{"link": "#"}])[0].get("link", "#")
                jobs.append({
                    "id": item.get("job_id", ""),
                    "title": item.get("title", ""),
                    "company": item.get("company_name", ""),
                    "location": item.get("location", "Ketapang"),
                    "via": item.get("via", "Google Jobs"),
                    "posted_at": item.get("detected_extensions", {}).get("posted_at", "Terbaru"),
                    "description": item.get("description", "")[:150] + "...",
                    "original_url": apply_link
                })
    except Exception as e:
        print(f"Error Google Jobs: {e}")
    return jobs

def fetch_html_scraping():
    """HTML Scraping tradisional dari portal Loker.id"""
    print("Menarik data via HTML Scraping (Loker.id)...")
    url = "https://www.loker.id/cari-lowongan-kerja?q=ketapang"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    jobs = []
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # Mencari elemen judul lowongan
            for h3 in soup.find_all('h3'):
                a_tag = h3.find('a')
                if a_tag and 'lowongan-kerja' in a_tag.get('href', ''):
                    title = a_tag.text.strip()
                    if "ketapang" in title.lower():
                        jobs.append({
                            "id": title.replace(" ", "-").lower(),
                            "title": title,
                            "company": "Cek di Halaman Sumber",
                            "location": "Ketapang",
                            "via": "Loker.id",
                            "posted_at": "Terbaru",
                            "description": "Buka tautan asli untuk melihat kualifikasi dan detail perusahaan.",
                            "original_url": a_tag['href']
                        })
    except Exception as e:
        print(f"Error HTML Scraping: {e}")
    return jobs

def main():
    all_jobs = []
    
    # 1. Jalankan semua fungsi scraper
    all_jobs.extend(fetch_google_jobs())
    all_jobs.extend(fetch_html_scraping())
    
    # 2. Hapus Duplikat berdasarkan Judul
    seen_titles = set()
    unique_jobs = []
    for job in all_jobs:
        if job["title"] not in seen_titles:
            seen_titles.add(job["title"])
            unique_jobs.append(job)
            
    # Jika gagal semua, sediakan 1 dummy agar front-end tidak crash
    if not unique_jobs:
        unique_jobs = [{
            "id": "dummy-1",
            "title": "Staf Administrasi (Menunggu Update)",
            "company": "Sistem Loker Ketapang",
            "location": "Ketapang",
            "via": "System",
            "posted_at": "Hari ini",
            "description": "Sistem sedang mengumpulkan data terbaru...",
            "original_url": "#"
        }]

    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M WIB"),
        "total": len(unique_jobs),
        "jobs": unique_jobs
    }
    
    with open("vacancy.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        
    print(f"Selesai! Berhasil mengumpulkan {len(unique_jobs)} lowongan.")

if __name__ == "__main__":
    main()
