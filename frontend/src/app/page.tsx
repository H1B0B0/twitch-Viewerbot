"use client";
import { useState, useEffect } from "react";
import {
  Card,
  CardHeader,
  CardBody,
  Input,
  Button,
  Slider,
  Checkbox,
  ButtonGroup,
} from "@heroui/react";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { StatCard } from "../components/StatCard";
import { useGetProfile, logout } from "./functions/UserAPI";
import { useRouter } from "next/navigation";
import { useViewerCount } from "../hooks/useViewerCount";
import { ViewerStatCard } from "../components/ViewerStatCard";
import { startBot, stopBot, getBotStats } from "./functions/BotAPI";

export default function ViewerBotInterface() {
  const router = useRouter();
  const { data: profile } = useGetProfile();
  const [config, setConfig] = useState({
    threads: 1,
    channelName: "",
    gameName: "",
    messagesPerMinute: 1,
    enableChat: false,
    proxyType: "http",
    timeout: 1000,
  });
  const { viewerCount: currentViewers, previousCount } = useViewerCount(
    // Use channelName from config if it doesn't match the profile's TwitchUsername
    config?.channelName || profile?.user?.TwitchUsername
  );

  console.log("currentViewers", currentViewers);
  console.log("profile", profile);

  const [isLoading, setIsLoading] = useState(false);
  const [proxyFile, setProxyFile] = useState<File | null>(null);
  const [stats, setStats] = useState({
    totalProxies: 0,
    aliveProxies: 0,
    activeThreads: 0,
    requests: 0,
    viewers: currentViewers, // Utilisé maintenant la valeur en direct
    targetViewers: 0,
    total_requests: 0,
  });

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    if (isLoading) {
      intervalId = setInterval(async () => {
        try {
          const stats = await getBotStats();
          setStats((prevStats) => ({
            ...prevStats,
            activeThreads: stats.active_threads,
            totalProxies: stats.total_proxies,
            aliveProxies: stats.alive_proxies,
            total_requests: stats.total_requests,
          }));

          // If active threads drops to 0, consider the bot stopped
          if (stats.active_threads === 0 && isLoading) {
            setIsLoading(false);
          }
        } catch (error) {
          console.error("Failed to fetch stats:", error);
        }
      }, 1000);
    }

    // Cleanup interval on unmount or when isLoading changes
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [isLoading]);

  useEffect(() => {
    // If profile loads and channel name is empty, set it to TwitchUsername
    if (profile?.user?.TwitchUsername && !config.channelName) {
      setConfig((prev) => ({
        ...prev,
        channelName: profile.user.TwitchUsername,
      }));
    }
  }, [profile]);

  const handleStart = async () => {
    try {
      setIsLoading(true); // Set loading before starting
      await startBot({
        channelName: config.channelName,
        threads: config.threads,
        proxyFile: proxyFile || undefined,
        timeout: config.timeout,
        proxyType: config.proxyType,
      });
      toast.success("Bot started successfully!");
    } catch (err) {
      toast.error(
        `Failed to start bot: ${
          err instanceof Error ? err.message : "Unknown error"
        }`
      );
      setIsLoading(false); // Reset loading on error
    }
  };

  const handleStop = async () => {
    try {
      await stopBot();
      toast.success("Bot stopped successfully!");
      setIsLoading(false);
      // Reset stats when stopping
      setStats((prevStats) => ({
        ...prevStats,
        activeThreads: 0,
        requests: 0,
      }));
    } catch (err) {
      toast.error("Failed to stop bot");
      console.error("Failed to stop bot:", err);
      // Keep isLoading true if stop fails
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      toast.success("Logged out successfully!");
      router.push("/login");
    } catch {
      toast.error("Failed to logout");
    }
  };

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header with Logout */}
        <div className="relative text-center mb-8 bg-background/60 backdrop-blur-3xl p-8 rounded-2xl border border-default-200">
          {profile && (
            <Button
              variant="bordered"
              onPress={handleLogout}
              className="absolute right-4 top-4"
              color="danger"
            >
              Logout
            </Button>
          )}
          <h1 className="text-5xl font-black mb-3 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            Twitch Viewer Bot
          </h1>
          <p className="text-xl font-medium">
            {profile
              ? `Welcome back, ${profile.user.username}`
              : "Monitor and control your viewer bot"}
          </p>
        </div>

        {/* Monitoring Section - Moved to top */}
        <Card>
          <CardHeader>
            <h2 className="text-2xl font-semibold">Live Monitoring</h2>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <ViewerStatCard
                value={currentViewers}
                previousValue={previousCount}
              />
              <StatCard
                title="Active Threads"
                value={stats.activeThreads}
                total={config.threads}
              />
              <StatCard
                title="Alive Proxies"
                value={stats.aliveProxies}
                total={stats.totalProxies}
              />
              <StatCard title="Requests" value={stats.total_requests} />
            </div>
          </CardBody>
        </Card>

        {/* Control Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Basic Configuration */}
          <Card>
            <CardHeader>
              <h2 className="text-2xl font-semibold">Basic Configuration</h2>
            </CardHeader>
            <CardBody className="space-y-6">
              <Input
                label="Channel Name"
                value={config.channelName}
                placeholder={
                  profile?.user?.TwitchUsername || "Enter channel name"
                }
                onChange={(e) =>
                  setConfig({ ...config, channelName: e.target.value })
                }
              />
              <Input
                label="Game Name"
                value={config.gameName}
                onChange={(e) =>
                  setConfig({ ...config, gameName: e.target.value })
                }
              />
              <Input
                type="number"
                label="Number of Threads"
                value={config.threads.toString()}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    threads: parseInt(e.target.value),
                  })
                }
              />
              <div className="space-y-2">
                <label className="text-sm font-medium block">
                  Proxy List (Optional)
                </label>
                <Input
                  type="file"
                  accept=".txt"
                  onChange={(e) => setProxyFile(e.target.files?.[0] || null)}
                />
                <p className="text-xs text-gray-500">
                  Upload a .txt file with proxies or let the bot scrape them
                  automatically
                </p>
              </div>
            </CardBody>
          </Card>

          {/* Advanced Settings */}
          <Card>
            <CardHeader>
              <h2 className="text-2xl font-semibold">Advanced Settings</h2>
            </CardHeader>
            <CardBody className="space-y-6">
              <div className="relative">
                <Slider
                  value={[1]}
                  defaultValue={[1]}
                  maxValue={60}
                  isDisabled={true}
                  label="Messages Per Minute"
                  getValue={(value) => `${value} messages`}
                  step={1}
                />
                <span className="absolute right-0 top-0 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs px-2 py-1 rounded">
                  Coming Soon Premium Feature
                </span>
              </div>

              <div>
                <Slider
                  value={[config.timeout]}
                  defaultValue={[10000]}
                  maxValue={10000}
                  onChange={(value) =>
                    setConfig({
                      ...config,
                      timeout: Number(Array.isArray(value) ? value[0] : value),
                    })
                  }
                  getValue={(timeout) => `${timeout}ms`}
                  label="Request Timeout"
                  step={100}
                />
              </div>

              <div className="relative">
                <Checkbox checked={false} isDisabled={true}>
                  <span className="text-gray-400">Enable Chat Messages</span>
                </Checkbox>
                <span className="absolute right-0 top-0 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs px-2 py-1 rounded">
                  Coming Soon Premium Feature
                </span>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">
                  Proxy Type
                </label>
                <ButtonGroup>
                  {["http", "socks4", "socks5", "all"].map((type) => (
                    <Button
                      key={type}
                      variant={config.proxyType === type ? "solid" : "bordered"}
                      onPress={() => setConfig({ ...config, proxyType: type })}
                    >
                      {type}
                    </Button>
                  ))}
                </ButtonGroup>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Action Button */}
        <Card>
          <CardBody className="py-6">
            <Button
              variant="solid"
              color={isLoading ? "danger" : "primary"}
              size="lg"
              fullWidth
              onPress={isLoading ? handleStop : handleStart}
            >
              {isLoading ? "Stop Bot" : "Start Bot"}
            </Button>
          </CardBody>
        </Card>
      </div>
      <ToastContainer />
    </div>
  );
}
