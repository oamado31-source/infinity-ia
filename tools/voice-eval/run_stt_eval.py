#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compare local STT models on Portuguese phrases in the style of the in-game box (ADR-0127).

Audio comes from the maintainer's own recordings (`--record`, kept in ~/.infinity-ai/voice-eval,
outside the repository) or from macOS pt-BR voices (`--say`, only a smoke test: synthetic speech is
cleaner than a person). For each model, with and without the vocabulary prompt, it reports the word
error rate (edit distance over normalized words), how many proper names came out right and the
seconds per phrase. The JSON report goes to ~/.infinity-ai/voice-eval/.

    python tools/voice-eval/run_stt_eval.py --say
    python tools/voice-eval/run_stt_eval.py --record          # record each phrase once
    python tools/voice-eval/run_stt_eval.py --recorded        # evaluate the recordings
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))

from infinity_ai.voice.capture import FfmpegRecorder, speech_level  # noqa: E402
from infinity_ai.voice.stt import SttError, WhisperCppStt, vocabulary_prompt  # noqa: E402

PHRASES = ROOT / 'tests' / 'voice_eval' / 'phrases.pt_BR.json'
OUT = Path.home() / '.infinity-ai' / 'voice-eval'
MODELS = (Path.home() / '.infinity-ai' / 'models' / 'ggml-large-v3-turbo-q5_0.bin',
          Path.home() / 'Projetos' / 'cargotalk-stt' / 'models' / 'ggml-small.bin')
SAY_VOICES = ('Luciana', 'Eddy (Português (Brasil))', 'Flo (Português (Brasil))')


def words(text: str) -> list[str]:
    plain = unicodedata.normalize('NFKD', text.lower())
    plain = ''.join(c for c in plain if not unicodedata.combining(c))
    return [w for w in ''.join(c if c.isalnum() else ' ' for c in plain).split() if w]


def wer(reference: str, hypothesis: str) -> float:
    ref, hyp = words(reference), words(hypothesis)
    row = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, row[0] = row[0], i
        for j, h in enumerate(hyp, 1):
            prev, row[j] = row[j], min(row[j] + 1, row[j - 1] + 1, prev + (r != h))
    return row[-1] / max(1, len(ref))


def names_right(names: list[str], hypothesis: str) -> int:
    hyp = ' '.join(words(hypothesis))
    return sum(' '.join(words(n)) in hyp for n in names)


def to_wav(src: Path, dst: Path) -> Path:
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(src),
                    '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', str(dst)], check=True)
    return dst


def say_audio(phrases: list[dict], folder: Path) -> list[tuple[dict, str, Path]]:
    out = []
    for voice in SAY_VOICES:
        for p in phrases:
            aiff = folder / f'{p["id"]}-{len(out)}.aiff'
            subprocess.run(['say', '-v', voice, '-o', str(aiff), p['text']], check=True)
            out.append((p, f'say:{voice.split()[0]}', to_wav(aiff, aiff.with_suffix('.wav'))))
    return out


def record(phrases: list[dict], device: str | None) -> None:
    folder = OUT / 'recordings'
    folder.mkdir(parents=True, exist_ok=True)
    for p in phrases:
        input(f'\n[{p["id"]}] Enter para começar e diga: "{p["text"]}"')
        rec = FfmpegRecorder(device=device, max_seconds=15)
        rec.start()
        input('   gravando... Enter para parar')
        wav = rec.stop()
        dest = folder / f'{p["id"]}.wav'
        dest.write_bytes(wav.read_bytes())
        rec.cancel()
        print(f'   salvo ({speech_level(dest):.0f} de nível)')


def recorded_audio(phrases: list[dict]) -> list[tuple[dict, str, Path]]:
    folder = OUT / 'recordings'
    return [(p, 'voz', folder / f'{p["id"]}.wav') for p in phrases
            if (folder / f'{p["id"]}.wav').is_file()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument('--say', action='store_true', help='macOS pt-BR voices (smoke test)')
    src.add_argument('--record', action='store_true', help='record each phrase with the mic')
    src.add_argument('--recorded', action='store_true', help='evaluate the recordings')
    ap.add_argument('--model', type=Path, action='append', help='whisper.cpp model (repeatable)')
    ap.add_argument('--mic-device', default=None)
    args = ap.parse_args()
    doc = json.loads(PHRASES.read_text(encoding='utf-8'))
    phrases = doc['phrases']
    if args.record:
        record(phrases, args.mic_device)
        return 0
    models = [m for m in (args.model or MODELS) if m.is_file()]
    if not models:
        print('nenhum modelo encontrado')
        return 1
    prompt = vocabulary_prompt(doc['names'])
    with tempfile.TemporaryDirectory() as tmp:
        audio = say_audio(phrases, Path(tmp)) if args.say else recorded_audio(phrases)
        if not audio:
            print('sem áudio: grave antes com --record')
            return 1
        results = []
        for model in models:
            stt = WhisperCppStt(model)
            for use_prompt in (False, True):
                rows = []
                for p, source, wav in audio:
                    began = time.monotonic()
                    try:
                        text = stt.transcribe(wav, prompt=prompt if use_prompt else '')
                    except SttError as exc:
                        text = f'<erro {exc}>'
                    rows.append({'id': p['id'], 'source': source, 'text': text,
                                 'wer': round(wer(p['text'], text), 3),
                                 'names': len(p['names']),
                                 'names_right': names_right(p['names'], text),
                                 'seconds': round(time.monotonic() - began, 2)})
                n = len(rows)
                summary = {'model': model.name, 'prompt': use_prompt, 'phrases': n,
                           'wer': round(sum(r['wer'] for r in rows) / n, 3),
                           'names': f'{sum(r["names_right"] for r in rows)}/'
                                    f'{sum(r["names"] for r in rows)}',
                           'mean_seconds': round(sum(r['seconds'] for r in rows) / n, 2),
                           'max_seconds': max(r['seconds'] for r in rows)}
                print(f'{model.name:34} prompt={"sim" if use_prompt else "não":3} '
                      f'WER={summary["wer"]:.3f} nomes={summary["names"]:7} '
                      f'tempo={summary["mean_seconds"]:.2f}s(máx {summary["max_seconds"]:.2f}s)')
                results.append({**summary, 'rows': rows})
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    path = OUT / f'stt-{stamp}.json'
    path.write_text(json.dumps({'schema': 'infinity-ai.voice-eval-report.v1',
                                'source': 'say' if args.say else 'recorded', 'prompt': prompt,
                                'results': results}, ensure_ascii=False, indent=1),
                    encoding='utf-8')
    print(f'relatório em {path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
