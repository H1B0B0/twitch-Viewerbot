export function extractChannelName(input: string): string {
  if (!input) return "";

  if (input.includes("twitch.tv/")) {
    const parts = input.split("twitch.tv/");
    const channel = parts[1].split(/[/?]/)[0];
    return channel.toLowerCase();
  }
  return input.toLowerCase();
}

export async function getViewerCount(username: string): Promise<number> {
  if (!username) {
    console.log("No username provided for viewer count fetch");
    return 0;
  }

  const channelName = extractChannelName(username);

  try {
    const graphqlQuery = {
      query: `
        query GetViewerCount($login: String!) {
          user(login: $login) {
            stream {
              viewersCount
            }
          }
        }
      `,
      variables: { login: channelName },
    };

    const response = await fetch("https://gql.twitch.tv/gql", {
      method: "POST",
      headers: {
        "Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(graphqlQuery),
    });

    const data = await response.json();
    const viewersCount = data?.data?.user?.stream?.viewersCount || 0;

    return viewersCount;
  } catch (error) {
    console.error(`🔴 Error fetching viewer count for ${username}:`, error);
    return 0;
  }
}
