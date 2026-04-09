import time
import subprocess
import psutil
import os
import csv
import requests
import urllib.parse
from datetime import datetime
import re

# ==========================================
# KONFIGURASI WHATSAPP (FONNTE API)
# ==========================================
WA_API_KEY = "FJ6iVFCQKvXESoYZSSXt"    # Token API Fonnte Anda
WA_TARGET = "120363409930034361@g.us"  # ID Grup "Test" (Didapat otomatis dari API Fonnte)
# ==========================================

LOG_FILE = "internet_log.csv"
SPEEDTEST_INTERVAL_MINUTES = 30 # Jalankan speedtest setiap 30 menit untuk test performa
WA_INTERVAL_MINUTES = 60        # Kirim laporan ke WhatsApp setiap 1 jam

def get_ping():
    loss = "0%"
    avg_ping = "N/A"
    try:
        # Menjalankan ping tanpa '-q' agar output per baris tersedia
        process = subprocess.Popen(['ping', '-c', '55', '8.8.8.8'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        output_lines = []
        # Menulis log ping dengan timestamp ke internet_log.txt
        with open("internet_log.txt", "a", encoding="utf-8") as log_file:
            for line in process.stdout:
                line_clean = line.strip()
                if line_clean:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_file.write(f"[{timestamp}] {line_clean}\n")
                    log_file.flush() # Memastikan log langsung masuk disk per detik
                output_lines.append(line_clean)
                
        process.wait()
        
        # Jika ping exit code bukan 0 (berarti ada error atau packet loss), kita set fallback ke 100% loss.
        # Nanti nilai ini akan tertimpa oleh pembacaan regex jika memang output summary-nya masih ada.
        if process.returncode != 0:
            loss = "100%"
            avg_ping = "Failed"
            
        for line in output_lines:
            loss_match = re.search(r'([\d\.]+)%\s+packet\s+loss', line)
            if loss_match:
                loss = loss_match.group(1) + "%"
            if line.startswith('rtt min/avg/max/mdev'):
                avg_ping = line.split('= ')[1].split('/')[1] + " ms"
                
        return avg_ping, loss
    except Exception as e:
        return "Failed", "100%"

def get_speedtest():
    try:
        import speedtest
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        upload_speed = st.upload() / 1_000_000 # Convert to Mbps
        return f"{download_speed:.2f} Mbps", f"{upload_speed:.2f} Mbps"
    except Exception as e:
        return "Failed", "Failed"

def send_whatsapp(message):
    try:
        url = "https://api.fonnte.com/send"
        headers = {
            "Authorization": WA_API_KEY
        }
        data = {
            "target": WA_TARGET,
            "message": message
        }
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        res_json = response.json()
        
        if res_json.get("status"):
            print(f"WhatsApp alert berhasil terkirim ke Grup '{WA_TARGET}'.")
        else:
            print(f"Gagal mengirim WhatsApp: {res_json.get('reason')}")
    except Exception as e:
        print(f"Error Request WhatsApp: {e}")

def main():
    print("Memulai Internet Monitoring...")
    print(f"File log: {LOG_FILE}")
    print(f"Peringatan WA Aktif: {WA_INTERVAL_MINUTES} Menit Sekali.")
    print("-" * 50)

    # Check/Create CSV Headers
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Uptime", "Ping Avg", "Packet Loss", "DL Used/min (MB)", "UL Used/min (MB)", "Total DL Used (MB)", "Total UL Used (MB)", "Speedtest DL", "Speedtest UL"])

    last_io = psutil.net_io_counters()
    start_io = last_io
    start_time = time.time()

    minutes_passed = 0
    
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uptime_sec = int(time.time() - start_time)
        hrs, rem = divmod(uptime_sec, 3600)
        mins, secs = divmod(rem, 60)
        uptime_str = f"{hrs}h {mins}m {secs}s"
        
        print(f"\n--- Mengumpulkan Metrik [{timestamp}] (Uptime: {uptime_str}) ---")
        print("Menjalankan continuous ping (55 detik) untuk tes packet loss...")
        
        ping_res, loss_res = get_ping()

        # Bandwidth Calc
        curr_io = psutil.net_io_counters()
        dl_min = max(0.0, (curr_io.bytes_recv - last_io.bytes_recv) / 1_000_000)
        ul_min = max(0.0, (curr_io.bytes_sent - last_io.bytes_sent) / 1_000_000)
        dl_total = max(0.0, (curr_io.bytes_recv - start_io.bytes_recv) / 1_000_000)
        ul_total = max(0.0, (curr_io.bytes_sent - start_io.bytes_sent) / 1_000_000)
        last_io = curr_io

        # Speedtest
        spd_dl, spd_ul = "Skipped", "Skipped"
        if minutes_passed % SPEEDTEST_INTERVAL_MINUTES == 0:
            print("Menjalankan Speedtest per 30 menit...")
            spd_dl, spd_ul = get_speedtest()
        
        # Log to CSV True Format
        with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, uptime_str, ping_res, loss_res, f"{dl_min:.2f}", f"{ul_min:.2f}", f"{dl_total:.2f}", f"{ul_total:.2f}", spd_dl, spd_ul])

        print(f"Ping Avg: {ping_res} | Loss: {loss_res} | DL: {dl_min:.2f}MB | UL: {ul_min:.2f}MB")
        print(f"Speed: DL {spd_dl}, UL {spd_ul}")

        # Send WhatsApp Alert pada detik pertama, dan kemudian setiap 60 menit
        if minutes_passed % WA_INTERVAL_MINUTES == 0:
            print("Waktunya mengirim pesan ke WhatsApp...")
            msg = f"⏱️ *Internet Report [{timestamp}]*\n"
            msg += f"⏳ *Uptime Tester:* {uptime_str}\n\n"
            msg += f"📡 *Ping Avg:* {ping_res}\n"
            msg += f"⚠️ *Packet Loss:* {loss_res}\n"
            msg += f"📥 *DL Terpakai 1 Min:* {dl_min:.2f} MB\n"
            msg += f"📤 *UL Terpakai 1 Min:* {ul_min:.2f} MB\n"
            msg += f"➖ *Total DL 1 Jam:* {dl_total:.2f} MB\n"
            msg += f"➖ *Total UL 1 Jam:* {ul_total:.2f} MB\n"
            
            # Khusus kalau pas berbarengan sama jam speedtest (karena 60 menit dibagi 30 kan pas)
            if spd_dl != "Skipped":
                msg += f"\n🚀 *SPEEDTEST (Asli)*\n⬇️ {spd_dl}\n⬆️ {spd_ul}"
                
            send_whatsapp(msg)
            
            # Reset tracker bandwidth setiap 1 jam, sehingga "Total DL 1 Jam" akurat untuk 1 jam ke depan
            if minutes_passed > 0:
                start_io = curr_io

        minutes_passed += 1
        
        # Wait until next minute (karena ping sudah memakan waktu 55 detik, sisanya 5 detik)
        time.sleep(5)

if __name__ == "__main__":
    main()
