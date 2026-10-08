from pathlib import Path
import hashlib
import av

root = Path(__file__).parent
for name in ("COFFEE-IA-amazon-muse-final-v9.mp4", "COFFEE-IA-amazon-muse-final-v10.mp4"):
    path = root / name
    with av.open(str(path)) as container:
        v = container.streams.video[0]
        a = container.streams.audio[0]
        frame_count = 0
        last_time = 0.0
        for frame in container.decode(v):
            frame_count += 1
            last_time = float(frame.time)
        print(name, "size", path.stat().st_size,
              "video", v.codec_context.name, v.width, v.height, frame_count,
              "last frame", round(last_time, 3),
              "audio", a.codec_context.name,
              "duration", round(float(container.duration / av.time_base), 3))
    with av.open(str(path)) as container:
        stream = container.streams.audio[0]
        digest = hashlib.sha256()
        packets = 0
        for packet in container.demux(stream):
            if packet.size:
                digest.update(bytes(packet))
                packets += 1
        print("audio packets", packets, "sha256", digest.hexdigest())
    with av.open(str(path)) as container:
        stream = container.streams.audio[0]
        count = sum(frame.samples for frame in container.decode(stream))
        print("decoded audio", count, "samples", round(count / stream.rate, 3), "s")
