import React, { useEffect, useState, useRef } from "react";
import { Card, CardBody } from "@heroui/react";
import { FaArrowUp, FaArrowDown, FaMinus } from "react-icons/fa";
import { useViewerCache } from "../hooks/useViewerCache";
import { cn } from "../utils/cn";

type ViewerStatCardProps = {
  value: number;
};

export function ViewerStatCard({ value }: ViewerStatCardProps) {
  const { previousValue, percentageChange } = useViewerCache(value);
  const difference = value - previousValue;
  const [showGlow, setShowGlow] = useState(false);
  const [addedValue, setAddedValue] = useState<number>(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const [isIncreasing, setIsIncreasing] = useState<boolean>(false);

  useEffect(() => {
    if (difference > 0) {
      setShowGlow(true);
      setIsIncreasing(true);
      setAddedValue(difference);

      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }

      timerRef.current = setTimeout(() => {
        setShowGlow(false);
        setIsIncreasing(false);
        setAddedValue(0);
      }, 2000);

      return () => {
        if (timerRef.current) {
          clearTimeout(timerRef.current);
        }
      };
    }
  }, [value, difference]);

  const getTrendColor = () => {
    if (difference > 0) return "text-green-500";
    if (difference < 0) return "text-red-500";
    return "text-gray-500";
  };

  const getTrendIcon = () => {
    if (difference > 0) return <FaArrowUp className="w-4 h-4" />;
    if (difference < 0) return <FaArrowDown className="w-4 h-4" />;
    return <FaMinus className="w-4 h-4" />;
  };

  return (
    <div className="relative h-full">
      {showGlow && (
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/30 via-pink-500/30 to-purple-500/30 rounded-lg blur-xl animate-pulse" />
      )}
      <Card
        className={cn(
          "relative h-full border-none bg-background/90 backdrop-blur-xl transition-all duration-300",
          showGlow && "ring-2 ring-purple-500/50"
        )}
        shadow="sm"
      >
        <CardBody className="space-y-4 p-6 flex flex-col justify-between h-full">
          {/* Subtle background pattern */}
          <div className="absolute inset-0 pointer-events-none opacity-5">
            <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <pattern
                  id="microGrid"
                  width="10"
                  height="10"
                  patternUnits="userSpaceOnUse"
                >
                  <path
                    d="M 10 0 L 0 0 0 10"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="0.5"
                  />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#microGrid)" />
            </svg>
          </div>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-default-600 uppercase tracking-wider">
              Live Viewers
            </h3>
            {showGlow && (
              <span className="flex h-2 w-2">
                <span className="animate-ping absolute h-2 w-2 rounded-full bg-purple-400 opacity-75" />
                <span className="rounded-full h-2 w-2 bg-purple-500" />
              </span>
            )}
          </div>
          <div className="space-y-2">
            <div className="flex items-baseline gap-2 relative">
              <span
                className={cn(
                  "text-4xl font-black bg-clip-text text-transparent transition-all duration-1000",
                  showGlow
                    ? "bg-gradient-to-r from-purple-400 via-pink-500 to-purple-600 animate-gradient-x"
                    : "bg-gradient-to-r from-purple-600 to-pink-600"
                )}
              >
                {value.toLocaleString()}
              </span>
              {isIncreasing && addedValue > 0 && (
                <span className="absolute -right-12 top-0 text-xs font-medium text-purple-600 animate-fade-up">
                  +{addedValue.toLocaleString()}
                </span>
              )}
            </div>
            <div className={`flex items-center gap-1 ${getTrendColor()}`}>
              {getTrendIcon()}
              <span className="text-sm font-medium">
                {Math.abs(percentageChange).toFixed(1)}%
              </span>
              <span className="text-xs text-default-500 ml-1">
                since last update
              </span>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
