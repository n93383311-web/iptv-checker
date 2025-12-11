import os
import re
import asyncio
import aiohttp
import uvloop

INPUT_DIR = "input_lists2"
OUTPUT_FILE = "output/working.m3u"

async def test_stream(session, url):
    try:
        async with session.get(url, timeout=4) as r:
            if r.status < 400:
                return url
    except:
        pass
    return None

def extract_urls(text):
    return re.findall(r'(https?://[^\s]+)', text)

async def process_all(urls):
    conn = aiohttp.TCPConnector(limit=200, ssl=False)  # 200 parallel streams
    timeout = aiohttp.ClientTimeout(total=4)
    headers = {"User-Agent": "IPTV-Checker"}

    async with aiohttp.ClientSession(connector=conn, timeout=timeout, headers=headers) as session:
        tasks = [test_stream(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

    return [url for url in results if url]

async def main():
    print("=== ULTRA FAST IPTV CHECKER ===")

    all_urls = []

    for filename in os.listdir(INPUT_DIR):
        if filename.endswith((".m3u", ".m3u8")):
            with open(os.path.join(INPUT_DIR, filename), "r", errors="ignore") as f:
                all_urls += extract_urls(f.read())

    print(f"Found total {len(all_urls)} URLs")

    working = await process_all(all_urls)

    print(f"Working streams: {len(working)}")

    os.makedirs("output", exist_ok=True)
    with open(OUTPUT_FILE, "w") as out:
        out.write("#EXTM3U\n")
        for i, url in enumerate(working):
            out.write(f"#EXTINF:-1,Stream {i}\n{url}\n")

    print("Saved:", OUTPUT_FILE)

if __name__ == "__main__":
    uvloop.install()
    asyncio.run(main())
