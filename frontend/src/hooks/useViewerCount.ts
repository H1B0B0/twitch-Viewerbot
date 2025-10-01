import { useState, useEffect, useRef } from "react";
import { getViewerCount } from "../app/functions/TwitchAPI";

export function useViewerCount(username: string | undefined) {
  const [viewerCount, setViewerCount] = useState(0);
  const [previousCount, setPreviousCount] = useState(0);
  const [lastUpdate, setLastUpdate] = useState<Date>();
  const usernameRef = useRef(username);

  // Update ref when username changes
  useEffect(() => {
    usernameRef.current = username;
  }, [username]);

  useEffect(() => {
    if (!username) return;

    const fetchViewerCount = async () => {
      try {
        const count = await getViewerCount(username);
        setViewerCount((prevCount) => {
          setPreviousCount(prevCount);
          return count;
        });
        setLastUpdate(new Date());
      } catch (error) {
        console.error("Error fetching viewer count:", error);
      }
    };

    // Initial fetch
    fetchViewerCount();

    // Set up interval for regular updates
    const interval = setInterval(fetchViewerCount, 3000); // Increased to 3 seconds to reduce API load

    return () => {
      clearInterval(interval);
    };
  }, [username]); // Only depend on username, not viewerCount

  return { viewerCount, previousCount, lastUpdate };
}
