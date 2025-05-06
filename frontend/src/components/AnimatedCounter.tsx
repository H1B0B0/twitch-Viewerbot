import React, { useEffect, useState } from "react";
import { usePreviousValue } from "../hooks/usePreviousValue";

interface AnimatedCounterProps {
  value: number;
  duration?: number;
}

export const AnimatedCounter: React.FC<AnimatedCounterProps> = ({
  value,
  duration = 500,
}) => {
  const [displayValue, setDisplayValue] = useState(value);
  const prevValue = usePreviousValue(value);

  useEffect(() => {
    // If this is the first render or values are the same, just set the display value
    if (prevValue === undefined || prevValue === value) {
      setDisplayValue(value);
      return;
    }

    // Only animate if we have a meaningful change
    if (Math.abs(prevValue - value) > 0) {
      let startTimestamp: number;
      const startValue = displayValue;

      const step = (timestamp: number) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);

        setDisplayValue(
          Math.round(startValue + progress * (value - startValue))
        );

        if (progress < 1) {
          window.requestAnimationFrame(step);
        }
      };

      window.requestAnimationFrame(step);
    }
  }, [value, prevValue, duration, displayValue]);

  return <>{displayValue.toLocaleString()}</>;
};
