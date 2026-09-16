import json
import os
import requests
from datetime import datetime

# Masukkan SERPAPI_KEY di GitHub Secrets jika pakai SerpApi
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

def fetch_google_jobs(keyword="lowongan kerja ketapang"):
    """Menarik data lowongan dari Google Jobs via SerpApi"""
    if not SERPAPI_KEY:
        print("PERINGATAN: SERPAPI_KEY tidak diisi. Menggunakan data simulasi fallback.")
        return get_mock_data()

    url = f"https://serpapi.com/search.json?engine=google_jobs&q={keyword}&hl=id&gl=id&api_key={SERPAPI_KEY}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            jobs = []
            for item in data.get("jobs_results", []):
                # Ambil link lamaran asli (direct redirect)
                apply_link = "#"
                if item.get("apply_options"):
                    apply_link = item["apply_options"][0].get("link", "#")
                elif item.get("related_links"):
                    apply_link = item["related_links"][0].get("link", "#")

                jobs.append({
                    "id": item.get("job_id", ""),
                    "title": item.get("title", ""),
                    "company": item.get("company_name", ""),
                    "location": item.get("location", "Ketapang, Kalimantan Barat"),
                    "via": item.get("via", "Google Jobs"),
                    "posted_at": item.get("detected_extensions", {}).get("posted_at", "Terbaru"),
                    "description": item.get("description", "")[:180] + "...",
                    "original_url": apply_link
                })
            return jobs
    except Exception as e:
        print(f"Error fetching Google Jobs: {e}")
    
    return get_mock_data()

def filter_ketapang(job_list):
    """Filter ketat agar hanya menampilkan lowongan Ketapang/Kalbar"""
    keywords = ["ketapang", "kalimantan barat", "kalbar"]
    filtered = []
    
    for job in job_list:
        loc = job.get("location", "").lower()
        title = job.get("title", "").lower()
        
        # Masukkan jika lokasi mengandung kata kunci Ketapang / Kalbar
        if any(kw in loc for kw in keywords) or "ketapang" in title:
            filtered.append(job)
            
    return filtered

def get_mock_data():
    """Data cadangan jika API key belum terpasang"""
    return [
        {
            "id": "mock-1",
            "title": "Staff Administrasi & Keuangan",
            "company": "PT Sawit Makmur Ketapang",
            "location": "Ketapang, Kalimantan Barat",
            "via": "JobStreet",
            "posted_at": "1 hari yang lalu",
            "description": "Dibutuhkan Staff Admin Keuangan untuk operasional kebun di wilayah Kabupaten Ketapang...",
            "original_url": "https://www.jobstreet.co.id"
        },
        {
            "id": "mock-2",
            "title": "Supervisor Lapangan Mining",
            "company": "PT Borneo Mineral",
            "location": "Ketapang, Kalbar",
            "via": "Glints",
            "posted_at": "3 hari yang lalu",
            "description": "Memiliki pengalaman minimal 2 tahun di bidang pengawasan tambang lokasi Ketapang...",
            "original_url": "https://glints.com"
        }
    ]

def main():
    print("Mulai mengambil data lowongan...")
    raw_jobs = fetch_google_jobs("lowongan kerja ketapang")
    ketapang_jobs = filter_ketapang(raw_jobs)
    
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M WIB"),
        "total": len(ketapang_jobs),
        "jobs": ketapang_jobs
    }
    
    with open("vacancy.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        
    print(f"Selesai! {len(ketapang_jobs)} lowongan disimpan di vacancy.json")

if __name__ == "__main__":
    main()
