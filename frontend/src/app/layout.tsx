import "./globals.css";
import "react-toastify/dist/ReactToastify.css";
import ThemeProvider from "./components/ThemeProvider";
import ThemeSwitcher from "./components/ThemeSwitcher";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <main className="w-full">
            <div>{children}</div>
          </main>
          <ThemeSwitcher />
        </ThemeProvider>
      </body>
    </html>
  );
}
