param(
    [Parameter(Mandatory=$true)][string]$SourceUrl,
    [string]$OutputDir = ".\hls_out",
    [int]$SegmentTime = 6
)

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Error "ffmpeg not found in PATH. Install ffmpeg and ensure it's available from the command line."
    exit 1
}

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$index = Join-Path $OutputDir "index.m3u8"

# Basic passthrough HLS stream. Adjust -c:v / -c:a if you need transcoding for browser compatibility.
$ffmpegCmd = @(
    "ffmpeg",
    "-y",
    "-hide_banner",
    "-loglevel", "info",
    "-i", "`"$SourceUrl`"",
    "-c:v", "copy",
    "-c:a", "copy",
    "-f", "hls",
    "-hls_time", "$SegmentTime",
    "-hls_list_size", "6",
    "-hls_flags", "delete_segments+append_list",
    "`"$index`""
) -join ' '

Write-Host "Starting restream from: $SourceUrl"
Write-Host "Output directory: $OutputDir"
Write-Host "Command: $ffmpegCmd"

# Start ffmpeg as a background process
$startInfo = @{ FilePath = 'ffmpeg'; ArgumentList = @( '-y','-hide_banner','-loglevel','info','-i', $SourceUrl, '-c:v','copy','-c:a','copy','-f','hls','-hls_time',$SegmentTime.ToString(),'-hls_list_size','6','-hls_flags','delete_segments+append_list',$index ); NoNewWindow = $false }
$proc = Start-Process @startInfo -PassThru
Write-Host "FFmpeg started (PID: $($proc.Id))."

# Start a simple static HTTP server to serve the output directory
$serverPort = 8081
Write-Host "Starting static server to serve $OutputDir on http://localhost:$serverPort/"
Start-Process -FilePath (Get-Command python).Source -ArgumentList '-m', 'http.server', $serverPort, '--directory', (Resolve-Path $OutputDir) -NoNewWindow
Write-Host "Static server started. Open http://localhost:$serverPort/index.m3u8 in your player."

Write-Host "To stop the restream, stop the FFmpeg process (PID: $($proc.Id)) manually or close this PowerShell session."
