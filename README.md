# Kuota & Internet Monitoring untuk Ubuntu 20 / 22

Script ini dirancang untuk PC/Server Ubuntu untuk melakukan serangkaian *stress-test* dan monitoring performa jaringan internet Anda secara otomatis (setiap 1 menit) dan menyimpannya di file CSV agar Anda memiliki data bukti nyata mengenai performa koneksi.

Aplikasi ini mendata:
1. Ping ke internet stabil (8.8.8.8) secara konstan.
2. Penggunaan/Bandwidth Data baik Menit-per-Menit dan Akumulatif (Download & Upload MB).
3. Auto Speedtest setiap 30 Menit untuk tes performa asli.
4. Menghitung Uptime Tester (Berapa lama aplikasi telah berhasil berjalan non-stop di server).

Semua data ini akan direkap secara rapi di file `internet_log.csv`.

---

## 🛠️ 1. Cara Instalasi (1 Klik)

Buka terminal di dalam folder proyek ini (Atau folder yang sudah ditaruh di PC, seperti `/opt/kuota-monitoring`) dan jalankan skrip instalasi untuk membereskan semua keperluannya otomatis:

```bash
bash install.sh
```

*(Script di atas akan meminta akses Sudo untuk merapikan Virtual Environment & Library)*

---

## ▶️ 2. Cara Menjalankannya secara Manual (Testing Terminal)

Jika Anda hanya ingin menjalankan dan melihat log yang keluar di layar Terminal untuk pengujian awal:

```bash
bash start.sh
```
*(Gunakan `Ctrl+C` pada terminal jika Anda ingin mematikannya)*

---

## 🔄 3. Cara Menjalankan Di Latar Belakang (24 Jam Non-Stop Otomatis)

Jika Anda ingin alat tes ini hidup dan berjalan konsisten bahkan ketika Ubuntu baru saja di-*restart*, cukup modifikasi sedikit file `internet-monitor.service` untuk memberitahu lokasinya (default tertulis ke folder `/opt`), lalu langsung jalankan setup service-nya dengan satu baris printah:

```bash
bash setup_service.sh
```

### 📋 Tambahan:
- **Melihat Log Terminal asli jika Service sedang berjalan:**
  `sudo journalctl -u internet-monitor.service -f`
- **Pemberhentian Service Penuh:**
  `sudo systemctl stop internet-monitor.service`
