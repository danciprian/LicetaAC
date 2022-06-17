@echo off

@REM Script for flashing the ESP32 device board
@REM 1. Erase the flash
@REM 2. Write the bootloader
@REM 3. Upload the python application files

set COMPORT="COM8"
set BOOTLOADER_PATH="bootloader\esp32-20210418-v1.15.bin"
set START_ADDR=0x1000

echo ====================================== ERASE FLASH ======================================
esptool.py erase_flash
echo =================================== FLASH BOOTLOADER ====================================
esptool.py --port %COMPORT% write_flash %START_ADDR% %BOOTLOADER_PATH%
echo ================================= UPLOAD Python files ===================================
echo Uploading mqtt_as.py file
ampy --port %COMPORT% put mqtt_as.py
echo Uploading boot.py file
ampy --port %COMPORT% put BME280.py
echo Uploading main.py file
ampy --port %COMPORT% put main.py

echo ===================================== COMMPLETED ========================================