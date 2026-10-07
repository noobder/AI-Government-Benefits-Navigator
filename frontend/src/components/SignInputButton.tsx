import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useHandGesture } from "../hooks/useHandGesture";
import { Button, IconButton } from "./Button";

/**
 * Opt-in camera button next to a yes/no field. Only rendered when the user
 * has explicitly enabled "Experimental hand-sign input" in Settings — see
 * useHandGesture.ts for exactly what it can and can't recognize.
 */
export default function SignInputButton({ onYesNo }: { onYesNo: (value: boolean) => void }) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const { start, stop, gesture, isLoading, error } = useHandGesture();

  useEffect(() => {
    if (open && videoRef.current) {
      start(videoRef.current);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const close = () => {
    stop();
    setOpen(false);
  };

  const confirm = () => {
    if (gesture === "thumbs_up") onYesNo(true);
    else if (gesture === "open_palm") onYesNo(false);
    close();
  };

  return (
    <>
      <IconButton
        type="button"
        onClick={() => setOpen(true)}
        aria-label={t("accessibility.signInputCameraTitle")}
        title={t("accessibility.signInputCameraTitle")}
      >
        <span aria-hidden>🖐️</span>
      </IconButton>

      {open && (
        <div
          className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 p-4"
          role="dialog"
          aria-modal="true"
          aria-label={t("accessibility.signInputCameraTitle")}
        >
          <div className="w-full max-w-sm rounded-2xl bg-[var(--surface)] p-5 shadow-xl">
            <h3 className="text-base font-bold text-[var(--ink)]">{t("accessibility.signInputCameraTitle")}</h3>

            <div className="relative mt-3 aspect-video overflow-hidden rounded-xl bg-black">
              {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
              <video ref={videoRef} className="h-full w-full -scale-x-100 object-cover" muted playsInline />
            </div>

            {isLoading && (
              <p className="mt-2 text-xs text-[var(--ink-muted)]">{t("accessibility.signInputLoadingModel")}</p>
            )}
            {error && <p className="mt-2 text-xs text-[var(--danger)]">{t("accessibility.signInputCameraError")}</p>}

            <ul className="mt-3 space-y-1 text-sm text-[var(--ink-muted)]">
              <li>{t("accessibility.signInputThumbsUp")}</li>
              <li>{t("accessibility.signInputOpenPalm")}</li>
            </ul>

            <p className="mt-2 text-sm font-semibold text-[var(--ink)]" role="status" aria-live="polite">
              {gesture === "none"
                ? t("accessibility.signInputNone")
                : t("accessibility.signInputDetected", { gesture: t(`accessibility.gesture.${gesture}`) })}
            </p>

            <div className="mt-4 flex gap-2">
              <Button type="button" onClick={confirm} disabled={gesture === "none"} fullWidth>
                {t("accessibility.signInputUse")}
              </Button>
              <Button type="button" variant="secondary" onClick={close} fullWidth>
                {t("accessibility.signInputCancel")}
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
