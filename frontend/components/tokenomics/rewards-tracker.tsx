"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { Coins, TrendingUp, Calendar, Gift, ArrowUpRight, Download } from "lucide-react"

interface RewardEntry {
  id: string
  date: string
  type: "staking" | "contribution" | "governance" | "referral"
  amount: number
  status: "pending" | "claimed" | "available"
  description: string
}

const mockRewards: RewardEntry[] = [
  {
    id: "1",
    date: "2024-01-20",
    type: "staking",
    amount: 12.45,
    status: "available",
    description: "Daily staking rewards for Gold tier",
  },
  {
    id: "2",
    date: "2024-01-19",
    type: "contribution",
    amount: 25.0,
    status: "claimed",
    description: "Dataset upload bonus - UK Parliament Voting Records",
  },
  {
    id: "3",
    date: "2024-01-18",
    type: "governance",
    amount: 8.75,
    status: "available",
    description: "Governance participation reward - Proposal #42",
  },
  {
    id: "4",
    date: "2024-01-17",
    type: "staking",
    amount: 12.45,
    status: "claimed",
    description: "Daily staking rewards for Gold tier",
  },
  {
    id: "5",
    date: "2024-01-16",
    type: "referral",
    amount: 15.0,
    status: "pending",
    description: "Referral bonus - New contributor joined",
  },
]

const rewardTypeConfig = {
  staking: { label: "Staking", color: "bg-primary/10 text-primary", icon: Coins },
  contribution: { label: "Contribution", color: "bg-accent/10 text-primary", icon: TrendingUp },
  governance: { label: "Governance", color: "bg-chart-2/10 text-chart-2", icon: Gift },
  referral: { label: "Referral", color: "bg-chart-3/10 text-chart-3", icon: ArrowUpRight },
}

export function RewardsTracker() {
  const { toast } = useToast()
  const [isClaiming, setIsClaiming] = useState(false)

  const availableRewards = mockRewards.filter((reward) => reward.status === "available")
  const totalAvailable = availableRewards.reduce((sum, reward) => sum + reward.amount, 0)
  const totalClaimed = mockRewards
    .filter((reward) => reward.status === "claimed")
    .reduce((sum, reward) => sum + reward.amount, 0)
  const totalPending = mockRewards
    .filter((reward) => reward.status === "pending")
    .reduce((sum, reward) => sum + reward.amount, 0)

  const handleClaimAll = async () => {
    if (availableRewards.length === 0) return

    setIsClaiming(true)

    // Simulate claiming transaction
    await new Promise((resolve) => setTimeout(resolve, 2000))

    setIsClaiming(false)

    toast({
      title: "Rewards claimed!",
      description: `Successfully claimed ${totalAvailable.toFixed(2)} LSDC to your wallet.`,
    })
  }

  const handleClaimSingle = async (rewardId: string) => {
    const reward = availableRewards.find((r) => r.id === rewardId)
    if (!reward) return

    toast({
      title: "Reward claimed!",
      description: `Successfully claimed ${reward.amount.toFixed(2)} LSDC.`,
    })
  }

  return (
    <div className="space-y-6">
      {/* Rewards Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-green-500/20 bg-green-500/5">
          <CardContent className="p-6 text-center">
            <div className="inline-flex rounded-full bg-green-500/10 p-3 mb-4">
              <Coins className="h-6 w-6 text-green-500" />
            </div>
            <div className="text-2xl font-bold text-green-500">{totalAvailable.toFixed(2)} LSDC</div>
            <div className="text-sm text-muted-foreground">Available to Claim</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <div className="inline-flex rounded-full bg-primary/10 p-3 mb-4">
              <TrendingUp className="h-6 w-6 text-primary" />
            </div>
            <div className="text-2xl font-bold">{totalClaimed.toFixed(2)} LSDC</div>
            <div className="text-sm text-muted-foreground">Total Claimed</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <div className="inline-flex rounded-full bg-accent/10 p-3 mb-4">
              <Calendar className="h-6 w-6 text-primary" />
            </div>
            <div className="text-2xl font-bold">{totalPending.toFixed(2)} LSDC</div>
            <div className="text-sm text-muted-foreground">Pending</div>
          </CardContent>
        </Card>
      </div>

      {/* Claim Actions */}
      {totalAvailable > 0 && (
        <Card className="border-primary/20 bg-primary/5">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold">Ready to Claim</h3>
                <p className="text-sm text-muted-foreground">
                  You have {availableRewards.length} reward{availableRewards.length !== 1 ? "s" : ""} available
                </p>
              </div>
              <Button
                onClick={handleClaimAll}
                disabled={isClaiming}
                className="bg-gradient-to-r from-primary to-accent hover:opacity-90"
              >
                {isClaiming ? (
                  <>
                    <Download className="mr-2 h-4 w-4 animate-spin" />
                    Claiming...
                  </>
                ) : (
                  <>
                    <Download className="mr-2 h-4 w-4" />
                    Claim All ({totalAvailable.toFixed(2)} LSDC)
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Rewards History */}
      <Card>
        <CardHeader>
          <CardTitle>Rewards History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockRewards.map((reward) => {
              const config = rewardTypeConfig[reward.type]
              const IconComponent = config.icon

              return (
                <div
                  key={reward.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-border/40"
                >
                  <div className="flex items-center space-x-4">
                    <div className={`p-2 rounded-lg ${config.color}`}>
                      <IconComponent className="h-4 w-4" />
                    </div>
                    <div>
                      <div className="font-medium">{reward.description}</div>
                      <div className="text-sm text-muted-foreground flex items-center space-x-2">
                        <span>{reward.date}</span>
                        <Badge variant="outline" className="text-xs">
                          {config.label}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="font-semibold">{reward.amount.toFixed(2)} LSDC</div>
                      <div className="text-xs text-muted-foreground">
                        {reward.status === "available" && <span className="text-green-500">Ready to claim</span>}
                        {reward.status === "claimed" && <span className="text-muted-foreground">Claimed</span>}
                        {reward.status === "pending" && <span className="text-yellow-500">Pending</span>}
                      </div>
                    </div>

                    {reward.status === "available" && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleClaimSingle(reward.id)}
                        className="text-xs"
                      >
                        Claim
                      </Button>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
