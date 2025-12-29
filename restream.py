#!/usr/bin/env python3
"""
Simple ffmpeg restream helper
Usage:
    python restream.py --source "SOURCE_URL" --outdir ./hls_out --segment 6

This will run ffmpeg and create HLS files in the output directory.
Requires ffmpeg installed and accessible in PATH.
"""
import argparse
import os
import shutil
import subprocess
import sys


def main():
    p = argparse.ArgumentParser(description='FFmpeg restream to HLS')
    p.add_argument('--source', '-s', required=True, help='Source stream URL')
    p.add_argument('--outdir', '-o', default='hls_out', help='Output directory for HLS')
    p.add_argument('--segment', '-t', type=int, default=6, help='HLS segment duration (seconds)')
    args = p.parse_args()

    if not shutil.which('ffmpeg'):
        print('ffmpeg not found in PATH. Install ffmpeg first.', file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.outdir, exist_ok=True)
    index = os.path.join(args.outdir, 'index.m3u8')

    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'info',
        '-i', args.source,
        '-c:v', 'copy', '-c:a', 'copy',
        '-f', 'hls',
        '-hls_time', str(args.segment),
        '-hls_list_size', '6',
        '-hls_flags', 'delete_segments+append_list',
        index
    ]

    print('Running:', ' '.join(cmd))

    # Start ffmpeg as background process
    try:
        ffmpeg_proc = subprocess.Popen(cmd)
        print(f'FFmpeg started (PID={ffmpeg_proc.pid})')
    except Exception as e:
        print('Failed to start ffmpeg:', e, file=sys.stderr)
        sys.exit(1)

    # Start a simple static HTTP server to serve the output directory
    server_port = 8081
    try:
        server_cmd = [sys.executable, '-m', 'http.server', str(server_port), '--directory', args.outdir]
        server_proc = subprocess.Popen(server_cmd)
        print(f'Static server started at http://localhost:{server_port}/ (PID={server_proc.pid})')
    except Exception as e:
        print('Failed to start static server:', e, file=sys.stderr)
        # If server failed, allow ffmpeg to keep running, but warn

    try:
        print('Press Ctrl+C to stop.')
        ffmpeg_proc.wait()
    except KeyboardInterrupt:
        print('\nStopping processes...')
        try:
            ffmpeg_proc.terminate()
        except Exception:
            pass
        try:
            server_proc.terminate()
        except Exception:
            pass
        ffmpeg_proc.wait()


if __name__ == '__main__':
    main()
