#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=== Instalasi Background Service Ubuntu ==="
echo "Mendeteksi lokasi folder saat ini di: $DIR"

SCRIPT_OWNER=$(stat -c '%U' "$DIR/setup_service.sh")
echo "Mengeset user service menjadi: $SCRIPT_OWNER agar terhindar dari isu hak akses file log..."

echo "Mengupdate file service secara otomatis agar selaras dengan lokasi direktori..."

sed -i "s|^User=.*|User=$SCRIPT_OWNER|g" "$DIR/internet-monitor.service"
sed -i "s|^WorkingDirectory=.*|WorkingDirectory=$DIR|g" "$DIR/internet-monitor.service"
sed -i "s|^ExecStart=.*|ExecStart=$DIR/venv/bin/python '$DIR/monitor_internet.py'|g" "$DIR/internet-monitor.service"

echo ""
echo "Melakukan copy service..."
sudo cp "$DIR/internet-monitor.service" /etc/systemd/system/

echo "Me-reload systemd..."
sudo systemctl daemon-reload

echo "Mengaktifkan Start Otomatis Setiap PC Dinyalakan..."
sudo systemctl enable internet-monitor.service

echo "Menjalankan script ke background..."
sudo systemctl start internet-monitor.service

echo ""
echo "✅ Berhasil! Script sekarang berjalan non-stop di balik layar."
echo "Untuk mengecek status apakah sedang jalan: sudo systemctl status internet-monitor.service"
echo "Untuk melihat log: sudo journalctl -u internet-monitor.service -f"
echo "Untuk mematikan: sudo systemctl stop internet-monitor.service"
