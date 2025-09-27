// components/tokenomics/staking-interface.tsx
"use client"

import type React from "react"
import { useAccount } from "wagmi"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { Coins, Shield, Zap, Crown, Star, Lock } from "lucide-react"
import { useStakeInfo, useStakedBalance } from "@/lib/stake"
import { useTokenBalance, useTokenInfo, fromUnit } from "@/lib/token"
import { ADDR } from "@/lib/contracts"

const tiers = [
  { id: "bronze",  name: "Bronze Contributor", min: 100,   apy: 8,  mult: 1,   icon: Shield, color: "text-orange-500",  bg: "bg-orange-500/10" },
  { id: "silver",  name: "Silver Curator",     min: 1000,  apy: 12, mult: 1.5, icon: Star,   color: "text-gray-400",   bg: "bg-gray-400/10" },
  { id: "gold",    name: "Gold Validator",     min: 5000,  apy: 16, mult: 2,   icon: Crown,  color: "text-yellow-500", bg: "bg-yellow-500/10" },
  { id: "diamond", name: "Diamond Guardian",   min: 20000, apy: 20, mult: 3,   icon: Zap,    color: "text-blue-500",   bg: "bg-blue-500/10" },
]

export function StakingInterface() {
  const { toast } = useToast()
  const { address } = useAccount()
  const { token, tokenInfo } = useStakeInfo()
  const stakeToken = token ?? ADDR.LSDC
  const stkBal = useStakedBalance(address as `0x${string}` | undefined)
  const walletBal = useTokenBalance(stakeToken)
  const walletTokenInfo = useTokenInfo(stakeToken)

  const decimals = walletTokenInfo.decimals || 18
  const stakedHuman = Number(fromUnit(stkBal.value, decimals))
  const balanceHuman = Number(fromUnit(walletBal.value, decimals))
  const currentTier = tiers.slice().reverse().find(t => stakedHuman >= t.min) || null

  return (
    <div className="space-y-6">
      <Card className="border-primary/20 bg-primary/5">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            {currentTier ? (<><currentTier.icon className={`h-5 w-5 ${currentTier.color}`} /><span>Current Stake: {currentTier.name}</span></>) : (<>Current Stake</>)}
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary">
              {stakedHuman.toLocaleString(undefined, { maximumFractionDigits: 4 })}
            </div>
            <div className="text-sm text-muted-foreground">{walletTokenInfo.symbol || "TOKEN"} Staked</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-primary">{currentTier?.apy ?? 0}%</div>
            <div className="text-sm text-muted-foreground">APY (tier)</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-chart-2">{currentTier?.mult ?? 1}x</div>
            <div className="text-sm text-muted-foreground">Voting Power</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-chart-3">{((stakedHuman * (currentTier?.apy ?? 0)) / 365 / 100).toFixed(4)}</div>
            <div className="text-sm text-muted-foreground">Daily Rewards ({walletTokenInfo.symbol || "TOKEN"})</div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">Available Balance</h3>
              <p className="text-sm text-muted-foreground">{walletTokenInfo.symbol || "TOKEN"} ready for staking</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">
                {balanceHuman.toLocaleString(undefined, { maximumFractionDigits: 4 })}
              </div>
              <div className="text-sm text-muted-foreground">{walletTokenInfo.symbol || "TOKEN"}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {tiers.map((tier) => {
          const Icon = tier.icon
          const isCurrent = currentTier?.id === tier.id
          return (
            <Card key={tier.id} className={`transition-all ${isCurrent ? "border-accent/50 bg-accent/5" : "border-border/40"}`}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`p-2 rounded-lg ${tier.bg}`}><Icon className={`h-5 w-5 ${tier.color}`} /></div>
                    <span>{tier.name}</span>
                  </div>
                  {isCurrent && <Badge variant="secondary">Current</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div><div className="text-sm text-muted-foreground">Min Stake</div><div className="font-semibold">{tier.min.toLocaleString()} {walletTokenInfo.symbol || "TOKEN"}</div></div>
                  <div><div className="text-sm text-muted-foreground">APY</div><div className="font-semibold text-green-500">{tier.apy}%</div></div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Stake Amount</label>
                  <Input type="number" placeholder={`Min: ${tier.min}`} disabled />
                  <Button disabled className="w-full"><Lock className="mr-2 h-4 w-4" />Stake (ABI write not wired yet)</Button>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
