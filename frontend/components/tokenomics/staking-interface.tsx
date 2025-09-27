"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { Coins, Shield, Zap, Crown, Star, Lock } from "lucide-react"

interface StakingTier {
  id: string
  name: string
  minStake: number
  maxStake: number | null
  apy: number
  votingMultiplier: number
  benefits: string[]
  icon: React.ComponentType<{ className?: string }>
  color: string
  bgColor: string
}

const stakingTiers: StakingTier[] = [
  {
    id: "bronze",
    name: "Bronze Contributor",
    minStake: 100,
    maxStake: 999,
    apy: 8,
    votingMultiplier: 1,
    benefits: ["Basic voting rights", "Monthly rewards", "Community access"],
    icon: Shield,
    color: "text-orange-500",
    bgColor: "bg-orange-500/10",
  },
  {
    id: "silver",
    name: "Silver Curator",
    minStake: 1000,
    maxStake: 4999,
    apy: 12,
    votingMultiplier: 1.5,
    benefits: ["Enhanced voting power", "Weekly rewards", "Priority support", "Beta features"],
    icon: Star,
    color: "text-gray-400",
    bgColor: "bg-gray-400/10",
  },
  {
    id: "gold",
    name: "Gold Validator",
    minStake: 5000,
    maxStake: 19999,
    apy: 16,
    votingMultiplier: 2,
    benefits: ["2x voting power", "Daily rewards", "Governance proposals", "Exclusive events"],
    icon: Crown,
    color: "text-yellow-500",
    bgColor: "bg-yellow-500/10",
  },
  {
    id: "diamond",
    name: "Diamond Guardian",
    minStake: 20000,
    maxStake: null,
    apy: 20,
    votingMultiplier: 3,
    benefits: ["3x voting power", "Instant rewards", "Council membership", "Revenue sharing"],
    icon: Zap,
    color: "text-blue-500",
    bgColor: "bg-blue-500/10",
  },
]

