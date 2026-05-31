"""
Sonic logo de Recontrata: sintetiza un sound design a medida y lo muxea con el
video de la animación. Narrativa sonora "el ciclo se cierra / vuelve a empezar":

  0.00s  cuadro entra        -> thump suave + whoosh de aire ascendente
  0.38s  se traza el arco    -> shimmer/riser brillante que sube con el trazo
  1.66s  giro de cierre      -> arpegio de campanas ascendente (C-E-G-C)
  2.28s  el círculo se cierra-> acorde mayor brillante (la firma) + cola con reverb
  3.20-4.00s  hold           -> el acorde resuena y resuelve, fade out

Todo es sintético (numpy), sin samples externos. Reverb por convolución con una
respuesta-impulso sintética (estéreo, dos IR distintas para dar ancho).

Reproducible:  python add_sound.py
Requiere:      numpy, scipy, imageio-ffmpeg
Salida:        output/recontrata_sonic.wav
               output/recontrata_intro_sound.mp4
               output/recontrata_intro_dark_sound.mp4
"""
import os
import subprocess

import numpy as np
from scipy import signal
from scipy.io import wavfile
from scipy.signal import fftconvolve
import imageio_ffmpeg

SR = 44100
T = 4.0                     # debe cubrir la animación (120 frames @30fps = 4.0s)
OUT = os.path.join(os.path.dirname(__file__), "output")
RNG = np.random.default_rng(7)   # determinista -> reproducible

n = int(SR * T)
t = np.arange(n) / SR
master = np.zeros(n, dtype=np.float64)
wet = np.zeros(n, dtype=np.float64)        # bus que va al reverb (campanas)


def _idx(sec):
    return int(sec * SR)


def add(buf, sig, t0):
    i = _idx(t0)
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def env_ar(length, attack, release, sr=SR):
    """Envolvente ataque-decaimiento exponencial suave (0..1)."""
    tt = np.arange(length) / sr
    a = np.clip(tt / max(attack, 1e-4), 0, 1)
    r = np.exp(-np.clip(tt - attack, 0, None) / max(release, 1e-4))
    return a * r


def bell(freq, dur, amp, ratio=2.0, index=4.0, decay=0.5):
    """Campana FM (carrier + modulador) con decaimiento exponencial."""
    length = _idx(dur)
    tt = np.arange(length) / SR
    e = np.exp(-tt / decay)
    mod = index * e * np.sin(2 * np.pi * freq * ratio * tt)
    sig = e * np.sin(2 * np.pi * freq * tt + mod)
    # pequeño "click" de ataque para definición
    sig[: _idx(0.004)] *= np.linspace(0, 1, _idx(0.004))
    return amp * sig


# notas (Hz)
C5, E5, G5, C6, E6, G4, C4 = 523.25, 659.25, 783.99, 1046.50, 1318.51, 392.0, 261.63

# ----------------------------------------------------------------------------
# A. Entrada del cuadro (0.00s): thump sub + whoosh de aire ascendente
# ----------------------------------------------------------------------------
# thump: seno grave con pitch que cae
th_len = _idx(0.45)
tt = np.arange(th_len) / SR
fsweep = 150 * np.exp(-tt / 0.10) + 55
thump = np.sin(2 * np.pi * np.cumsum(fsweep) / SR) * np.exp(-tt / 0.13) * 0.55
add(master, thump, 0.00)

# whoosh: ruido filtrado pasa-banda con cutoff subiendo + swell
wh_len = _idx(0.60)
noise = RNG.standard_normal(wh_len)
b, a = signal.butter(2, [600 / (SR / 2), 6000 / (SR / 2)], btype="band")
wh = signal.lfilter(b, a, noise)
tt = np.arange(wh_len) / SR
swell = np.sin(np.pi * np.clip(tt / 0.55, 0, 1)) ** 1.5          # sube y baja
wh *= swell * 0.22
add(master, wh, 0.02)

# ----------------------------------------------------------------------------
# B. Trazado del arco (0.38 - 1.54s): riser/shimmer que sube con el trazo
# ----------------------------------------------------------------------------
ri_len = _idx(1.18)
tt = np.arange(ri_len) / SR
prog = np.clip(tt / 1.12, 0, 1)
fr = 420 * (2.6 ** prog)                                          # ~420 -> ~1100 Hz
riser = np.sin(2 * np.pi * np.cumsum(fr) / SR)
trem = 0.85 + 0.15 * np.sin(2 * np.pi * 11 * tt)                  # leve tremolo
renv = np.sin(np.pi * prog) ** 1.2                                # swell in/out
riser *= trem * renv * 0.10
add(master, riser, 0.40)

