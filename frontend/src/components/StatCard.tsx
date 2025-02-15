import React from "react";
import { Card, CardBody, Progress } from "@heroui/react";

type StatCardProps = {
  title: string;
  value: number;
  total?: number;
  increment?: boolean;
};

export function StatCard({ title, value, total, increment }: StatCardProps) {
  const percentage = total ? (value / total) * 100 : 0;

  return (
    <Card>
      <CardBody className="space-y-3">
        <h3 className="text-sm font-medium">{title}</h3>
        <div className="flex justify-between items-baseline">
          <div className="flex items-baseline">
            <span className="text-2xl font-bold">{value}</span>
            {increment && <span className="ml-1 text-sm opacity-70">/s</span>}
          </div>
          {total && <div className="text-sm opacity-70">of {total}</div>}
        </div>
        {total && <Progress value={percentage} />}
      </CardBody>
    </Card>
  );
}
