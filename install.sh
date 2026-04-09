#!/bin/bash
echo "=== Setup Internet Monitoring ==="
echo "Meminta akses sudo untuk menginstall paket pendukung (python3-venv & network-manager)..."
sudo apt update
sudo apt install python3-venv network-manager iputils-ping -y

echo ""
echo "Membersihkan sisa VENV dari PC sebelah (Mencegah Error GLIBC_2.38)..."
rm -rf venv

echo "Membuat environment Python lokal yang baru..."
python3 -m venv venv

echo ""
echo "Menginstall library Python yang dibutuhkan..."
./venv/bin/pip install -r requirements.txt

echo ""
echo "Instalasi Selesai! 🎉"
echo "Sekarang Anda dapat menjalankan script ini menggunakan perintah:"
echo "  ./start.sh"
echo "Atau jalankan sebagai background service (24 jam) menggunakan:"
echo "  bash setup_service.sh"
