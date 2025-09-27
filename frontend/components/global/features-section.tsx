import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Brain, Coins, Shield, Upload, Search, Vote, Zap, Globe, Lock } from "lucide-react"

const features = [
  {
    icon: Brain,
    title: "AI Quality Scoring",
    description:
      "Advanced machine learning algorithms automatically analyze and score dataset quality, completeness, and relevance.",
    badge: "AI-Powered",
    color: "text-primary",
  },
  {
    icon: Upload,
    title: "Seamless Upload",
    description: "Simple drag-and-drop interface for JSON, CSV, and XML files with automatic metadata extraction.",
    badge: "User-Friendly",
    color: "text-accent",
  },
  {
    icon: Coins,
    title: "LSDC Payments",
    description: "Stable, transparent payments using LSDC stablecoin with automatic revenue distribution.",
    badge: "Stable Payments",
    color: "text-chart-2",
  },
  {
    icon: Shield,
    title: "IPFS Storage",
    description: "Permanent, decentralized storage via Lighthouse ensuring data availability and immutability.",
    badge: "Decentralized",
    color: "text-chart-3",
  },
  {
    icon: Search,
    title: "Smart Discovery",
    description: "AI-powered search and filtering helps users find exactly the datasets they need.",
    badge: "Intelligent",
    color: "text-chart-4",
  },
  {
    icon: Vote,
    title: "DAO Governance",
    description: "Token holders vote on platform decisions, fee structures, and feature development.",
    badge: "Democratic",
    color: "text-chart-5",
  },
  {
    icon: Zap,
    title: "Instant Access",
    description: "NFT-based licensing provides immediate access to purchased datasets with proof of ownership.",
    badge: "Fast",
    color: "text-primary",
  },
  {
    icon: Globe,
    title: "Open Marketplace",
    description: "Global access to high quality datasets with transparent pricing and contributor rewards.",
    badge: "Global",
    color: "text-accent",
  },
  {
    icon: Lock,
    title: "Secure & Audited",
    description: "Smart contracts audited for security with multi-signature governance controls.",
    badge: "Secure",
    color: "text-chart-2",
  },
]

export function FeaturesSection() {
  return (
    <section className="py-24 lg:py-32">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
            Built for the Future of{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Data Democracy
            </span>
          </h2>
          <p className="text-lg text-muted-foreground text-pretty">
            Combining cutting-edge AI, blockchain technology, and democratic governance to create the world's first
            decentralized dataset marketplace.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="group relative overflow-hidden border-border/40 bg-card/50 backdrop-blur hover:bg-card/80 transition-all duration-300"
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className={`rounded-lg bg-background/50 p-2 ${feature.color}`}>
                    <feature.icon className="h-5 w-5" />
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    {feature.badge}
                  </Badge>
                </div>

                <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">{feature.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
