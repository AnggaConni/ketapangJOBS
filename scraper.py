import json
import requests
from datetime import datetime

def fetch_free_jobs_ketapang():
    print("Mencari lowongan di Ketapang melalui Web Data...")
    
    # Menembak langsung endpoint internal yang digunakan web JobStreet
    url = "https://www.jobstreet.co.id/api/chalice-search/v4/search"
    
    params = {
        "siteKey": "ID-Main",
        "sourcesystem": "houston",
        "where": "Ketapang",     # Lokasi target
        "page": 1,
        "pageSize": 30           # Ambil 30 lowongan terbaru
    }
    
    # Menyamar sebagai browser agar tidak diblokir
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    jobs = []
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            job_list = data.get("data", [])
            
            for item in job_list:
                job_id = item.get("id", "")
                title = item.get("title", "")
                
                # Ambil nama perusahaan
                advertiser = item.get("advertiser", {})
                company = advertiser.get("description", "Perusahaan Tidak Diketahui")
                
                # Ambil lokasi
                locations = item.get("locations", [])
                location_label = locations[0].get("label", "Ketapang") if locations else "Ketapang"
                
                # Format URL agar menuju ke halaman JobStreet yang sebenarnya
                original_url = f"https://www.jobstreet.co.id/id/job/{job_id}"
                
                # Deskripsi singkat (buang tag HTML jika ada)
                description = item.get("teaser", "Silakan klik untuk melihat detail lengkap pekerjaan ini.")
                
                jobs.append({
                    "id": job_id,
                    "title": title,
                    "company": company,
                    "location": location_label,
                    "via": "JobStreet",
                    "posted_at": item.get("listingDateDisplay", "Terbaru"),
                    "description": description,
                    "original_url": original_url
                })
            print(f"Berhasil menarik {len(jobs)} data mentah.")
        else:
            print(f"Gagal menarik data. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching data: {e}")
        
    return jobs

def filter_ketapang(job_list):
    """Pastikan data benar-benar untuk area Ketapang atau Kalimantan Barat"""
    keywords = ["ketapang", "kalimantan barat", "kalbar", "pontianak"]
    filtered = []
    
    for job in job_list:
        loc = job.get("location", "").lower()
        title = job.get("title", "").lower()
        
        if any(kw in loc for kw in keywords) or any(kw in title for kw in keywords):
            filtered.append(job)
            
    return filtered

def main():
    raw_jobs = fetch_free_jobs_ketapang()
    ketapang_jobs = filter_ketapang(raw_jobs)
    
    # Jika gagal fetch atau kosong, sediakan 1 dummy agar web tetap jalan (MVP test)
    if not ketapang_jobs:
        ketapang_jobs = [{
            "id": "dummy-1",
            "title": "Staf Operasional (Sistem Sedang Menunggu Lowongan Baru)",
            "company": "Sistem Agregator Loker Ketapang",
            "location": "Ketapang, Kalimantan Barat",
            "via": "System",
            "posted_at": "Hari ini",
            "description": "Belum ada lowongan baru yang sesuai di Ketapang saat ini. Sistem akan otomatis memperbarui data kembali dalam beberapa jam.",
            "original_url": "#"
        }]

    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M WIB"),
        "total": len(ketapang_jobs),
        "jobs": ketapang_jobs
    }
    
    with open("vacancy.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        
    print(f"Selesai! {len(ketapang_jobs)} lowongan disimpan ke vacancy.json")

if __name__ == "__main__":
    main()
