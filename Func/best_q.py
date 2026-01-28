const MAX_SIZE = 2 * 1024 * 1024 * 1024; // 2GB
const PREFERRED_QUALITY = 720;

async function getBestQualityUnder2GB(obj) {
    let streams = obj.videos[0].streams
        .map(s => ({ ...s, quality: Number(s.quality) }));

    // 🔹 Sort: 720p first, then highest → lowest
    streams.sort((a, b) => {
        if (a.quality === PREFERRED_QUALITY) return -1;
        if (b.quality === PREFERRED_QUALITY) return 1;
        return b.quality - a.quality;
    });

    for (const stream of streams) {
        try {
            // ================= MP4 =================
            if (stream.url.includes(".mp4")) {
                const head = await fetch(stream.url, { method: "HEAD" });
                const size = Number(head.headers.get("content-length") || 0);

                if (size > 0 && size <= MAX_SIZE) {
                    return {
                        quality: stream.quality,
                        url: stream.url,
                        type: "mp4",
                        sizeBytes: size,
                        sizeGB: (size / 1024 / 1024 / 1024).toFixed(2)
                    };
                }
            }

            // ================= M3U8 =================
            if (stream.url.includes(".m3u8")) {
                const playlist = await fetch(stream.url).then(r => r.text());

                const baseUrl = stream.url.split("/").slice(0, -1).join("/");
                const segments = playlist
                    .split("\n")
                    .filter(l => l && !l.startsWith("#"))
                    .map(seg => seg.startsWith("http") ? seg : `${baseUrl}/${seg}`);

                let totalSize = 0;

                for (const seg of segments) {
                    const head = await fetch(seg, { method: "HEAD" });
                    const segSize = Number(head.headers.get("content-length") || 0);
                    totalSize += segSize;

                    if (totalSize > MAX_SIZE) break;
                }

                if (totalSize > 0 && totalSize <= MAX_SIZE) {
                    return {
                        quality: stream.quality,
                        url: stream.url,
                        type: "m3u8",
                        sizeBytes: totalSize,
                        sizeGB: (totalSize / 1024 / 1024 / 1024).toFixed(2)
                    };
                }
            }

        } catch (e) {
            continue; // try next option
        }
    }

    return null;
}
