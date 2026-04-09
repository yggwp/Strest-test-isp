import time
import subprocess
import psutil
import os
import csv
import requests
import urllib.parse
from datetime import datetime

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
    try:
        # Pengecekan ping berkelanjutan selama 55 detik (55 paket)
        output = subprocess.check_output(['ping', '-c', '55', '-q', '8.8.8.8'], stderr=subprocess.STDOUT, universal_newlines=True)
        loss = "0%"
        avg_ping = "N/A"
        for line in output.split('\n'):
            if 'packet loss' in line:
                loss = line.split('received, ')[1].split(' packet loss')[0]
            if line.startswith('rtt min/avg/max/mdev'):
                avg_ping = line.split('= ')[1].split('/')[1] + " ms"
        return avg_ping, loss
    except subprocess.CalledProcessError as e:
        # Menangani packet loss berat atau disconnect (ping exit code 1)
        loss = "100%"
        for line in e.output.split('\n'):
            if 'packet loss' in line:
                try:
                    loss = line.split('received, ')[1].split(' packet loss')[0]
                except:
                    pass
        return "Failed", loss
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
        dl_min = (curr_io.bytes_recv - last_io.bytes_recv) / 1_000_000
        ul_min = (curr_io.bytes_sent - last_io.bytes_sent) / 1_000_000
        dl_total = (curr_io.bytes_recv - start_io.bytes_recv) / 1_000_000
        ul_total = (curr_io.bytes_sent - start_io.bytes_sent) / 1_000_000
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

        minutes_passed += 1
        
        # Wait until next minute (karena ping sudah memakan waktu 55 detik, sisanya 5 detik)
        time.sleep(5)

if __name__ == "__main__":
    main()
