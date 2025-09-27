import { Button } from "@/components/ui/button"
import { ArrowRight, Database, Coins, Shield } from "lucide-react"

export function HeroSection() {
  return (
    <section className="relative overflow-hidden py-24 lg:py-32">
      <div className="hero-gradient absolute inset-0" />

      {/* Floating background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary/10 rounded-full blur-3xl float-animation" />
        <div
          className="absolute top-3/4 right-1/4 w-96 h-96 bg-accent/10 rounded-full blur-3xl float-animation"
          style={{ animationDelay: "2s" }}
        />
        <div
          className="absolute top-1/2 left-3/4 w-48 h-48 bg-chart-2/10 rounded-full blur-3xl float-animation"
          style={{ animationDelay: "4s" }}
        />
      </div>

      <div className="container relative">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-8 flex justify-center">
            <div className="inline-flex items-center rounded-full border border-border/40 bg-card/50 px-4 py-2 text-sm backdrop-blur">
              <Shield className="mr-2 h-4 w-4 text-primary" />
              Decentralized • AI-Powered • Governance-Driven
            </div>
          </div>

          <h1 className="mb-6 text-4xl font-bold tracking-tight text-balance sm:text-6xl lg:text-7xl">
            Democratize{" "}
            <span className="bg-gradient-to-r from-primary via-accent to-chart-2 bg-clip-text text-transparent">
            high quality datasets
            </span>{" "}
            with AI & Web3
          </h1>

          <p className="mx-auto mb-8 max-w-2xl text-lg text-muted-foreground text-pretty">
            D³ Data DAO is the first decentralized marketplace for high quality datasets. Upload, analyze, tokenize,
            and monetize data with AI quality scoring, permanent IPFS storage, and LUSDC payments.
          </p>

          <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
            <Button size="lg" className="bg-gradient-to-r from-primary to-accent hover:opacity-90 pulse-glow">
              Start Contributing
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            <Button size="lg" variant="outline" className="border-border/40 hover:bg-card/50 bg-transparent">
              Explore Marketplace
            </Button>
          </div>

          <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-3">
            <div className="flex flex-col items-center">
              <div className="mb-4 rounded-full bg-primary/10 p-3">
                <Database className="h-6 w-6 text-primary" />
              </div>
              <h3 className="mb-2 font-semibold">AI-Curated Data</h3>
              <p className="text-sm text-muted-foreground text-center">
                Advanced AI analyzes and scores dataset quality automatically
              </p>
            </div>

            <div className="flex flex-col items-center">
              <div className="mb-4 rounded-full bg-accent/10 p-3">
                <Coins className="h-6 w-6 text-accent" />
              </div>
              <h3 className="mb-2 font-semibold">Dual Token Economy</h3>
              <p className="text-sm text-muted-foreground text-center">
                Earn D3 governance tokens and receive LUSDC payments
              </p>
            </div>

            <div className="flex flex-col items-center">
              <div className="mb-4 rounded-full bg-chart-2/10 p-3">
                <Shield className="h-6 w-6 text-chart-2" />
              </div>
              <h3 className="mb-2 font-semibold">DAO Governance</h3>
              <p className="text-sm text-muted-foreground text-center">
                Community-driven decisions and transparent operations
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
