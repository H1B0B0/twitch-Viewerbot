import axios from "axios";

const BASE_URL = "http://localhost:3001/api";
const AUTH_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:3000";

// Fonction pour vérifier si l'utilisateur est authentifié
async function checkAuthStatus() {
  try {
    const response = await axios.get(`${AUTH_URL}/users/profile`, {
      withCredentials: true,
    });
    return !!response.data;
  } catch (error) {
    console.error("Authentication check failed:", error);
    return false;
  }
}

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
  // Vérifier l'authentification avant de démarrer le bot
  const isAuthenticated = await checkAuthStatus();
  if (!isAuthenticated) {
    throw new Error("Authentication required");
  }

  try {
    const formData = new FormData();
    formData.append("channelName", config.channelName);
    formData.append("threads", config.threads.toString());
    formData.append("timeout", config.timeout.toString());
    formData.append("proxyType", config.proxyType);

    if (config.proxyFile) {
      formData.append("proxyFile", config.proxyFile);
    }

    const response = await axios.post(`${BASE_URL}/bot/start`, formData);
    return response.data;
  } catch (error: unknown) {
    if (error instanceof Error) {
      throw new Error(error.message);
    }
    throw new Error("An unknown error occurred");
  }
}

export async function stopBot() {
  const isAuthenticated = await checkAuthStatus();
  if (!isAuthenticated) {
    throw new Error("Authentication required");
  }

  try {
    const response = await axios.post(`${BASE_URL}/bot/stop`);
    return response.data;
  } catch (error: unknown) {
    throw error;
  }
}

export async function getBotStats() {
  const isAuthenticated = await checkAuthStatus();
  if (!isAuthenticated) {
    throw new Error("Authentication required");
  }

  try {
    const response = await axios.get<BotStats>(`${BASE_URL}/bot/stats`);
    return response.data;
  } catch (error: unknown) {
    throw error;
  }
}
