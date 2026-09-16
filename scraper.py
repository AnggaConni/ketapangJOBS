import json
import os
import requests
from datetime import datetime

# Mengambil key dari GitHub Secrets
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")

def fetch_jsearch_jobs(keyword="lowongan kerja ketapang"):
    """Menarik data lowongan dari JSearch API (RapidAPI)"""
    if not RAPIDAPI_KEY:
        print("PERINGATAN: RAPIDAPI_KEY tidak diisi. Proses dihentikan.")
        return []

    url = "https://jsearch.p.rapidapi.com/search"
    
    # Parameter pencarian JSearch
    querystring = {
        "query": keyword,
        "page": "1",
        "num_pages": "1", # Tarik 1 halaman pertama (biasanya isi ~10-15 lowongan)
        "country": "id",
        "date_posted": "all" # Bisa diubah ke "today", "3days", "week"
    }

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    print("Fetching data dari JSearch API...")
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        if response.status_code == 200:
            data = response.json().get("data", [])
            jobs = []
            
            for item in data:
                # Format lokasi (Kota, Provinsi)
                city = item.get("job_city") or ""
                state = item.get("job_state") or ""
                location = f"{city}, {state}".strip(", ")
                if not location:
                    location = item.get("job_location", "Kalimantan Barat")

                # Memastikan ada deskripsi dan memotongnya agar tidak terlalu panjang
                desc = item.get("job_description") or ""
                if len(desc) > 200:
                    desc = desc[:200] + "..."

                # Mapping format JSON JSearch ke format standar kita
                jobs.append({
                    "id": item.get("job_id", ""),
                    "title": item.get("job_title", ""),
                    "company": item.get("employer_name", ""),
                    "location": location,
                    "via": item.get("job_publisher", "JSearch"), # Misal: LinkedIn, Glassdoor, ZipRecruiter
                    "posted_at": item.get("job_posted_at_datetime_utc", "")[:10], # Ambil tanggalnya saja (YYYY-MM-DD)
                    "description": desc,
                    "original_url": item.get("job_apply_link") or item.get("job_google_link", "#")
                })
            return jobs
        else:
            print(f"Error API: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error saat request ke JSearch: {e}")
    
    return []

def filter_ketapang(job_list):
    """Memastikan hanya mengambil lowongan yang berlokasi di Ketapang atau Kalbar"""
    keywords = ["ketapang", "kalimantan barat", "kalbar"]
    filtered = []
    
    for job in job_list:
        loc = job.get("location", "").lower()
        title = job.get("title", "").lower()
        desc = job.get("description", "").lower()
        
        # Validasi: Jika kata kunci ada di Lokasi, Judul, ATAU Deskripsi
        if any(kw in loc for kw in keywords) or any(kw in title for kw in keywords) or any(kw in desc for kw in keywords):
            filtered.append(job)
            
    return filtered

def main():
    # 1. Tarik dari API
    raw_jobs = fetch_jsearch_jobs("lowongan kerja ketapang kalimantan barat")
    
    # 2. Filter data
    ketapang_jobs = filter_ketapang(raw_jobs)
    
    # 3. Susun Output JSON
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M WIB"),
        "total": len(ketapang_jobs),
        "jobs": ketapang_jobs
    }
    
    # 4. Tulis ke vacancy.json
    with open("vacancy.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        
    print(f"Sukses! {len(ketapang_jobs)} lowongan disimpan ke vacancy.json")

if __name__ == "__main__":
    main()
