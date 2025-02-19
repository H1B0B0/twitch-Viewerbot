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
  Tooltip,
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
    threads: 0,
    channelName: "",
    gameName: "",
    messagesPerMinute: 1,
    enableChat: false,
    proxyType: "http",
    timeout: 10000,
  });
  const { viewerCount: currentViewers } = useViewerCount(
    config?.channelName || profile?.user?.TwitchUsername
  );

  const [isLoading, setIsLoading] = useState(false);
  const [proxyFile, setProxyFile] = useState<File | null>(null);
  const [stats, setStats] = useState({
    totalProxies: 0,
    aliveProxies: 0,
    activeThreads: 0,
    request_count: 0,
    viewers: currentViewers, // Utilisé maintenant la valeur en direct
    targetViewers: 0,
  });

  const [channelNameModified, setChannelNameModified] = useState(false);

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
            request_count: stats.request_count,
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
    // If profile loads and channel name is empty, set it ONLY ONCE
    if (
      profile?.user?.TwitchUsername &&
      !config.channelName &&
      !channelNameModified
    ) {
      setConfig((prev) => ({
        ...prev,
        channelName: profile.user.TwitchUsername,
      }));
    }
  }, [profile, channelNameModified, config.channelName]);

  // Modifier la vérification initiale de l'état du bot
  useEffect(() => {
    const checkBotStatus = async () => {
      try {
        const stats = await getBotStats();
        // Si le bot a des threads actifs, il est en cours d'exécution
        if (stats.active_threads > 0 || stats.is_running) {
          setIsLoading(true);
          // Mettre à jour les stats
          setStats((prevStats) => ({
            ...prevStats,
            activeThreads: stats.active_threads,
            totalProxies: stats.total_proxies,
            aliveProxies: stats.alive_proxies,
            request_count: stats.request_count,
          }));

          // Restaurer la configuration du bot si elle existe
          if (stats.config) {
            const { threads, timeout, proxy_type } = stats.config;
            const parsedTimeout = parseInt(timeout, 10);
            setConfig((prevConfig) => ({
              ...prevConfig,
              threads: threads ?? prevConfig.threads,
              timeout: Number.isNaN(parsedTimeout) ? 10000 : parsedTimeout,
              proxyType: proxy_type ?? prevConfig.proxyType,
              channelName: stats.channel_name || prevConfig.channelName,
            }));
          }
        }
      } catch (error) {
        console.error("Failed to check bot status:", error);
      }
    };

    // Vérifier l'état du bot au chargement de la page
    checkBotStatus();
  }, []); // Exécuter une seule fois au montage

  const handleStart = async () => {
    if (!config.channelName) {
      toast.error("Channel name is required");
      return;
    } else if (config.threads === 0) {
      toast.error("Threads count must be greater than 0");
      return;
    }
    try {
      setIsLoading(true);
      await startBot({
        channelName: config.channelName,
        threads: config.threads,
        proxyFile: proxyFile || undefined,
        timeout: config.timeout,
        proxyType: config.proxyType,
      });
      toast.success(
        "Bot started successfully!🚀 It may take a while before the viewers appear on the stream."
      );
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

  const handleChannelNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setChannelNameModified(true);
    setConfig((prev) => ({
      ...prev,
      channelName: e.target.value,
    }));
  };

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header with Logout */}
        <Card className="relative text-center mb-8 p-8 rounded-2xl">
          <Button
            as="a"
            href="https://www.patreon.com/c/HIBO"
            target="_blank"
            rel="noopener noreferrer"
            variant="bordered"
            className="absolute left-4 top-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white border-none"
            startContent={<span className="text-lg">❤️</span>}
          >
            Support Me
          </Button>
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
        </Card>

        {/* Monitoring Section - Moved to top */}
        <Card>
          <CardHeader>
            <h2 className="text-2xl font-semibold">Live Monitoring</h2>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <ViewerStatCard value={currentViewers} />
              <StatCard
                title="Active Threads"
                value={stats.activeThreads}
                total={config.threads}
              />
              <StatCard
                title="Proxies"
                value={stats.totalProxies}
                total={stats.totalProxies}
              />
              <StatCard title="Requests" value={stats.request_count} />
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
                onChange={handleChannelNameChange}
              />
              <div className="flex items-center space-x-2">
                <Input
                  type="number"
                  label="Number of Threads"
                  value={config.threads === 0 ? "" : config.threads.toString()}
                  min={0}
                  max={1000}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      threads:
                        e.target.value === ""
                          ? 0
                          : Math.min(1000, parseInt(e.target.value) || 0),
                    })
                  }
                />
                <Tooltip
                  content={
                    <div className="max-w-xs p-2">
                      <p>
                        Threads determine how many simultaneous connections the
                        bot will make.
                      </p>
                      <p className="mt-1">
                        More threads = more viewers, but requires more resources
                        and stable proxies.
                      </p>
                      <p className="mt-1">
                        Recommended: Start with 100-200 threads.
                      </p>
                    </div>
                  }
                >
                  <div className="flex items-center justify-center w-6 h-6 rounded-full bg-default-100 text-default-500 cursor-help">
                    ?
                  </div>
                </Tooltip>
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
              <div className="space-y-2">
                <label className="text-sm font-medium block">
                  Proxy List (Optional)
                </label>
                <div className="relative">
                  <Button
                    as="label"
                    className="w-full h-[40px] flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg cursor-pointer transition-all duration-300 group"
                  >
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                      />
                    </svg>
                    <span className="text-sm">
                      {proxyFile
                        ? proxyFile.name
                        : "Choose proxy file (Optional)"}
                    </span>
                    <Input
                      type="file"
                      accept=".txt"
                      onChange={(e) =>
                        setProxyFile(e.target.files?.[0] || null)
                      }
                      className="hidden"
                    />
                  </Button>
                </div>
                <p className="text-xs text-gray-500">
                  Upload a .txt file with proxies or let the bot scrape them
                  automatically (format: ip:port). Ensure the proxies are
                  reliable for better performance.
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
                <Input
                  label="Game Name"
                  value={config.gameName}
                  onChange={(e) =>
                    setConfig({ ...config, gameName: e.target.value })
                  }
                  isDisabled={true}
                />
                <span className="absolute right-0 top-0 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs px-2 py-1 rounded">
                  Coming Soon Premium Feature
                </span>
              </div>
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
