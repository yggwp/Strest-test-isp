#!/bin/bash
echo "Menjalankan Internet Monitoring..."
echo "Aplikasi ini memonitor koneksi Anda dan menyimpannya di internet_log.csv"
echo "Tekan Ctrl+C di terminal ini kapan saja untuk mematikannya."
echo ""
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ ! -d "$DIR/venv" ]; then
    echo "Peringatan: Venv belum ditemukan! Memulai installasi otomatis..."
    bash "$DIR/install.sh"
fi

cd "$DIR"
./venv/bin/python monitor_internet.py
