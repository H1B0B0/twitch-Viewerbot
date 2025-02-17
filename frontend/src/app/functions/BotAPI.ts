import axios from "axios";

const BASE_URL = "http://localhost:3001/api";

export interface BotStats {
  request_count: number;
  active_threads: number;
  total_proxies: number;
  alive_proxies: number;
  is_running: boolean;
  channel_name: string | null;
  config?: {
    threads: number;
    timeout: number;
    proxy_type: string;
  };
}

export interface BotConfig {
  channelName: string;
  threads: number;
  proxyFile?: File;
  timeout: number;
  proxyType: string;
}

export async function startBot(config: BotConfig) {
  try {
    const formData = new FormData();
    formData.append("channelName", config.channelName);
    formData.append("threads", config.threads.toString());
    formData.append("timeout", config.timeout.toString());
    formData.append("proxyType", config.proxyType);

    if (config.proxyFile) {
      formData.append("proxyFile", config.proxyFile);
    }

    const response = await axios.post(`${BASE_URL}/bot/start`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error starting bot:", error);
    throw error;
  }
}

export async function stopBot() {
  try {
    const response = await axios.post(`${BASE_URL}/bot/stop`);
    return response.data;
  } catch (error) {
    console.error("Error stopping bot:", error);
    throw error;
  }
}

export async function getBotStats() {
  try {
    const response = await axios.get<BotStats>(`${BASE_URL}/bot/stats`);
    console.log("Bot stats:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error fetching bot stats:", error);
    throw error;
  }
}