# chispas (pings cortos agudos) salpicando el trazado
for k in range(7):
    ts = 0.55 + k * 0.13 + RNG.uniform(-0.02, 0.02)
    f = RNG.choice([G5, C6, E6, 1567.98])
    sp = bell(f, 0.22, 0.035, ratio=3.0, index=2.0, decay=0.10)
    add(wet, sp, ts)

# ----------------------------------------------------------------------------
# C. Arpegio de campanas ascendente (1.66 - 2.15s): C5-E5-G5-C6
# ----------------------------------------------------------------------------
arp = [(C5, 1.70, 0.16), (E5, 1.84, 0.18), (G5, 1.98, 0.20), (C6, 2.12, 0.24)]
for f, t0, amp in arp:
    add(wet, bell(f, 1.0, amp, ratio=1.4, index=3.0, decay=0.45), t0)

# ----------------------------------------------------------------------------
# D. Cierre del ciclo (2.28s): acorde mayor brillante (la firma) + cola
# ----------------------------------------------------------------------------
chord = [(C5, 0.34), (E5, 0.30), (G5, 0.30), (C6, 0.34), (E6, 0.22)]
for f, amp in chord:
    add(wet, bell(f, 1.7, amp, ratio=2.0, index=3.5, decay=1.30), 2.28)
# golpe de cuerpo grave que ancla el acorde
add(master, bell(C4, 1.4, 0.20, ratio=1.0, index=1.0, decay=0.9), 2.28)
add(master, bell(G4, 1.4, 0.12, ratio=1.0, index=1.0, decay=0.9), 2.28)
# brillo final agudo
add(wet, bell(C6 * 2, 1.2, 0.06, ratio=2.0, index=2.0, decay=0.9), 2.30)

# ----------------------------------------------------------------------------
# Reverb estéreo por convolución (IR sintética) sobre el bus 'wet'
# ----------------------------------------------------------------------------
def make_ir(decay, length_s=1.3):
    m = _idx(length_s)
    tt = np.arange(m) / SR
    ir = RNG.standard_normal(m) * np.exp(-tt / decay)
    ir[: _idx(0.005)] = 0
    ir[0] = 1.0                          # componente directa
    return ir / np.max(np.abs(ir))

irL, irR = make_ir(0.42), make_ir(0.48)
wetL = fftconvolve(wet, irL)[:n]
wetR = fftconvolve(wet, irR)[:n]

dry_w = 0.85
rev = 0.30
left = master + dry_w * wet + rev * wetL
right = master + dry_w * wet + rev * wetR

# ----------------------------------------------------------------------------
# Master: soft-clip, normalizar, fades
# ----------------------------------------------------------------------------
def finalize(ch):
    ch = np.tanh(ch * 1.1)
    fi = _idx(0.005)
    ch[:fi] *= np.linspace(0, 1, fi)
    fo = _idx(0.25)
    ch[-fo:] *= np.linspace(1, 0, fo)
    return ch

left, right = finalize(left), finalize(right)
peak = max(np.max(np.abs(left)), np.max(np.abs(right)))
g = 0.92 / peak
stereo = np.stack([left * g, right * g], axis=1)
pcm = (stereo * 32767).astype(np.int16)

wav_path = os.path.join(OUT, "recontrata_sonic.wav")
wavfile.write(wav_path, SR, pcm)
print(f"WAV  -> {wav_path}  ({T:.1f}s, peak {peak:.2f})")

# diagnóstico de timing: RMS por ventanas de 0.25s
win = _idx(0.25)
mono = stereo.mean(axis=1)
print("RMS por 0.25s:")
for k in range(int(T / 0.25)):
    seg = mono[k * win:(k + 1) * win]
    bars = int(np.sqrt(np.mean(seg ** 2)) * 120)
    print(f"  {k*0.25:4.2f}s |{'#' * bars}")

# ----------------------------------------------------------------------------
# Mux con los MP4 (claro y oscuro)
# ----------------------------------------------------------------------------
FF = imageio_ffmpeg.get_ffmpeg_exe()
for src, dst in [("recontrata_intro.mp4", "recontrata_intro_sound.mp4"),
                 ("recontrata_intro_dark.mp4", "recontrata_intro_dark_sound.mp4")]:
    s = os.path.join(OUT, src)
    d = os.path.join(OUT, dst)
    if not os.path.exists(s):
        print(f"[skip] no existe {src}")
        continue
    cmd = [FF, "-y", "-i", s, "-i", wav_path,
           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
           "-shortest", d]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"MP4  -> {d}")

print("Listo.")
