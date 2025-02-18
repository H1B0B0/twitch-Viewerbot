"use client";
import { useState, useEffect } from "react";
import axios from "axios";

const GITHUB_API =
  "https://api.github.com/repos/H1B0B0/twitch-Viewerbot/releases/latest";
const CURRENT_VERSION = "3.0.2";

interface GithubRelease {
  tag_name: string;
  html_url: string;
  body: string;
  assets: {
    browser_download_url: string;
    name: string;
  }[];
}

export function useUpdateChecker() {
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [latestVersion, setLatestVersion] = useState<GithubRelease | null>(
    null
  );

  useEffect(() => {
    const checkForUpdates = async () => {
      try {
        const response = await axios.get<GithubRelease>(GITHUB_API);
        const latest = response.data;

        // Comparer les versions (sans le 'v' initial)
        const isNewer = latest.tag_name.replace("v", "") > CURRENT_VERSION;

        if (isNewer) {
          setUpdateAvailable(true);
          setLatestVersion(latest);
        }
      } catch (error) {
        console.error("Failed to check for updates:", error);
      }
    };

    // Vérifier au démarrage et toutes les 24 heures
    checkForUpdates();
    const interval = setInterval(checkForUpdates, 24 * 60 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  return { updateAvailable, latestVersion };
}
