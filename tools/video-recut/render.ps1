# video-recut / render — gera a composição, faz lint + prévias ou render final.
# uso:
#   .\tools\video-recut\render.ps1 -Nome "2026-09-meu-video" -Previa -Em "3.9,8.9,13.6"   # só frames (segundos, rápido)
#   .\tools\video-recut\render.ps1 -Nome "2026-09-meu-video"                              # render final (~8 min / 43s)
param(
  [Parameter(Mandatory)] [string]$Nome,
  [switch]$Previa,
  [switch]$NaoEsperar,   # agente: dispara e acompanha pelo log (evita o limite de 10 min por comando)
  [string]$Em = "",
  [string]$Destino = "$env:USERPROFILE\Downloads"
)
$ErrorActionPreference = 'Stop'
$raiz = $PSScriptRoot
$work = Join-Path $raiz "work\$Nome"
$build = Join-Path $raiz "videos\$Nome\build.cjs"
if (-not (Test-Path "$work\public\input-video.mp4")) { throw "Rode prep.ps1 antes (falta $work\public\input-video.mp4)." }

node $build "$work\public\index.html"
Push-Location $work
try {
  npx hyperframes lint public 2>&1 | Select-String "✗|◇" -Context 0, 1
  if ($Previa) {
    Remove-Item -Recurse -Force "public\snapshots" -ErrorAction SilentlyContinue
    npx hyperframes snapshot public --at $Em 2>&1 | Select-String "saved"
    Write-Host "Prévia: $work\public\snapshots\contact-sheet.jpg"
    return
  }
  # render destacado: comandos de agente morrem em 10 min; o render leva ~8 min nesta máquina (1 worker, low-memory)
  $log = "$work\render.log"; $out = "$work\output.mp4"
  Remove-Item $out, $log -ErrorAction SilentlyContinue
  $p = Start-Process cmd.exe -ArgumentList "/c", "npx hyperframes render public --skill=talking-head-recut --quality delivery -o output.mp4 --fps 30 > render.log 2>&1" -WorkingDirectory $work -WindowStyle Hidden -PassThru
  Write-Host "Render iniciado (PID $($p.Id)). Log: $log"
  if ($NaoEsperar) { Write-Host "Saída ficará em $out (copie para o destino ao terminar)"; return }
  $p.WaitForExit()
  if (-not (Test-Path $out)) { Get-Content $log -Tail 30; throw "Render falhou." }
  $final = Join-Path $Destino "$Nome.mp4"
  Copy-Item $out $final -Force
  Get-Content $log -Tail 5 | Select-String "rendered in"
  Write-Host "Final: $final"
} finally { Pop-Location }
