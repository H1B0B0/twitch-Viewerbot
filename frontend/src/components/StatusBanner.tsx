import { Card, CardBody, Progress } from "@heroui/react";
import { motion, AnimatePresence } from "framer-motion";

interface StatusBannerProps {
  status: {
    state: string;
    message: string;
    proxy_loading_progress: number;
    startup_progress: number;
  };
}

export const StatusBanner = ({ status }: StatusBannerProps) => {
  const getTextColor = () => {
    switch (status.state) {
      case "error":
        return "text-red-600";
      case "running":
        return "text-green-600";
      case "loading_proxies":
        return "text-blue-600";
      case "starting":
        return "text-blue-600";
      case "stopped":
        return "text-gray-600";
      case "stopping":
        return "text-orange-600";
      default:
        return "text-gray-600";
    }
  };

  const getBackgroundColor = () => {
    switch (status.state) {
      case "error":
        return "from-red-500/10 to-red-600/5";
      case "running":
        return "from-green-500/10 to-green-600/5";
      case "loading_proxies":
      case "starting":
        return "from-blue-500/10 to-blue-600/5";
      case "stopping":
        return "from-orange-500/10 to-orange-600/5";
      default:
        return "from-gray-500/10 to-gray-600/5";
    }
  };

  const getStatusIndicator = () => {
    const baseClasses = "relative flex h-3 w-3 mr-2";
    const pulseClasses =
      "animate-ping absolute inline-flex h-full w-full rounded-full opacity-75";
    const dotClasses = "relative inline-flex rounded-full h-3 w-3";

    switch (status.state) {
      case "error":
        return (
          <motion.span
            className={baseClasses}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
          >
            <span className={`${pulseClasses} bg-red-400`}></span>
            <span className={`${dotClasses} bg-red-500`}></span>
          </motion.span>
        );
      case "running":
        return (
          <motion.span
            className={baseClasses}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
          >
            <span className={`${pulseClasses} bg-green-400`}></span>
            <span className={`${dotClasses} bg-green-500`}></span>
          </motion.span>
        );
      case "loading_proxies":
      case "starting":
        return (
          <motion.span
            className={baseClasses}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
          >
            <span className={`${pulseClasses} bg-blue-400`}></span>
            <span className={`${dotClasses} bg-blue-500`}></span>
          </motion.span>
        );
      case "stopped":
        return (
          <span className={baseClasses}>
            <span className={`${dotClasses} bg-gray-400`}></span>
          </span>
        );
      case "stopping":
        return (
          <motion.span
            className={baseClasses}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
          >
            <span className={`${pulseClasses} bg-orange-400`}></span>
            <span className={`${dotClasses} bg-orange-500`}></span>
          </motion.span>
        );
      default:
        return null;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="w-full border-none glass-card shadow-xl hover:shadow-2xl transition-all duration-500">
        <CardBody className="p-4 relative overflow-hidden">
          {/* Animated background gradient based on status */}
          <motion.div
            className={`absolute inset-0 bg-gradient-to-r ${getBackgroundColor()} ${
              status.state === "running" ? "animate-pulse-subtle" : ""
            }`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          />

          <div className="space-y-3 relative z-10">
            <div className="flex items-center justify-between">
              <motion.div
                className="flex items-center"
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.1 }}
              >
                {getStatusIndicator()}
                <span
                  className={`${getTextColor()} font-medium uppercase tracking-wider text-sm`}
                >
                  {status.state.replace(/_/g, " ")}
                </span>
                <motion.span
                  className="ml-3 text-gray-700 dark:text-gray-300"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  {status.message}
                </motion.span>
              </motion.div>
            </div>

            <AnimatePresence>
              {(status.state === "loading_proxies" ||
                status.state === "starting") && (
                <motion.div
                  className="space-y-3 pt-2"
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  {status.proxy_loading_progress > 0 && (
                    <motion.div
                      className="animate-fade-in"
                      initial={{ x: -20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: 0.1 }}
                    >
                      <div className="flex justify-between text-sm mb-1.5">
                        <span className="font-medium">Loading Proxies</span>
                        <span className="font-medium">
                          {status.proxy_loading_progress}%
                        </span>
                      </div>
                      <Progress
                        value={status.proxy_loading_progress}
                        color="primary"
                        className="h-2"
                      />
                    </motion.div>
                  )}
                  {status.startup_progress > 0 && (
                    <motion.div
                      className="animate-fade-in"
                      initial={{ x: -20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: 0.2 }}
                    >
                      <div className="flex justify-between text-sm mb-1.5">
                        <span className="font-medium">Starting Bot</span>
                        <span className="font-medium">
                          {status.startup_progress}%
                        </span>
                      </div>
                      <Progress
                        value={status.startup_progress}
                        color="success"
                        className="h-2"
                      />
                    </motion.div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </CardBody>
      </Card>
    </motion.div>
  );
};
