#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
export FONTCONFIG_FILE="$PWD/fonts.conf"
Q="-loglevel error -y"
W=840; H=560
cover() { ffmpeg $Q -i "$1" -vf "scale=${W}:${H}:force_original_aspect_ratio=increase:flags=lanczos,crop=${W}:${H}${2}" "$3"; }
cover duo.png "" k_duo.png
cover fold1.jpg ":0:(ih-${H})*0.45" k_fold.png
cover cand2.jpg "" k_ipod.png
cover cand4.jpg "" k_iphone.png
cover cand6.jpg "" k_watch.png
ffmpeg $Q -f lavfi -i "color=c=0x0F1418:s=${W}x${H}:d=1" -vf "subtitles=card-quebra.ass" -frames:v 1 k_quebra.png
X=120; Y=70; C0=23.58; C1=25.62
ffmpeg $Q -i t.mp4 -i k_duo.png -i k_fold.png -i k_ipod.png -i k_iphone.png -i k_watch.png -i k_quebra.png \
  -stream_loop -1 -i music.mp3 -filter_complex "
[0:v]trim=0:$C0,setpts=PTS-STARTPTS[v1];[0:v]trim=$C1,setpts=PTS-STARTPTS[v2];
[0:a]atrim=0:$C0,asetpts=PTS-STARTPTS,afade=t=out:st=23.53:d=0.05[a1];[0:a]atrim=$C1,asetpts=PTS-STARTPTS,afade=t=in:d=0.04[a2];
[v1][a1][v2][a2]concat=n=2:v=1:a=1[vb][voz];
[vb][1:v]overlay=$X:$Y:enable='between(t,0.40,3.20)'[o1];
[o1][2:v]overlay=$X:$Y:enable='between(t,6.30,8.60)'[o2];
[o2][3:v]overlay=$X:$Y:enable='between(t,10.30,11.25)'[o3];
[o3][4:v]overlay=$X:$Y:enable='between(t,11.85,12.90)'[o4];
[o4][5:v]overlay=$X:$Y:enable='between(t,13.40,14.30)'[o5];
[o5][6:v]overlay=$X:$Y:enable='between(t,14.80,17.85)'[vout];
[voz]asplit[vk][vsc];
[7:a]atrim=0:29.8,volume=0.16,afade=t=in:d=0.5,afade=t=out:st=28.3:d=1.5[mus];
[mus][vsc]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=500[musd];
[vk][musd]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.9[aout]
" -map "[vout]" -map "[aout]" -r 30 -c:v libx264 -crf 18 -preset fast -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -movflags +faststart ed2.mp4
echo done
