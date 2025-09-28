"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { appKit } from "@/lib/wallet"
import { useAccount } from "wagmi"

export function Header() {
  const { isConnected, address } = useAccount()
  const [mounted, setMounted] = useState(false)
  useEffect(() => setMounted(true), [])

  const openConnect = () => appKit.open()

  return (
    <header className="border-b bg-background">
      <div className="container flex h-14 items-center justify-between">
        <nav className="flex items-center gap-6">
          <Link href="/" className="font-semibold">D³ Data</Link>
          <Link href="/marketplace" className="text-sm text-muted-foreground hover:text-foreground">Marketplace</Link>
          <Link href="/upload" className="text-sm text-muted-foreground hover:text-foreground">Upload</Link>
          <Link href="/governance" className="text-sm text-muted-foreground hover:text-foreground">Governance</Link>
          <Link href="/tokenomics" className="text-sm text-muted-foreground hover:text-foreground">Tokenomics</Link>
        </nav>

        {/* Render connect button only after mount to avoid SSR mismatch */}
        <div>
          { isConnected ? (
            <Button onClick={openConnect} size="sm" className="bg-primary text-primary-foreground">
               {address}
            </Button>
          ) : (
            <Button onClick={openConnect} size="sm" className="bg-primary text-primary-foreground">
              Connect Wallet
            </Button>
          )}
        </div>
      </div>
    </header>
  )
}
