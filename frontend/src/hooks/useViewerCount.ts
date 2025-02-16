import { useState, useEffect } from "react";
import { getViewerCount } from "../app/functions/TwitchAPI";

export function useViewerCount(username: string | undefined) {
  const [viewerCount, setViewerCount] = useState(0);
  const [previousCount, setPreviousCount] = useState(0);
  const [lastUpdate, setLastUpdate] = useState<Date>();

  useEffect(() => {
    if (!username) return;

    const fetchViewerCount = async () => {
      const count = await getViewerCount(username);
      setPreviousCount(viewerCount);
      setViewerCount(count);
      setLastUpdate(new Date());
      console.log(
        `📊 Viewer count updated at ${new Date().toLocaleTimeString()}: ${count} viewers`
      );
    };

    console.log(`🔄 Starting viewer count polling for ${username}`);
    fetchViewerCount();
    const interval = setInterval(fetchViewerCount, 2000);

    return () => {
      console.log(`⏹️ Stopping viewer count polling for ${username}`);
      clearInterval(interval);
    };
  }, [username, viewerCount]);

  return { viewerCount, previousCount, lastUpdate };
}
