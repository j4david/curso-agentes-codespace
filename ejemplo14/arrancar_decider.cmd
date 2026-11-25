@echo off
rem Arranca el modelo de decision del ejemplo 14 en tu ordenador (http://127.0.0.1:8092).
rem Deja esta ventana abierta mientras uses la herramienta «decidir» de OpenCode; para pararlo, Ctrl+C.
rem Espera la carpeta de llama.cpp en .\llama y el modelo en .\modelo (ver el enunciado P14.1).
cd /d "%~dp0"
llama\llama-server.exe -m modelo\decider-0.8b.Q8_0.gguf --host 127.0.0.1 --port 8092 -c 8192 -b 4096 -ub 2048 --parallel 1
pause
