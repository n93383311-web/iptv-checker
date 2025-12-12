import os
import re
import requests

INPUT_DIR = "input_lists3"
OUTPUT_FILE = "output/working.m3u"

# More accurate IPTV URL extractor
URL_REGEX = r'(https?://[^\s"\']+)'

def extract_urls(text):
    return re.findall(URL_REGEX, text)

def test_stream(url):
    try:
        # Follow redirects + bigger timeout
        r = requests.get(
            url,
            timeout=10,
            stream=True,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        # If redirect landed on a non-video URL → skip
        content_type = r.headers.get("Content-Type", "")
        
        # Basic IPTV detection
        if "video" in content_type.lower():
            return True
        if "mpegurl" in content_type.lower():  # M3U8 playlists
            return True
        if r.status_code < 400:  # fallback, many streams don't return Content-Type
            return True

    except Exception as e:
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
            out.write(f"#EXTINF:-1,Stream {i+1}\n{url}\n")

    print(f"Saved to {OUTPUT_FILE}")
    print("=== FINISHED ===")


if __name__ == "__main__":
    main()
