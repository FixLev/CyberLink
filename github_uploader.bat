@echo off
chcp 65001 >nul
title GitHub Uploader - CyberLink

:: ============================================
:: CyberLink - Автоматическая выгрузка на GitHub
:: Версия: 1.0.0
:: Репозиторий: https://github.com/FixLev/CyberLink
:: ============================================

setlocal enabledelayedexpansion

:: Цвета
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"
set "RESET=[0m"

:: ============================================
:: Основная часть
:: ============================================

cls
echo.
echo %CYAN%======================================================================%RESET%
echo %CYAN%   ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██╗     ██╗███╗   ██╗██╗  ██╗%RESET%
echo %CYAN%  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██║     ██║████╗  ██║██║ ██╔╝%RESET%
echo %CYAN%  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██║     ██║██╔██╗ ██║█████╔╝ %RESET%
echo %CYAN%  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██║     ██║██║╚██╗██║██╔═██╗ %RESET%
echo %CYAN%  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║███████╗██║██║ ╚████║██║  ██╗%RESET%
echo %CYAN%   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝%RESET%
echo %CYAN%======================================================================%RESET%
echo %GREEN%🚀 GitHub Uploader v1.0.0%RESET%
echo %CYAN%======================================================================%RESET%
echo.

:: ============================================
:: Проверка Git
:: ============================================
echo %BLUE%[1/7] Проверка Git...%RESET%
where git >nul 2>nul
if errorlevel 1 (
    echo %RED%❌ Git не найден!%RESET%
    echo %YELLOW%Установите Git: https://git-scm.com/download/win%RESET%
    pause
    exit /b 1
)
echo %GREEN%✅ Git найден%RESET%
echo.

:: ============================================
:: Проверка репозитория
:: ============================================
echo %BLUE%[2/7] Проверка репозитория...%RESET%
if not exist ".git" (
    echo %YELLOW%⚠️ Git репозиторий не найден. Инициализация...%RESET%
    git init
    git remote add origin https://github.com/FixLev/CyberLink.git
    echo %GREEN%✅ Репозиторий инициализирован%RESET%
) else (
    echo %GREEN%✅ Репозиторий найден%RESET%
)
echo.

:: ============================================
:: Проверка подключения к GitHub
:: ============================================
echo %BLUE%[3/7] Проверка подключения к GitHub...%RESET%
ping -n 2 github.com >nul 2>nul
if errorlevel 1 (
    echo %RED%❌ Нет подключения к интернету!%RESET%
    echo %YELLOW%Подключитесь к интернету и попробуйте снова%RESET%
    pause
    exit /b 1
)
echo %GREEN%✅ Интернет доступен%RESET%
echo.

:: ============================================
:: Проверка изменений
:: ============================================
echo %BLUE%[4/7] Проверка изменений...%RESET%
git fetch origin >nul 2>nul

:: Проверяем, есть ли изменения
git status --porcelain > temp_status.txt
set "HAS_CHANGES=0"
for /f "tokens=*" %%a in (temp_status.txt) do (
    set "HAS_CHANGES=1"
)
del temp_status.txt 2>nul

if "%HAS_CHANGES%"=="0" (
    echo %YELLOW%⚠️ Нет изменений для выгрузки%RESET%
    echo.
    echo %CYAN%Хотите проверить наличие обновлений с GitHub?%RESET%
    choice /C:YN /M "Проверить? (Y/N)"
    if errorlevel 2 goto :end
    goto :pull_updates
)
echo %GREEN%✅ Есть изменения для выгрузки%RESET%
echo.

:: ============================================
:: Показываем изменения
:: ============================================
echo %BLUE%[5/7] Измененные файлы:%RESET%
echo %CYAN%------------------------------------------------------------%RESET%
git status --short
echo %CYAN%------------------------------------------------------------%RESET%
echo.

