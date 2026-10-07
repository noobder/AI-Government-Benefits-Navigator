import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useVoice } from "./useVoice";

/** A fake SpeechRecognition the tests drive manually, standing in for the
 * real browser API so we can assert on useVoice's own logic without a real
 * microphone. This is what actually caught the original bug: interim
 * results must flow into onResult live, not just once at the very end. */
class FakeSpeechRecognition {
  lang = "";
  interimResults = false;
  continuous = false;
  maxAlternatives = 1;
  onstart: (() => void) | null = null;
  onerror: ((e: any) => void) | null = null;
  onresult: ((e: any) => void) | null = null;
  onend: (() => void) | null = null;

  // Test helper: simulate the browser reporting a specific recognition error.
  emitError(reason: string) {
    this.onerror?.({ error: reason });
  }

  start() {
    this.onstart?.();
  }
  stop() {
    this.onend?.();
  }

  // Test helper: simulate the browser delivering one result event.
  emitResult(transcript: string, isFinal: boolean) {
    this.onresult?.({
      resultIndex: 0,
      results: [{ 0: { transcript }, isFinal, length: 1 }],
    });
  }

  emitEnd() {
    this.onend?.();
  }
}

describe("useVoice", () => {
  let lastInstance: FakeSpeechRecognition;

  beforeEach(() => {
    (window as any).SpeechRecognition = vi.fn(() => {
      lastInstance = new FakeSpeechRecognition();
      return lastInstance;
    });
  });

  afterEach(() => {
    delete (window as any).SpeechRecognition;
  });

  it("reports interim results live via onResult, not only at the end", () => {
    const { result } = renderHook(() => useVoice("en"));
    const onResult = vi.fn();

    act(() => {
      result.current.listen(onResult);
    });
    expect(result.current.isSupported).toBe(true);

    act(() => {
      lastInstance.emitResult("hello", false);
    });
    expect(onResult).toHaveBeenCalledWith("hello");

    act(() => {
      lastInstance.emitResult("hello world", false);
    });
    expect(onResult).toHaveBeenLastCalledWith("hello world");
  });

  it("reports a plain-language error when recognition ends with nothing heard", () => {
    const { result } = renderHook(() => useVoice("en"));

    act(() => {
      result.current.listen(vi.fn());
    });
    act(() => {
      lastInstance.emitEnd();
    });

    expect(result.current.error).toMatch(/didn't catch/i);
  });

  it("does not report the no-result error when a final transcript was captured", () => {
    const { result } = renderHook(() => useVoice("en"));
    const onResult = vi.fn();

    act(() => {
      result.current.listen(onResult);
    });
    act(() => {
      lastInstance.emitResult("done", true);
    });
    act(() => {
      lastInstance.emitEnd();
    });

    expect(result.current.error).toBeNull();
  });

  it("keeps the specific onerror message instead of letting onend overwrite it with the generic one", () => {
    const { result } = renderHook(() => useVoice("en"));

    act(() => {
      result.current.listen(vi.fn());
    });
    act(() => {
      lastInstance.emitError("not-allowed");
    });
    act(() => {
      lastInstance.emitEnd();
    });

    expect(result.current.error).toMatch(/blocked/i);
    expect(result.current.error).not.toMatch(/didn't catch/i);
  });

  it("does not surface an error when recognition is stopped by the user (aborted)", () => {
    const { result } = renderHook(() => useVoice("en"));

    act(() => {
      result.current.listen(vi.fn());
    });
    act(() => {
      lastInstance.emitError("aborted");
    });
    act(() => {
      lastInstance.emitEnd();
    });

    expect(result.current.error).toBeNull();
  });

  it("maps the app language to the correct speech recognition locale", () => {
    const { result } = renderHook(() => useVoice("hi"));
    act(() => {
      result.current.listen(vi.fn());
    });
    expect(lastInstance.lang).toBe("hi-IN");
  });
});
