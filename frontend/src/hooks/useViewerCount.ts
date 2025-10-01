import { useState, useEffect, useRef, useCallback } from "react";
import { getViewerCount } from "../app/functions/TwitchAPI";

export function useViewerCount(username: string | undefined) {
  const [viewerCount, setViewerCount] = useState(0);
  const [previousCount, setPreviousCount] = useState(0);
  const [lastUpdate, setLastUpdate] = useState<Date>();
  const [isLoading, setIsLoading] = useState(false);
  const usernameRef = useRef(username);
  const abortControllerRef = useRef<AbortController | null>(null);
  const consecutiveErrorsRef = useRef<number>(0);

  // Update ref when username changes
  useEffect(() => {
    usernameRef.current = username;
  }, [username]);

  const fetchViewerCount = useCallback(async () => {
    if (!username) {
      setViewerCount(0);
      setPreviousCount(0);
      return;
    }

    // Cancel previous request if it exists
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();

    try {
      setIsLoading(true);
      const count = await getViewerCount(username);

      // Reset error counter on success
      consecutiveErrorsRef.current = 0;

      setViewerCount((prevCount) => {
        setPreviousCount(prevCount);
        return count;
      });
      setLastUpdate(new Date());
    } catch (error) {
      consecutiveErrorsRef.current++;

      // Only log error if it's not an abort error and we've had multiple failures
      if (error instanceof Error && error.name !== "AbortError") {
        if (consecutiveErrorsRef.current <= 3) {
          console.error("Error fetching viewer count:", error);
        }
      }
    } finally {
      setIsLoading(false);
    }
  }, [username]);

  useEffect(() => {
    if (!username) return;

    // Initial fetch
    fetchViewerCount();

    // Set up interval for regular updates (reduced to every 5 seconds)
    const interval = setInterval(fetchViewerCount, 5000);

    return () => {
      clearInterval(interval);
      // Cancel any pending requests on cleanup
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [username, fetchViewerCount]);

  return { viewerCount, previousCount, lastUpdate, isLoading };
}
