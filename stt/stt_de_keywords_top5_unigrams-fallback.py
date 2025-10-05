#!/usr/bin/env python3
# stt_de_keywords_top5_unigrams-fallback.py
# Erweiterung: Wenn 60s kein Mikrofoninput -> zufällige Zitate aus Datei senden (alle 30s),
# bis wieder Sprache erkannt wird.

import argparse, json, os, queue, re, sys, time, random, socket
from pathlib import Path
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import yake

# UDP Ziel
UDP_IP = "127.0.0.1"
UDP_PORT = 5555

# kompakte deutsche Stopwortliste
STOPWORDS_DE = {
    "der","die","das","des","dem","den","ein","eine","einer","einem","einen",
    "und","oder","aber","doch","nur","auch","so","wie","als","dass","weil","wenn",
    "zu","mit","auf","für","im","in","am","an","aus","bei","vom","von","nach","über","unter","zwischen",
    "ist","sind","war","waren","wird","werden","sein","hat","habe","haben","hatte","hatten",
    "nicht","kein","keine","keinen","keinem","mehr","sehr","hier","da","dort",
    "ich","du","er","sie","es","wir","ihr","man","euch","euer","eure","mein","meine","dein","deine",
    "dies","diese","dieser","dieses","jenes","solche","solcher","solches","mal","einmal"
}

# ---------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------

def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr, flush=True)
    sys.exit(code)

def load_model(model_path: str | None) -> Model:
    path = model_path or os.environ.get("VOSK_MODEL_PATH")
    if not path:
        die("Kein Vosk-Modellpfad angegeben. (--model oder VOSK_MODEL_PATH)")
    p = Path(path)
    if not p.exists():
        die(f"Vosk-Modellpfad existiert nicht: {p}")
    return Model(str(p))

def clean_token(tok: str) -> str:
    return re.sub(r"[^a-zäöüß\-]", "", tok.lower())

def pick_top5_unigrams(text: str):
    extractor = yake.KeywordExtractor(lan="de", n=1, top=50, dedupLim=0.9, windowsSize=1)
    kws = extractor.extract_keywords(text)
    kws.sort(key=lambda kv: kv[1])
    seen = set()
    out = []
    for k, s in kws:
        k = clean_token(k)
        if not k or len(k) < 2: continue
        if k in STOPWORDS_DE: continue
        if k in seen: continue
        seen.add(k)
        out.append((k, s))
        if len(out) == 5: break
    return out

def send_udp(keyword, utterance, score):
    msg = bytes(f"{keyword}${utterance}#{score}", "utf-8")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg, (UDP_IP, UDP_PORT))
    sock.close()

def process_utterance(utt, min_len):
    utt = (utt or "").strip()
    if len(utt) < min_len:
        return False
    top5 = pick_top5_unigrams(utt)
    print(utt)
    for k, s in top5:
        print(f"{k}\t{s:.4f}", flush=True)
        send_udp(k, utt, s)
    print("", flush=True)
    return True

def load_quotes(file_path):
    if not file_path:
        return []
    p = Path(file_path)
    if not p.exists():
        print(f"[Warnung] Zitate-Datei nicht gefunden: {p}", file=sys.stderr)
        return []
    quotes = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            t = line.strip().strip('"\u201e\u201c\u201f')
            if t:
                quotes.append(t)
    if not quotes:
        print(f"[Warnung] Zitate-Datei ist leer: {p}", file=sys.stderr)
    return quotes

# ---------------------------------------------------
# Hauptschleife mit Fallback
# ---------------------------------------------------

def stream_with_fallback(model, samplerate, device, min_utt_chars,
                         inactivity_seconds, fallback_interval, quotes):

    q = queue.Queue()

    def audio_cb(indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    rec = KaldiRecognizer(model, samplerate)
    rec.SetWords(True)

    last_activity = time.monotonic()
    in_fallback = False
    next_quote_time = None

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device,
                           dtype="int16", channels=1, callback=audio_cb):
        print("[Info] STT gestartet. Warte auf Sprache...", flush=True)

        try:
            while True:
                now = time.monotonic()

                # check for inactivity
                if not in_fallback and now - last_activity > inactivity_seconds and quotes:
                    in_fallback = True
                    next_quote_time = now
                    print("[Info] Keine Sprache erkannt – Fallback aktiviert.", flush=True)

                # check if fallback active
                if in_fallback and now >= next_quote_time:
                    quote = random.choice(quotes)
                    print(f"[Fallback] Zitat: {quote}", flush=True)
                    process_utterance(quote, min_len=1)
                    next_quote_time = now + fallback_interval

                # handle audio
                try:
                    data = q.get(timeout=0.2)
                except queue.Empty:
                    continue

                if rec.AcceptWaveform(data):
                    utt = json.loads(rec.Result()).get("text", "").strip()
                    if process_utterance(utt, min_utt_chars):
                        last_activity = time.monotonic()
                        if in_fallback:
                            in_fallback = False
                            print("[Info] Mikrofon-Aktivität erkannt – Fallback deaktiviert.", flush=True)

        except KeyboardInterrupt:
            print("\n[Beendet durch Benutzer]", flush=True)

# ---------------------------------------------------
# main()
# ---------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Deutsches STT mit automatischem Zitat-Fallback bei Inaktivität.")
    ap.add_argument("--model", type=str, required=True, help="Pfad zum Vosk-DE-Modell.")
    ap.add_argument("--quotes-file", type=str, required=False, help="Pfad zur .txt-Datei mit Zitaten.")
    ap.add_argument("--samplerate", type=int, default=16000)
    ap.add_argument("--device", type=int, default=None)
    ap.add_argument("--min-utt-chars", type=int, default=8)
    ap.add_argument("--inactivity-seconds", type=int, default=60)
    ap.add_argument("--fallback-interval", type=int, default=30)
    args = ap.parse_args()

    model = load_model(args.model)
    quotes = load_quotes(args.quotes_file)
    stream_with_fallback(model, args.samplerate, args.device,
                         args.min_utt_chars, args.inactivity_seconds,
                         args.fallback_interval, quotes)

if __name__ == "__main__":
    main()
