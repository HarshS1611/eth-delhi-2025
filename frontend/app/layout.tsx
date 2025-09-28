"use client";


import { WagmiProvider } from "wagmi";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect } from "react";
import { appKit, wagmiConfig } from "@/lib/wallet";
import "./globals.css";


const qc = new QueryClient();

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`container mx-auto antialiased`}>
        <WagmiProvider config={wagmiConfig}>
          <QueryClientProvider client={qc}>{children}</QueryClientProvider>
        </WagmiProvider>
      </body>
    </html>
  );
}