TSKILL %4
Timeout /t 3 /nobreak
del AudioMixer.exe
@echo off
move %1 %2
rename "%3" "AudioMixer.exe"
