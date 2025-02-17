import "./globals.css";
import "react-toastify/dist/ReactToastify.css";
import ThemeProvider from "../components/ThemeProvider";
import ThemeSwitcher from "../components/ThemeSwitcher";
import Spline from "@splinetool/react-spline";
import ApiHealthProvider from "../components/ApiHealthProvider";
import UpdateProvider from "../components/UpdateProvider";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <div className="fixed inset-0 -z-10">
            <Spline
              scene="https://prod.spline.design/LE-Lh2ApbhLmRH9i/scene.splinecode"
              className="blur-xl"
            />
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
