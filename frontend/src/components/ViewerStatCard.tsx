import React, { useEffect, useState, useMemo } from "react";
import { Card, CardBody } from "@heroui/react";
import { motion } from "framer-motion";

type ViewerStatCardProps = {
  value: number;
  previousValue?: number;
};

type EmberParticleProps = {
  trend: "up" | "down";
  delay?: number;
};

function EmberParticle({ trend, delay = 0 }: EmberParticleProps) {
  const [randomSeed, setRandomSeed] = useState(Math.random());

  const randomValues = useMemo(
    () => ({
      initialX: Math.random() * 80 - 40,
      randomX1: Math.random() * 40 - 20,
      randomX2: Math.random() * 80 - 40,
      randomRotate: Math.random() * 360,
      randomSize: Math.random() * 3 + 2, // taille entre 2 et 5px
      randomBorderRadius: Math.random() * 10 + 2, // forme moins arrondie
    }),
    [] // Removed randomSeed from dependencies as it's not needed
  );

  return (
    <motion.div
      key={randomSeed} // En changeant le key, on force le remount du composant pour un nouveau cycle
      initial={{
        y: 0,
        x: randomValues.initialX,
        opacity: 1,
        scale: 1,
        rotate: 0,
      }}
      animate={{
        y: trend === "up" ? [0, -40, -120] : [0, 40, 80],
        x:
          trend === "up"
            ? [
                randomValues.initialX,
                randomValues.initialX + randomValues.randomX1,
                randomValues.initialX + randomValues.randomX2,
              ]
            : [
                randomValues.initialX,
                randomValues.initialX,
                randomValues.initialX,
              ],
        opacity: [1, 0.7, 0],
        scale: [1, 1.3, 0],
        rotate: [0, randomValues.randomRotate, 0],
      }}
      transition={{
        duration: 2 + Math.random(),
        delay: delay,
        ease: "easeOut",
      }}
      onAnimationComplete={() => setRandomSeed(Math.random())}
      style={{
        width: randomValues.randomSize,
        height: randomValues.randomSize,
        borderRadius: randomValues.randomBorderRadius,
      }}
      className={`absolute ${
        trend === "up"
          ? "bg-gradient-to-t from-orange-600 to-yellow-400 shadow-lg shadow-orange-500/50"
          : "bg-gradient-to-b from-blue-500 to-cyan-300"
      }`}
    />
  );
}

export function ViewerStatCard({ value, previousValue }: ViewerStatCardProps) {
  const [trend, setTrend] = useState<"up" | "down" | null>(null);

  useEffect(() => {
    if (previousValue !== undefined && value !== previousValue) {
      setTrend(value > previousValue ? "up" : "down");
    }
  }, [value, previousValue]);

  const renderParticles = () => {
    return Array.from({ length: 20 }).map((_, i) => (
      <EmberParticle key={`${trend}-${i}`} trend={trend!} delay={i * 0.1} />
    ));
  };

  return (
    <Card>
      <CardBody className="space-y-3 relative overflow-hidden">
        <h3 className="text-sm font-medium flex items-center gap-2">
          Current Viewers
          {trend && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className={`text-xl ${
                trend === "up" ? "text-orange-500" : "text-blue-500"
              }`}
            >
              {trend === "up" ? "🔥" : "❄️"}
            </motion.div>
          )}
        </h3>
        <div className="flex justify-center items-center relative min-h-[80px]">
          <motion.div
            key={value}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{
              scale: 1,
              opacity: 1,
              transition: { type: "spring", stiffness: 300, damping: 20 },
            }}
            className={`text-4xl font-bold relative z-10 ${
              trend === "up"
                ? "text-orange-500 drop-shadow-[0_0_15px_rgba(255,165,0,0.7)]"
                : trend === "down"
                ? "text-blue-500 drop-shadow-[0_0_15px_rgba(0,191,255,0.7)]"
                : ""
            }`}
          >
            {value === 0 ? (
              <span className="text-2xl text-default-400">Offline</span>
            ) : (
              value.toLocaleString()
            )}
          </motion.div>
          {trend && (
            <div className="absolute inset-0 flex items-center justify-center">
              {renderParticles()}
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
}
