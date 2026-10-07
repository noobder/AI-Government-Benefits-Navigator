param(
    [string]$ScriptJson = "script.json",
    [string]$OutDir = "audio",
    [string]$Voice = "Microsoft Zira Desktop"
)

Add-Type -AssemblyName System.Speech

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$lines = Get-Content $ScriptJson -Raw | ConvertFrom-Json

$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try { $synth.SelectVoice($Voice) } catch { Write-Host "Voice '$Voice' not found, using default." }
$synth.Rate = -1  # slightly slower than default for clarity

function Get-WavDurationSeconds($path) {
    # Locate the "data" subchunk explicitly instead of assuming a fixed
    # header offset (SpeechSynthesizer's WAV header layout isn't always the
    # minimal 44-byte PCM header).
    $bytes = [System.IO.File]::ReadAllBytes($path)
    $dataOffset = -1
    $dataSize = 0
    for ($i = 12; $i -lt ($bytes.Length - 8); $i++) {
        if ($bytes[$i] -eq 0x64 -and $bytes[$i+1] -eq 0x61 -and $bytes[$i+2] -eq 0x74 -and $bytes[$i+3] -eq 0x61) {
            $dataSize = [BitConverter]::ToUInt32($bytes, $i + 4)
            $dataOffset = $i + 8
            break
        }
    }
    if ($dataOffset -eq -1) { return 0 }
    # Known encoding: 24000 Hz, mono, 16-bit -> byte rate = 24000 * 1 * 2
    $byteRate = 24000 * 1 * 2
    return [math]::Round($dataSize / $byteRate, 3)
}

$manifest = @()

foreach ($line in $lines) {
    $outPath = Join-Path $OutDir "$($line.id).wav"
    $synth.SetOutputToWaveFile($outPath, (New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(24000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)))
    $synth.Speak($line.narration)
    $synth.SetOutputToNull()

    $duration = Get-WavDurationSeconds $outPath
    Write-Host "$($line.id): $duration s"

    $manifest += [PSCustomObject]@{
        id = $line.id
        narration = $line.narration
        file = "$($line.id).wav"
        duration = $duration
    }
}

$manifest | ConvertTo-Json -Depth 5 | Set-Content -Path (Join-Path $OutDir "manifest.json") -Encoding utf8
Write-Host "Done. Manifest written to $OutDir\manifest.json"
