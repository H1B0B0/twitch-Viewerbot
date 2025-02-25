import React from "react";
import { Button } from "@heroui/react";
import { FaPlayCircle, FaStopCircle } from "react-icons/fa";
import { cn } from "../utils/cn";
import { useStore } from "../store/store";

export function ControlButtons() {
  const { botStatus, startBot, stopBot } = useStore((state) => ({
    botStatus: state.botStatus,
    startBot: state.startBot,
    stopBot: state.stopBot,
  }));

  console.log("Statut actuel du bot:", botStatus);

  // Vérifier si les boutons doivent être désactivés
  const isStartDisabled =
    botStatus === "RUNNING" ||
    botStatus === "STOPPING" ||
    botStatus === "STARTING";
  const isStopDisabled =
    botStatus === "STOPPED" ||
    botStatus === "STOPPING" ||
    botStatus === "STARTING";

  return (
    <div className="flex gap-3">
      <Button
        color="success"
        className={cn(
          "transition-all",
          isStartDisabled ? "opacity-50 cursor-not-allowed" : "hover:scale-105"
        )}
        startContent={<FaPlayCircle className="text-xl" />}
        onClick={startBot}
        disabled={isStartDisabled}
      >
        {botStatus === "STARTING" ? "Starting..." : "Start Bot"}
      </Button>
      <Button
        color="danger"
        className={cn(
          "transition-all",
          isStopDisabled ? "opacity-50 cursor-not-allowed" : "hover:scale-105"
        )}
        startContent={<FaStopCircle className="text-xl" />}
        onClick={stopBot}
        disabled={isStopDisabled}
      >
        {botStatus === "STOPPING" ? "Stopping..." : "Stop Bot"}
      </Button>
    </div>
  );
}