:: ============================================
:: Запрос сообщения коммита
:: ============================================
echo %BLUE%[6/7] Введите сообщение для коммита:%RESET%
set /p "COMMIT_MSG=> "

if "%COMMIT_MSG%"=="" (
    set "COMMIT_MSG=feat: CyberLink update %date% %time%"
)
echo.
echo %GREEN%✅ Сообщение: %COMMIT_MSG%%RESET%
echo.

:: ============================================
:: Выгрузка на GitHub
:: ============================================
echo %BLUE%[7/7] Выгрузка на GitHub...%RESET%
echo.

:: Добавляем все файлы
echo %YELLOW%Добавление файлов...%RESET%
git add .
if errorlevel 1 (
    echo %RED%❌ Ошибка добавления файлов%RESET%
    pause
    exit /b 1
)
echo %GREEN%✅ Файлы добавлены%RESET%

:: Коммит
echo %YELLOW%Создание коммита...%RESET%
git commit -m "%COMMIT_MSG%"
if errorlevel 1 (
    echo %RED%❌ Ошибка создания коммита%RESET%
    pause
    exit /b 1
)
echo %GREEN%✅ Коммит создан%RESET%

:: Пуш
echo %YELLOW%Отправка на GitHub...%RESET%
git push -u origin main
if errorlevel 1 (
    echo.
    echo %RED%❌ Ошибка отправки на GitHub!%RESET%
    echo.
    echo %YELLOW%Возможные причины:%RESET%
    echo 1. Нет прав на запись в репозиторий
    echo 2. Репозиторий защищен паролем
    echo 3. Конфликт с удаленными изменениями
    echo.
    echo %CYAN%Хотите попробовать принудительную отправку? (--force)%RESET%
    choice /C:YN /M "Принудительно? (Y/N)"
    if errorlevel 2 goto :error
    echo.
    echo %YELLOW%Принудительная отправка...%RESET%
    git push -u origin main --force
    if errorlevel 1 (
        echo %RED%❌ Принудительная отправка не удалась%RESET%
        goto :error
    )
    echo %GREEN%✅ Принудительная отправка выполнена%RESET%
) else (
    echo %GREEN%✅ Отправка выполнена успешно%RESET%
)

echo.
echo %GREEN%======================================================================%RESET%
echo %GREEN%🎉 CyberLink успешно выгружен на GitHub!%RESET%
echo %GREEN%======================================================================%RESET%
echo.
echo %CYAN%📊 Статистика:%RESET%
echo   📁 Изменено файлов: %HAS_CHANGES%
echo   📝 Сообщение: %COMMIT_MSG%
echo   🔗 Ссылка: https://github.com/FixLev/CyberLink
echo.
goto :end

:: ============================================
:: Проверка обновлений с GitHub
:: ============================================
:pull_updates
echo.
echo %BLUE%Проверка обновлений с GitHub...%RESET%
git pull origin main
if errorlevel 1 (
    echo %RED%❌ Не удалось получить обновления%RESET%
) else (
    echo %GREEN%✅ Обновления получены%RESET%
)
goto :end

:: ============================================
:: Обработка ошибок
:: ============================================
:error
echo.
echo %RED%======================================================================%RESET%
echo %RED%❌ Ошибка выгрузки на GitHub!%RESET%
echo %RED%======================================================================%RESET%
echo.
echo %YELLOW%💡 Рекомендации:%RESET%
echo 1. Проверьте подключение к интернету
echo 2. Проверьте логин и пароль GitHub
echo 3. Убедитесь что репозиторий существует
echo 4. Попробуйте выполнить вручную:
echo    git add .
echo    git commit -m "ваше сообщение"
echo    git push -u origin main
echo.
echo %CYAN%Открыть страницу репозитория?%RESET%
choice /C:YN /M "Открыть? (Y/N)"
if errorlevel 2 goto :end
start https://github.com/FixLev/CyberLink

:: ============================================
:: Конец
:: ============================================
:end
echo.
pause