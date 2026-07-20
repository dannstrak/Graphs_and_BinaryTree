#!/bin/bash
set -e

echo ">> Iniciando pantalla virtual (Xvfb) en $DISPLAY ..."
Xvfb $DISPLAY -screen 0 $SCREEN_RES &
sleep 2

echo ">> Iniciando gestor de ventanas (fluxbox) ..."
fluxbox &
sleep 1

echo ">> Iniciando servidor VNC (x11vnc) ..."
x11vnc -display $DISPLAY -forever -shared -nopw -rfbport 5900 &
sleep 1

echo ">> Iniciando noVNC (puente web -> VNC) en el puerto 8080 ..."
websockify --web=/usr/share/novnc/ 8080 localhost:5900 &
sleep 1

echo ">> Lanzando la aplicacion (main.py) sin modificaciones ..."
cd /app/src
PYTHONPATH=/app python main.py

# Si main.py termina, mantenemos el contenedor vivo para poder inspeccionar logs
wait
