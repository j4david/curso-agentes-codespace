@echo off
rem Arranca el modelo local de este ejemplo en tu ordenador (http://127.0.0.1:8092).
rem Deja esta ventana abierta mientras pasas los correos; para pararlo, Ctrl+C.
rem Espera la carpeta de llama.cpp en .\llama y el modelo en .\modelo (ver LEEME.md).
rem Si ya lo tienes del ejemplo 14, vale el mismo: copia sus carpetas llama y modelo aqui.
cd /d "%~dp0"
if not exist llama\llama-server.exe (
  echo Falta llama\llama-server.exe. Mira el apartado "Modelo local" de LEEME.md.
  pause
  exit /b 1
)
if not exist modelo\decider-0.8b.Q8_0.gguf (
  echo Falta modelo\decider-0.8b.Q8_0.gguf. Mira el apartado "Modelo local" de LEEME.md.
  pause
  exit /b 1
)
llama\llama-server.exe -m modelo\decider-0.8b.Q8_0.gguf --host 127.0.0.1 --port 8092 -c 8192 -b 4096 -ub 2048 --parallel 1
pause
