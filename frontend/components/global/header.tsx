import Link from "next/link"
import { Button } from "@/components/ui/button"

export function Header() {
  return (
    <header className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center space-x-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-lg">D³</span>
          </div>
          <span className="font-bold text-xl">Data DAO</span>
        </Link>

        <nav className="hidden md:flex items-center space-x-6">
          <Link href="/marketplace" className="text-muted-foreground hover:text-foreground transition-colors">
            Marketplace
          </Link>
          <Link href="/upload" className="text-muted-foreground hover:text-foreground transition-colors">
            Upload
          </Link>
          <Link href="/tokenomics" className="text-muted-foreground hover:text-foreground transition-colors">
            Tokenomics
          </Link>
          <Link href="/governance" className="text-muted-foreground hover:text-foreground transition-colors">
            Governance
          </Link>
        </nav>

        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm">
            Connect Wallet
          </Button>
          <Button size="sm" className="bg-gradient-to-r from-primary to-accent hover:opacity-90">
            Get Started
          </Button>
        </div>
      </div>
    </header>
  )
}
