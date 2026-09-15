# video-recut / prep — corta, trata a cor, transcreve (Groq) e gera a legenda.
# uso: .\tools\video-recut\prep.ps1 -Video "C:\...\IMG_1234.MOV" -Nome "2026-09-meu-video" [-Inicio 16.1] [-Fim 59.2] [-SemCor]
param(
  [Parameter(Mandatory)] [string]$Video,
  [Parameter(Mandatory)] [string]$Nome,
  [double]$Inicio = 0,
  [double]$Fim = 0,
  [switch]$SemCor
)
$ErrorActionPreference = 'Stop'
$inv = [Globalization.CultureInfo]::InvariantCulture
$raiz = $PSScriptRoot
$work = Join-Path $raiz "work\$Nome"
$pub = Join-Path $work "public"
New-Item -ItemType Directory -Force "$pub\fonts", "$pub\vendor" | Out-Null

$livre = (Get-PSDrive C).Free / 1GB
if ($livre -lt 1.5) { throw ("Disco C: com {0:N2} GB livres — libere espaço antes (render precisa ~1 GB)." -f $livre) }

if ($Fim -le 0) { $Fim = [double]::Parse((ffprobe -v error -show_entries format=duration -of csv=p=0 "$Video"), $inv) }
$dur = $Fim - $Inicio
Write-Host ("Corte: {0:N2}s → {1:N2}s ({2:N2}s)" -f $Inicio, $Fim, $dur)

# 1. corte + tratamento de cor + GOP 30 (renderer congela em GOP esparso)
$cor = "hqdn3d=1.2:1.2:4:4,eq=contrast=1.11:saturation=1.17:gamma=0.97,colorbalance=rs=0.03:gs=0.005:bs=-0.025:rm=0.02:bm=-0.02,curves=all='0/0.02 0.5/0.5 1/0.98',vignette=angle=0.42,unsharp=5:5:0.7:3:3:0"
$vf = if ($SemCor) { "null" } else { $cor }
ffmpeg -v error -y -ss $Inicio.ToString($inv) -to $Fim.ToString($inv) -i "$Video" -vf $vf -c:v libx264 -preset medium -crf 16 -g 30 -keyint_min 30 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k "$pub\input-video.mp4"

# 2. assets (fontes Inter 700/800/900 + GSAP)
Copy-Item "$raiz\assets\fonts\*" "$pub\fonts\" -Force
Copy-Item "$raiz\assets\vendor\gsap.min.js" "$pub\vendor\" -Force

# 3. transcrição com timestamp por palavra (Groq grátis; chave do WhisperFlow)
$k = $env:GROQ_API_KEY; if (-not $k) { $k = [Environment]::GetEnvironmentVariable('GROQ_API_KEY', 'User') }
if (-not $k) { throw "GROQ_API_KEY não encontrada (env ou variável de usuário)." }
ffmpeg -v error -y -i "$Video" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$work\audio.wav"
curl.exe -s https://api.groq.com/openai/v1/audio/transcriptions -H "Authorization: Bearer $k" -F "file=@$work\audio.wav" -F "model=whisper-large-v3-turbo" -F "language=pt" -F "response_format=verbose_json" -F "timestamp_granularities[]=word" -F "timestamp_granularities[]=segment" -o "$work\transcricao.json"
Remove-Item "$work\audio.wav"
if ((Get-Content "$work\transcricao.json" -Raw) -match '"error"') { Get-Content "$work\transcricao.json"; throw "Groq retornou erro." }

# 4. legenda agrupada + folha de contato para posicionar (rosto)
node "$raiz\agrupar.cjs" "$work\transcricao.json" $Inicio.ToString($inv) $Fim.ToString($inv) "$work\legenda.json"
ffmpeg -v error -y -i "$pub\input-video.mp4" -vf "fps=1/4,scale=180:-1,tile=6x2" -frames:v 1 "$work\contato.jpg"
@{ duracao = [math]::Round($dur, 2); inicio = $Inicio; fim = $Fim; origem = $Video } | ConvertTo-Json | Out-File -Encoding utf8 "$work\meta.json"
Write-Host "`nPronto: $work"
Write-Host "Próximo: copiar videos\_modelo\build.cjs para videos\$Nome\build.cjs, editar conteúdo, rodar render.ps1"
