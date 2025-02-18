import "./globals.css";
import type { Metadata } from "next";
import "react-toastify/dist/ReactToastify.css";
import ThemeProvider from "../components/ThemeProvider";
import ThemeSwitcher from "../components/ThemeSwitcher";
import Spline from "@splinetool/react-spline";
import ApiHealthProvider from "../components/ApiHealthProvider";
import UpdateProvider from "../components/UpdateProvider";

export const metadata: Metadata = {
  title: "Viewer Bot",
  description: "Viewer bot for streaming platforms",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <div className="fixed inset-0 w-full h-full overflow-hidden">
            <div className="absolute inset-0">
              <Spline
                scene="https://prod.spline.design/LE-Lh2ApbhLmRH9i/scene.splinecode"
                className="blur-xl absolute"
              />
            </div>
          </div>
          <main className="w-full relative z-10">
            <ApiHealthProvider>{children}</ApiHealthProvider>
          </main>
          <ThemeSwitcher />
          <UpdateProvider />
        </ThemeProvider>
      </body>
    </html>
  );
}
