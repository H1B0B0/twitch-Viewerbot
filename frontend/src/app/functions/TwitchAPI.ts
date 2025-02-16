export async function getViewerCount(username: string): Promise<number> {
  if (!username) {
    console.log("No username provided for viewer count fetch");
    return 0;
  }

  try {
    console.log(`📺 Fetching viewer count for channel: ${username}`);
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
      variables: { login: username },
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

    if (data?.data?.user?.stream) {
      console.log(`✅ Channel ${username}: ${viewersCount} viewers on stream`);
    } else {
      console.log(
        `❌ Channel ${username} is offline or no stream data available`
      );
    }

    console.log("Response data:", data);
    return viewersCount;
  } catch (error) {
    console.error(`🔴 Error fetching viewer count for ${username}:`, error);
    return 0;
  }
}
