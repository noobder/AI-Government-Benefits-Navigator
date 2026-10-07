import { useCallback, useEffect, useRef, useState } from "react";
import { FilesetResolver, HandLandmarker, type NormalizedLandmark } from "@mediapipe/tasks-vision";

/**
 * EXPERIMENTAL hand-sign input.
 *
 * Recognizes exactly two static hand poses from the browser camera —
 * thumbs up ("yes") and an open palm ("no") — using MediaPipe's hand
 * landmark model, entirely on-device (the video frame never leaves the
 * browser). This is a small-vocabulary gesture recognizer, not sign
 * language: it cannot understand ISL/ASL grammar or arbitrary signs. It
 * exists as a fast, low-literacy-friendly way to answer a yes/no question
 * without typing or speaking, and is always optional (gated behind the
 * "Experimental hand-sign input" setting) with plain tapping as the
 * fallback.
 */
export type GestureId = "thumbs_up" | "open_palm" | "none";

const WASM_BASE = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm";
const MODEL_URL =
  "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task";

let landmarkerPromise: Promise<HandLandmarker> | null = null;

function getLandmarker(): Promise<HandLandmarker> {
  if (!landmarkerPromise) {
    landmarkerPromise = FilesetResolver.forVisionTasks(WASM_BASE).then((fileset) =>
      HandLandmarker.createFromOptions(fileset, {
        baseOptions: { modelAssetPath: MODEL_URL, delegate: "GPU" },
        runningMode: "VIDEO",
        numHands: 1,
      })
    );
  }
  return landmarkerPromise;
}

// Landmark indices per MediaPipe Hands topology.
const WRIST = 0;
const THUMB_MCP = 2;
const THUMB_TIP = 4;
const FINGER_TIP_PIP: [number, number][] = [
  [8, 6], // index
  [12, 10], // middle
  [16, 14], // ring
  [20, 18], // pinky
];

function classifyGesture(lm: NormalizedLandmark[]): GestureId {
  const fingerExtended = FINGER_TIP_PIP.map(([tip, pip]) => lm[tip].y < lm[pip].y);
  const extendedCount = fingerExtended.filter(Boolean).length;
  const curledCount = 4 - extendedCount;

  const thumbPointingUp = lm[THUMB_TIP].y < lm[WRIST].y - 0.05 && lm[THUMB_TIP].y < lm[THUMB_MCP].y;

  if (extendedCount === 4) return "open_palm";
  if (thumbPointingUp && curledCount >= 3) return "thumbs_up";
  return "none";
}

export function useHandGesture() {
  const videoElRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const rafRef = useRef<number | null>(null);
  const [gesture, setGesture] = useState<GestureId>("none");
  const [isLoading, setIsLoading] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const stop = useCallback(() => {
    if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    rafRef.current = null;
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    videoElRef.current = null;
    setIsActive(false);
    setGesture("none");
  }, []);

  const start = useCallback(async (videoEl: HTMLVideoElement) => {
    setError(null);
    setIsLoading(true);
    videoElRef.current = videoEl;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
      streamRef.current = stream;
      videoEl.srcObject = stream;
      await videoEl.play();

      const landmarker = await getLandmarker();
      setIsLoading(false);
      setIsActive(true);

      const loop = () => {
        if (!videoElRef.current) return;
        const result = landmarker.detectForVideo(videoElRef.current, performance.now());
        setGesture(result.landmarks && result.landmarks.length > 0 ? classifyGesture(result.landmarks[0]) : "none");
        rafRef.current = requestAnimationFrame(loop);
      };
      rafRef.current = requestAnimationFrame(loop);
    } catch (e) {
      setIsLoading(false);
      setError(e instanceof Error ? e.message : "Camera error");
    }
  }, []);

  useEffect(() => stop, [stop]);

  return { start, stop, gesture, isLoading, isActive, error };
}
