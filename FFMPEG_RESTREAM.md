# FFmpeg Re-stream Helper

This repository includes two simple helpers to re-stream an input stream into an HLS playlist served from a local directory.

Files:
- `restream.py` — Python wrapper that runs `ffmpeg` to produce HLS files.
- `restream.ps1` — PowerShell wrapper for Windows.
- `proxy.py` — (existing) optional proxy to serve/modify manifests for browser playback.

Requirements:
- `ffmpeg` installed and available in your PATH.
- (Optional) `python3` to run `restream.py`.

Quick examples:

PowerShell (Windows):
```powershell
# Start restream using PowerShell
.\restream.ps1 -SourceUrl "http://example.com/stream.m3u8" -OutputDir ".\hls_out" -SegmentTime 6
```

Python:
```powershell
python restream.py --source "http://example.com/stream.m3u8" --outdir ./hls_out --segment 6
```

Serve the `hls_out` directory with a static server (or use the existing local `python -m http.server 8080`):

```powershell
python -m http.server 8081 --directory hls_out
```

Then point your player at `http://localhost:8081/index.m3u8` (or route via `proxy.py` if needed).

Notes:
- The scripts use `-c copy` (no transcoding) for minimal CPU usage. If browser compatibility requires different codecs, change `-c:v`/`-c:a` to appropriate encoders (e.g. `-c:v libx264 -c:a aac`).
- This is for development/testing. For production, use a robust re-streaming pipeline and proper TLS/CORS configuration.
