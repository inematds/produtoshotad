"""Worker 1/2 — voiceover local via Kokoro (kokoro_onnx), custo US$ 0.
Reusa os pesos já baixados em ~/.cache/hyperframes/tts (mesmo cache do HyperFrames).

Uso:
  python3 scripts/kokoro_tts.py "script do anúncio aqui" -o output/voz/ad-1.wav [--voice af_heart]
"""
import argparse
import os

MODEL = os.path.expanduser('~/.cache/hyperframes/tts/models/kokoro-v1.0.onnx')
VOICES = os.path.expanduser('~/.cache/hyperframes/tts/voices/voices-v1.0.bin')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('text')
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--voice', default='af_heart')
    ap.add_argument('--speed', type=float, default=1.0)
    a = ap.parse_args()

    if not (os.path.exists(MODEL) and os.path.exists(VOICES)):
        raise SystemExit(
            f'Modelos Kokoro não encontrados em {MODEL} / {VOICES}. '
            'Baixe-os (ver documentação do HyperFrames TTS) antes de rodar este script.'
        )

    from kokoro_onnx import Kokoro
    import soundfile as sf

    kokoro = Kokoro(MODEL, VOICES)
    samples, sr = kokoro.create(a.text, voice=a.voice, speed=a.speed, lang='en-us')
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    sf.write(a.out, samples, sr)
    print(f'✅ {a.out}  ({len(samples)/sr:.1f}s, {sr}Hz, voice={a.voice})')


if __name__ == '__main__':
    main()