export function StakingInterface() {
  const { toast } = useToast()
  const [selectedTier, setSelectedTier] = useState<string | null>(null)
  const [stakeAmount, setStakeAmount] = useState("")
  const [isStaking, setIsStaking] = useState(false)

  // Mock user data
  const userBalance = 15000
  const currentStake = 2500
  const currentTier = stakingTiers.find(
    (tier) => currentStake >= tier.minStake && (!tier.maxStake || currentStake <= tier.maxStake),
  )

  const handleStake = async () => {
    const amount = Number.parseFloat(stakeAmount)
    if (!amount || amount <= 0) {
      toast({
        title: "Invalid amount",
        description: "Please enter a valid staking amount.",
        variant: "destructive",
      })
      return
    }

    if (amount > userBalance) {
      toast({
        title: "Insufficient balance",
        description: "You don't have enough D3 tokens to stake this amount.",
        variant: "destructive",
      })
      return
    }

    setIsStaking(true)

    // Simulate staking transaction
    await new Promise((resolve) => setTimeout(resolve, 2000))

    setIsStaking(false)
    setStakeAmount("")
    setSelectedTier(null)

    toast({
      title: "Staking successful!",
      description: `Successfully staked ${amount} D3 tokens. Your rewards will start accruing immediately.`,
    })
  }

  const calculateRewards = (amount: number, tier: StakingTier) => {
    const dailyReward = (amount * tier.apy) / 365 / 100
    const monthlyReward = dailyReward * 30
    const yearlyReward = amount * (tier.apy / 100)

    return { dailyReward, monthlyReward, yearlyReward }
  }

  return (
    <div className="space-y-6">
      {/* Current Staking Status */}
      {currentStake > 0 && currentTier && (
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <currentTier.icon className={`h-5 w-5 ${currentTier.color}`} />
              <span>Current Stake: {currentTier.name}</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary">{currentStake.toLocaleString()}</div>
                <div className="text-sm text-muted-foreground">DataCoin Staked</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary">{currentTier.apy}%</div>
                <div className="text-sm text-muted-foreground">APY</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-chart-2">{currentTier.votingMultiplier}x</div>
                <div className="text-sm text-muted-foreground">Voting Power</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-chart-3">
                  {calculateRewards(currentStake, currentTier).dailyReward.toFixed(2)}
                </div>
                <div className="text-sm text-muted-foreground">Daily LSDC</div>
              </div>
            </div>

            <div className="flex flex-wrap gap-4">
              Benfits: 
              {currentTier.benefits.map((benefit) => (
                <Badge key={benefit} variant="secondary" className="text-xs bg-primary/10">
                  {benefit}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Available Balance */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">Available Balance</h3>
              <p className="text-sm text-muted-foreground">D3 tokens ready for staking</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">{userBalance.toLocaleString()}</div>
              <div className="text-sm text-muted-foreground">D3 Tokens</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Staking Tiers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {stakingTiers.map((tier) => {
          const isSelected = selectedTier === tier.id
          const isCurrentTier = currentTier?.id === tier.id
          const stakeAmountNum = Number.parseFloat(stakeAmount) || 0
          const projectedRewards = stakeAmountNum > 0 ? calculateRewards(stakeAmountNum, tier) : null

          return (
            <Card
              key={tier.id}
              className={`cursor-pointer transition-all duration-300 ${
                isSelected
                  ? "border-primary bg-primary/5 shadow-lg"
                  : isCurrentTier
                    ? "border-accent/50 bg-accent/5"
                    : "border-border/40 hover:border-border/60 hover:bg-card/80"
              }`}
              onClick={() => setSelectedTier(isSelected ? null : tier.id)}
            >
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className={`p-2 rounded-lg ${tier.bgColor}`}>
                      <tier.icon className={`h-5 w-5 ${tier.color}`} />
                    </div>
                    <span>{tier.name}</span>
                  </div>
                  {isCurrentTier && <Badge variant="default">Current</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-muted-foreground">Min Stake</div>
                    <div className="font-semibold">{tier.minStake.toLocaleString()} D3</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">APY</div>
                    <div className="font-semibold text-green-500">{tier.apy}%</div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="text-sm text-muted-foreground">Benefits</div>
                  <div className="flex flex-wrap gap-1">
                    {tier.benefits.slice(0, 2).map((benefit) => (
                      <Badge key={benefit} variant="outline" className="text-xs">
                        {benefit}
                      </Badge>
                    ))}
                    {tier.benefits.length > 2 && (
                      <Badge variant="outline" className="text-xs">
                        +{tier.benefits.length - 2} more
                      </Badge>
                    )}
                  </div>
                </div>

                {isSelected && (
                  <div className="space-y-4 pt-4 border-t">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Stake Amount</label>
                      <Input
                        type="number"
                        placeholder={`Min: ${tier.minStake} D3`}
                        value={stakeAmount}
                        onChange={(e) => setStakeAmount(e.target.value)}
                        min={tier.minStake}
                        max={tier.maxStake || userBalance}
                      />
                    </div>

                    {projectedRewards && (
                      <div className="bg-muted/50 rounded-lg p-3 space-y-2">
                        <div className="text-sm font-medium">Projected Rewards</div>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                          <div>
                            <div className="text-muted-foreground">Daily</div>
                            <div className="font-medium">{projectedRewards.dailyReward.toFixed(2)} LSDC</div>
                          </div>
                          <div>
                            <div className="text-muted-foreground">Monthly</div>
                            <div className="font-medium">{projectedRewards.monthlyReward.toFixed(2)} LSDC</div>
                          </div>
                          <div>
                            <div className="text-muted-foreground">Yearly</div>
                            <div className="font-medium">{projectedRewards.yearlyReward.toFixed(2)} LSDC</div>
                          </div>
                        </div>
                      </div>
                    )}

                    <Button
                      onClick={handleStake}
                      disabled={isStaking || !stakeAmount || Number.parseFloat(stakeAmount) < tier.minStake}
                      className="w-full bg-gradient-to-r from-primary to-accent hover:opacity-90"
                    >
                      {isStaking ? (
                        <>
                          <Lock className="mr-2 h-4 w-4 animate-spin" />
                          Staking...
                        </>
                      ) : (
                        <>
                          <Coins className="mr-2 h-4 w-4" />
                          Stake {stakeAmount || tier.minStake} D3
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
