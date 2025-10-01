const API_BASE_URL = "https://velbots.shop/api/bot";

// Retry logic with exponential backoff
const fetchWithRetry = async (
  url: string,
  options: RequestInit,
  retries = 3,
  backoff = 300
): Promise<Response> => {
  try {
    const response = await fetch(url, options);

    // If response is OK or it's a client error (4xx), return immediately
    if (response.ok || (response.status >= 400 && response.status < 500)) {
      return response;
    }

    // For server errors (5xx), retry
    if (retries > 0) {
      await new Promise((resolve) => setTimeout(resolve, backoff));
      return fetchWithRetry(url, options, retries - 1, backoff * 2);
    }

    return response;
  } catch (error) {
    if (retries > 0) {
      await new Promise((resolve) => setTimeout(resolve, backoff));
      return fetchWithRetry(url, options, retries - 1, backoff * 2);
    }
    throw error;
  }
};

export const startBot = async (config: {
  channelName: string;
  threads: number;
  proxyFile?: File;
  timeout?: number;
  proxyType?: string;
  stabilityMode?: boolean;
}) => {
  const formData = new FormData();
  formData.append("channelName", config.channelName);
  formData.append("threads", config.threads.toString());
  if (config.proxyFile) {
    formData.append("proxyFile", config.proxyFile);
  }
  if (config.timeout) {
    formData.append("timeout", config.timeout.toString());
  }
  if (config.proxyType) {
    formData.append("proxyType", config.proxyType);
  }
  formData.append("stabilityMode", config.stabilityMode ? "true" : "false");

  const response = await fetchWithRetry(
    `${API_BASE_URL}/start`,
    {
      method: "POST",
      body: formData,
      credentials: "include",
    },
    2 // Reduced retries for start operation
  );

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Unknown error" }));
    throw new Error(
      errorData.message || `HTTP error! status: ${response.status}`
    );
  }
  return response.json();
};

export const stopBot = async () => {
  const response = await fetchWithRetry(
    `${API_BASE_URL}/stop`,
    {
      method: "POST",
      credentials: "include",
    },
    2 // Reduced retries for stop operation
  );

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: "Unknown error" }));
    throw new Error(
      errorData.message || `HTTP error! status: ${response.status}`
    );
  }
  return response.json();
};

export const getBotStats = async () => {
  const response = await fetchWithRetry(
    `${API_BASE_URL}/stats`,
    {
      credentials: "include",
    },
    1 // Only 1 retry for stats to avoid delays
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};
