#!/usr/bin/env python3
# stt_de_keywords_top5_unigrams.py
# Kontinuierliches deutsches STT (Vosk) -> pro Äußerung NUR Top-5 EINZELWÖRTER + Score.

import argparse, json, os, queue, re, sys
from pathlib import Path
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import yake
import socket

# init UDP Server
UDP_IP = "127.0.0.1"
UDP_PORT = 5555


# sehr kompakte deutsche Stopwortliste (kannst du beliebig erweitern)
STOPWORDS_DE = {
    "der","die","das","des","dem","den","ein","eine","einer","einem","einen",
    "und","oder","aber","doch","nur","auch","so","wie","als","dass","weil","wenn",
    "zu","mit","auf","für","im","in","am","an","aus","bei","vom","von","nach","über","unter","zwischen",
    "ist","sind","war","waren","wird","werden","sein","hat","habe","haben","hatte","hatten",
    "nicht","kein","keine","keinen","keinem","mehr","sehr","hier","da","dort",
    "ich","du","er","sie","es","wir","ihr","man","euch","euer","eure","mein","meine","dein","deine",
    "dies","diese","dieser","dieses","jenes","solche","solcher","solches","mal","einmal"
}

def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr, flush=True); sys.exit(code)

def load_model(model_path: str | None) -> Model:
    path = model_path or os.environ.get("VOSK_MODEL_PATH")
    if not path: die("Kein Vosk-Modellpfad. --model angeben oder VOSK_MODEL_PATH setzen.")
    p = Path(path)
    if not p.exists(): die(f"Vosk-Modellpfad existiert nicht: {p}")
    try: return Model(str(p))
    except Exception as e: die(f"Vosk-Modell konnte nicht geladen werden: {e}")

def clean_token(tok: str) -> str:
    # nur Buchstaben/Bindestrich, lowercased; erlaubt äöüß
    t = re.sub(r"[^a-zäöüß\-]", "", tok.lower())
    return t

def pick_top5_unigrams(text: str) -> list[tuple[str, float]]:
    # YAKE auf EINZELWÖRTER (n=1) — wir holen mehr Kandidaten und filtern dann
    extractor = yake.KeywordExtractor(lan="de", n=1, top=50, dedupLim=0.9, windowsSize=1)
    kws = extractor.extract_keywords(text)  # [(wort, score), ...]  — kleinerer Score = besser
    kws.sort(key=lambda kv: kv[1])

    seen = set()
    out: list[tuple[str,float]] = []
    for k, s in kws:
        k = clean_token(k)
        if not k or len(k) < 2:  # min. 2 Zeichen
            continue
        if k in STOPWORDS_DE:
            continue
        if k in seen:
            continue
        seen.add(k)
        out.append((k, s))
        if len(out) == 5:
            break
    return out

def stream_keywords_only(model: Model, samplerate: int, device: int | None, min_utt_chars: int = 8):
    q = queue.Queue()

    def audio_cb(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr, flush=True)
        q.put(bytes(indata))

    rec = KaldiRecognizer(model, samplerate)
    rec.SetWords(True)

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device,
                           dtype="int16", channels=1, callback=audio_cb):
        try:
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    utt = (json.loads(rec.Result()).get("text") or "").strip()
                    if len(utt) < min_utt_chars:
                        continue
                    top5 = pick_top5_unigrams(utt)
                    print(utt)
                    for k, s in top5:
                        print(f"{k}\t{s:.4f}", flush=True)

                        # UDP send
                        MESSAGE = bytes(k+'$'+utt+'#'+str(s),'UTF-8')
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
                        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

                    print("", flush=True)  # Leerzeile zwischen Äußerungen
        except KeyboardInterrupt:
            pass

    # Rest verarbeiten (falls kurz vor Ctrl+C gesprochen)
    final = (json.loads(rec.FinalResult()).get("text") or "").strip()
    if len(final) >= min_utt_chars:
        top5 = pick_top5_unigrams(final)
        for k, s in top5:
            print(f"{k}\t{s:.4f}", flush=True)
        print("", flush=True)

def main():
    ap = argparse.ArgumentParser(description="Kontinuierlich: Top-5 EINZELWORT-Keywords (YAKE) je Äußerung.")
    ap.add_argument("--model", type=str, help="Pfad zum (entpackten) Vosk-DE-Modell.")
    ap.add_argument("--samplerate", type=int, default=16000, help="Samplerate (Default 16000).")
    ap.add_argument("--device", type=int, default=None, help="Input-Device Index.")
    ap.add_argument("--min-utt-chars", type=int, default=8, help="Ignoriere sehr kurze Äußerungen.")
    args = ap.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    model = load_model(args.model)
    stream_keywords_only(model, samplerate=args.samplerate, device=args.device, min_utt_chars=args.min_utt_chars)

if __name__ == "__main__":
    main()
