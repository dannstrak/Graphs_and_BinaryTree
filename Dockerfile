FROM python:3.11-slim

# --- Dependencias de sistema: X virtual, VNC, noVNC, y libs que Tkinter necesita ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11vnc \
    python3-tk \
    tk \
    fluxbox \
    novnc \
    websockify \
    wget \
    fonts-dejavu \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- Copiamos el proyecto TAL CUAL ---
COPY . /app

# --- Instalamos dependencias de Python del proyecto ---
RUN pip install --no-cache-dir customtkinter Pillow

# --- Variables de entorno para el display virtual ---
ENV DISPLAY=:99
ENV SCREEN_RES=1280x800x24

# Puerto que expone noVNC (Azure enrutará el tráfico web hacia aquí)
EXPOSE 8080

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
