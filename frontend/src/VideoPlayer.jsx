import { useEffect, useRef, useState } from "react";
import Hls from "hls.js";

export default function VideoPlayer({ src }) {
  const videoRef = useRef(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    if (Hls.isSupported()) {
      const hls = new Hls({ liveSyncDurationCount: 2 });
      hls.loadSource(src);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, () => setError(""));
      hls.on(Hls.Events.ERROR, (_, data) => {
        if (data.fatal) {
          setError("Stream nahi mila. MediaMTX aur ffmpeg chal rahe hain?");
          setTimeout(() => hls.loadSource(src), 5000);   // retry
        }
      });
      return () => hls.destroy();
    }
    if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = src;
    }
  }, [src]);

  return (
    <div className="video-box">
      <video ref={videoRef} autoPlay muted playsInline controls />
      {error && <div className="video-error">{error}</div>}
    </div>
  );
}
