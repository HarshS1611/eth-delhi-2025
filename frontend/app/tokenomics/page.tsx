"use client"
import { Header } from "@/components/global/header"
import { TokenomicsOverview } from "@/components/tokenomics/tokenomics-overview"
import { StakingInterface } from "@/components/tokenomics/staking-interface"
import { RewardsTracker } from "@/components/tokenomics/rewards-tracker"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function TokenomicsPage() {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="container py-8">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Tokenomics</span>{" "}
            Dashboard
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Stake your D3 tokens to earn LSDC rewards, gain voting power in governance, and participate in the
            decentralized data economy.
          </p>
        </div>

        <Tabs defaultValue="overview" className="space-y-8">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="staking">Staking</TabsTrigger>
            <TabsTrigger value="rewards">Rewards</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <TokenomicsOverview />
          </TabsContent>

          <TabsContent value="staking" className="space-y-6">
            <StakingInterface />
          </TabsContent>

          <TabsContent value="rewards" className="space-y-6">
            <RewardsTracker />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
