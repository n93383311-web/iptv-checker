import os
import re
import requests

INPUT_DIR = "input_lists"
OUTPUT_FILE = "output/working.m3u"

def extract_urls(text):
    return re.findall(r'(https?://[^\s]+)', text)

def test_stream(url, timeout=5):
    try:
        r = requests.get(url, stream=True, timeout=timeout)
        # Working if it starts responding & header is video/TS-like
        if r.status_code < 400:
            return True
    except:
        pass
    return False

def main():
    print("=== IPTV STREAM CHECKER STARTED ===")

    all_working = []

    for filename in os.listdir(INPUT_DIR):
        if not filename.endswith((".m3u", ".m3u8")):
            continue

        filepath = os.path.join(INPUT_DIR, filename)
        print(f"\nReading: {filepath}")

        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        urls = extract_urls(content)
        print(f" → Found {len(urls)} URLs")

        for url in urls:
            print(f"Testing {url} ... ", end="")
            if test_stream(url):
                print("OK")
                all_working.append(url)
            else:
                print("FAILED")

    print(f"\nTotal working streams: {len(all_working)}")

    os.makedirs("output", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("#EXTM3U\n")
        for i, url in enumerate(all_working):
            out.write(f"#EXTINF:-1,Stream {i}\n{url}\n")

    print(f"Saved to {OUTPUT_FILE}")
    print("=== FINISHED ===")


if __name__ == "__main__":
    main()

