"use client"

import { createAppKit } from "@reown/appkit"
import { sepolia } from "@reown/appkit/networks"
import { WagmiAdapter } from "@reown/appkit-adapter-wagmi"
import { http } from "viem"

const projectId = process.env.NEXT_PUBLIC_REOWN_PROJECT_ID!
if (!projectId) throw new Error("Missing NEXT_PUBLIC_REOWN_PROJECT_ID")

const rpcUrl = process.env.NEXT_PUBLIC_RPC_URL

export const networks = [sepolia]

export const wagmiAdapter = new WagmiAdapter({
  projectId,
  networks,
  transports: rpcUrl ? { [sepolia.id]: http(rpcUrl) } : undefined,
})
export const wagmiConfig = wagmiAdapter.wagmiConfig

export const appKit = createAppKit({
  adapters: [wagmiAdapter],
  projectId,
  networks,
  metadata: {
    name: "Data Marketplace",
    description: "Decentralized dataset marketplace",
    url: "https://your.app",
    icons: ["https://your.app/icon.png"],
  },
  features: { analytics: true },
})

export function openConnect() { appKit.open() }
export function logout() { appKit.disconnect() }
