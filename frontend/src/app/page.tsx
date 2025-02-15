"use client";
import { useState } from "react";
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
import { useGetProfile } from "./functions/UserAPI";

export default function ViewerBotInterface() {
  const { data: profile } = useGetProfile();
  const [isLoading, setIsLoading] = useState(false);
  const [stats] = useState({
    totalProxies: 0,
    aliveProxies: 0,
    activeThreads: 0,
    requests: 0,
    viewers: 0,
    targetViewers: 0,
  });
  const [config, setConfig] = useState({
    threads: 1,
    channelName: "",
    gameName: "",
    messagesPerMinute: 1,
    enableChat: false,
    proxyType: "http",
    timeout: 1000,
  });

  const handleStart = async () => {
    setIsLoading(true);
    try {
      // API call logic here
      toast.success("Bot started successfully!");
    } catch {
      toast.error("Failed to start bot");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center mb-8 bg-background/60 backdrop-blur-3xl p-8 rounded-2xl border border-default-200">
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
              <StatCard
                title="Current Viewers"
                value={stats.viewers}
                total={stats.targetViewers}
              />
              <StatCard
                title="Active Threads"
                value={stats.activeThreads}
                total={config.threads}
              />
              <StatCard
                title="Proxies"
                value={stats.aliveProxies}
                total={stats.totalProxies}
              />
              <StatCard title="Requests" value={stats.requests} increment />
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
                  defaultValue={[1000]}
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
              color="primary"
              size="lg"
              fullWidth
              isLoading={isLoading}
              onPress={handleStart}
            >
              {isLoading ? "Running..." : "Start Bot"}
            </Button>
          </CardBody>
        </Card>
      </div>
      <ToastContainer />
    </div>
  );
}
