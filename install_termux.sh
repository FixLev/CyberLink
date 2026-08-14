#!/data/data/com.termux/files/usr/bin/bash
# CyberLink - Установка для Termux

echo "⚡ CyberLink - Установка для Termux"
echo "===================================="
echo ""

# Обновляем пакеты
echo "📦 Обновление пакетов..."
pkg update -y && pkg upgrade -y

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pkg install -y python python-pip git openssl libffi

# 👇 ОБНОВЛЕНО: Ваш репозиторий
echo "📥 Клонирование CyberLink из FixLev/CyberLink..."
if [ -d "cyberlink" ]; then
    echo "⚠️ Папка cyberlink уже существует. Обновляем..."
    cd cyberlink
    git pull
    cd ..
else
    git clone https://github.com/FixLev/CyberLink.git cyberlink
    cd cyberlink
fi

# Устанавливаем Python пакеты
echo "📦 Установка Python пакетов..."
pip install -r requirements.txt

# Создаем ярлык
echo "🔗 Создание ярлыка..."
cat > ../usr/bin/cyberlink << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/cyberlink
python run.py "$@"
EOF

chmod +x ../usr/bin/cyberlink

echo ""
echo "✅ CyberLink успешно установлен!"
echo ""
echo "🚀 Запуск: cyberlink"
echo "📱 Или перезапустите терминал и введите: cyberlink"
echo ""
echo "⭐ Не забудьте поставить звезду на GitHub!"
echo "🔗 https://github.com/FixLev/CyberLink"