import { Card, CardBody, Progress, Badge } from "@heroui/react";
import { motion } from "framer-motion";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface MetricData {
  label: string;
  value: number;
  color: string;
  unit: string;
  history: number[];
  maxValue: number;
}

interface SystemMetricsProps {
  metrics: {
    cpu: MetricData;
    memory: MetricData;
    network_up: MetricData;
    network_down: MetricData;
  };
}

export const SystemMetrics = ({ metrics }: SystemMetricsProps) => {
  const renderBasicMetric = (metric: MetricData, index: number) => (
    <motion.div
      key={metric.label}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.3 }}
    >
      <Card className="border-none glass-card" shadow="sm">
        <CardBody className="space-y-4 p-6 flex flex-col justify-between h-full relative overflow-hidden">
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
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium">{metric.label}</span>
            <motion.div
              key={metric.value}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              <Badge>
                {metric.value.toFixed(1)}
                {metric.unit}
              </Badge>
            </motion.div>
          </div>
          <Progress
            value={(metric.value / metric.maxValue) * 100}
            color={
              (metric.value / metric.maxValue) * 100 < 30
                ? "success"
                : (metric.value / metric.maxValue) * 100 < 70
                ? "warning"
                : "danger"
            }
            className="mb-3"
          />
        </CardBody>
      </Card>
    </motion.div>
  );

  const renderNetworkMetric = () => (
    <Card className="border-none glass-card" shadow="sm">
      <CardBody className="space-y-4 p-6 flex flex-col justify-between h-full relative overflow-hidden">
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
        <span className="text-sm font-medium block mb-3">Network Traffic</span>
        <div className="grid grid-cols-2 gap-4">
          <Card className="border-none glass-card" shadow="sm">
            <CardBody className="p-3">
              <div className="absolute inset-0 pointer-events-none opacity-5">
                <svg
                  width="100%"
                  height="100%"
                  xmlns="http://www.w3.org/2000/svg"
                >
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
              <div className="flex justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-purple-400 text-lg">↑</span>
                  <span className="text-xs font-medium">Upload</span>
                </div>
                <Badge variant="flat" className="text-xs">
                  {metrics.network_up.value.toFixed(1)}
                  {metrics.network_up.unit}
                </Badge>
              </div>
            </CardBody>
          </Card>

          <Card className="border-none glass-card" shadow="sm">
            <CardBody className="p-3">
              <div className="absolute inset-0 pointer-events-none opacity-5">
                <svg
                  width="100%"
                  height="100%"
                  xmlns="http://www.w3.org/2000/svg"
                >
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
              <div className="flex justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-red-400 text-lg">↓</span>
                  <span className="text-xs font-medium">Download</span>
                </div>
                <Badge color="danger" variant="flat" className="text-xs">
                  {metrics.network_down.value.toFixed(1)}
                  {metrics.network_down.unit}
                </Badge>
              </div>
            </CardBody>
          </Card>
        </div>
      </CardBody>
    </Card>
  );

  return (
    <Card className="w-full border-none bg-background/90 backdrop-blur-xl shadow-xl hover:shadow-2xl transition-all duration-300">
      <CardBody>
        <h3 className="text-2xl font-semibold mb-4 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
          System Metrics
        </h3>
        <div className="space-y-4">
          {renderBasicMetric(metrics.cpu, 0)}
          {renderBasicMetric(metrics.memory, 1)}
          {renderNetworkMetric()}
        </div>
      </CardBody>
    </Card>
  );
};
