"use client";
import { useUpdateChecker } from "../hooks/useUpdateChecker";
import UpdateNotification from "./UpdateNotification";

export default function UpdateProvider() {
  const { updateAvailable, latestVersion } = useUpdateChecker();

  if (updateAvailable && latestVersion) {
    return (
      <UpdateNotification
        isOpen={updateAvailable}
        onClose={() => {}}
        version={latestVersion.tag_name}
        releaseNotes={latestVersion.body}
        downloadUrl={latestVersion.html_url}
      />
    );
  }

  return null;
}
