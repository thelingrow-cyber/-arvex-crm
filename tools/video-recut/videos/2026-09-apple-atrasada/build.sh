#!/usr/bin/env bash
# Edição "Apple chegou atrasada" — inserções acima da cabeça, corte de 23,58–25,62, trilha
set -e
cd "$(dirname "$0")"
export FONTCONFIG_FILE="$PWD/fonts.conf"
Q="-loglevel error -y"

# --- cards de imagem: fundo branco 660x440, imagem encaixada com margem
card() { ffmpeg $Q -i "$1" -vf "$2scale=620:400:force_original_aspect_ratio=decrease,pad=660:440:(ow-iw)/2:(oh-ih)/2:color=white" "$3"; }
card duo.png "" c_duo.png
card fold1.jpg "" c_fold.png
card ipod.jpg "" c_ipod.png
card iphone1.jpg "crop=iw:ih*0.8:0:ih*0.1," c_iphone.png
card watch.jpg "crop=iw:ih*0.5:0:0," c_watch.png

# --- cards de texto: fundo carvão
node cards.cjs
ffmpeg $Q -f lavfi -i "color=c=0x0F1418:s=660x440:d=1" -vf "subtitles=card-quebra.ass" -frames:v 1 c_quebra.png
ffmpeg $Q -f lavfi -i "color=c=0x0F1418:s=660x440:d=1" -vf "subtitles=card-imposto.ass" -frames:v 1 c_imposto.png

# --- montagem
X=210; Y=150
C0=23.58; C1=25.62
ffmpeg $Q -i t.mp4 -i c_duo.png -i c_fold.png -i c_ipod.png -i c_iphone.png -i c_watch.png -i c_quebra.png -i c_imposto.png \
  -stream_loop -1 -i music.mp3 -filter_complex "
[0:v]trim=0:$C0,setpts=PTS-STARTPTS[v1];[0:v]trim=$C1,setpts=PTS-STARTPTS[v2];
[0:a]atrim=0:$C0,asetpts=PTS-STARTPTS,afade=t=out:st=23.53:d=0.05[a1];[0:a]atrim=$C1,asetpts=PTS-STARTPTS,afade=t=in:d=0.04[a2];
[v1][a1][v2][a2]concat=n=2:v=1:a=1[vb][voz];
[vb][1:v]overlay=$X:$Y:enable='between(t,0.40,3.20)'[o1];
[o1][2:v]overlay=$X:$Y:enable='between(t,6.30,8.60)'[o2];
[o2][3:v]overlay=$X:$Y:enable='between(t,10.30,11.25)'[o3];
[o3][4:v]overlay=$X:$Y:enable='between(t,11.85,12.90)'[o4];
[o4][5:v]overlay=$X:$Y:enable='between(t,13.40,14.30)'[o5];
[o5][6:v]overlay=$X:$Y:enable='between(t,14.80,17.85)'[o6];
[o6][7:v]overlay=$X:$Y:enable='between(t,22.15,23.58)'[vout];
[voz]asplit[vk][vsc];
[8:a]atrim=0:29.8,volume=0.30,afade=t=in:d=0.5,afade=t=out:st=28.3:d=1.5[mus];
[mus][vsc]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=500[musd];
[vk][musd]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.9[aout]
" -map "[vout]" -map "[aout]" -r 30 -c:v libx264 -crf 18 -preset fast -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -movflags +faststart ed.mp4
echo done
