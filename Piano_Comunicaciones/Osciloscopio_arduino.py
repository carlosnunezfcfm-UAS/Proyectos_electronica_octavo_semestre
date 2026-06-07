import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# -----------------------------------
# CONFIGURACIÓN
# -----------------------------------

PUERTO = 'COM3'
BAUDIOS = 250000

arduino = serial.Serial(PUERTO, BAUDIOS)

N = 1024

canal1 = deque([0] * N, maxlen=N)
canal2 = deque([0] * N, maxlen=N)

# -----------------------------------
# VENTANA
# -----------------------------------

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))

# -----------------------------------
# OSCILOSCOPIO
# -----------------------------------

linea1, = ax1.plot(np.zeros(N), linewidth=2, label='Canal A0')
linea2, = ax1.plot(np.zeros(N), linewidth=2, label='Canal A1')

ax1.set_title("Señal Temporal")
ax1.set_ylim(-0.1, 5.1)
ax1.set_xlim(0, N)
ax1.set_ylabel("Voltaje (V)")
ax1.grid(True)
ax1.legend()

ax1.axhline(y=0, linestyle='--', linewidth=1)
ax1.axhline(y=5, linestyle='--', linewidth=1)

texto_volt = ax1.text(
    0.01,
    0.95,
    "",
    transform=ax1.transAxes
)

# -----------------------------------
# FFT
# -----------------------------------

fft1_linea, = ax2.plot([], [], linewidth=2, label='FFT A0')
fft2_linea, = ax2.plot([], [], linewidth=2, label='FFT A1')

ax2.set_title("FFT")
ax2.set_xlabel("Frecuencia (Hz)")
ax2.set_ylabel("Magnitud")
ax2.grid(True)
ax2.legend()

texto_freq = ax2.text(
    0.01,
    0.95,
    "",
    transform=ax2.transAxes
)

# -----------------------------------
# ACTUALIZACIÓN
# -----------------------------------

def actualizar(frame):

    while arduino.in_waiting >= 2:

        dato1 = ord(arduino.read())
        dato2 = ord(arduino.read())

        v1 = dato1 * 5.0 / 255.0
        v2 = dato2 * 5.0 / 255.0

        canal1.append(v1)
        canal2.append(v2)

    datos1 = np.array(canal1)
    datos2 = np.array(canal2)

    # Señal temporal
    linea1.set_ydata(datos1)
    linea2.set_ydata(datos2)

    texto_volt.set_text(
        f"A0 = {datos1[-1]:.2f} V    A1 = {datos2[-1]:.2f} V"
    )

    # FFT Canal 1
    fft1 = np.abs(
        np.fft.rfft(datos1 - np.mean(datos1))
    )

    # FFT Canal 2
    fft2 = np.abs(
        np.fft.rfft(datos2 - np.mean(datos2))
    )

    frecuencias = np.fft.rfftfreq(
        len(datos1),
        d=0.0002
    )

    fft1_linea.set_data(frecuencias, fft1)
    fft2_linea.set_data(frecuencias, fft2)

    ax2.set_xlim(0, 5000)

    # Frecuencia dominante A0
    if len(fft1) > 1:
        idx1 = np.argmax(fft1[1:]) + 1
        freq1 = frecuencias[idx1]
    else:
        freq1 = 0

    # Frecuencia dominante A1
    if len(fft2) > 1:
        idx2 = np.argmax(fft2[1:]) + 1
        freq2 = frecuencias[idx2]
    else:
        freq2 = 0

    texto_freq.set_text(
        f"A0: {freq1:.1f} Hz   |   A1: {freq2:.1f} Hz"
    )

    ax2.relim()
    ax2.autoscale_view(True, True, True)

    return (
        linea1,
        linea2,
        fft1_linea,
        fft2_linea,
        texto_volt,
        texto_freq
    )

# -----------------------------------
# ANIMACIÓN
# -----------------------------------

ani = FuncAnimation(
    fig,
    actualizar,
    interval=20,
    cache_frame_data=False
)

plt.tight_layout()

try:
    plt.get_current_fig_manager().window.state('zoomed')
except:
    pass

plt.show()