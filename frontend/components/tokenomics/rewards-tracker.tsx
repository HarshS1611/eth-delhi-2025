"use client"

import { useState, useMemo } from "react"
import { useAccount, useWriteContract } from "wagmi"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { useToast } from "@/hooks/use-toast"
import { Coins, TrendingUp, Calendar, Download, Loader2, Gift, ArrowUpRight } from "lucide-react"

import { ADDR, STAKE_ABI } from "@/lib/contracts"
import { usePendingRewards, useTotalRewardsDistributed } from "@/lib/stake"
import { useTokenInfo } from "@/lib/token"
import { fromUnit } from "@/lib/token"
import { pub } from "@/lib/dao"


const mockRewards: any[] = [
  {
    id: "1",
    date: "2024-01-20",
    type: "staking",
    amount: 12.45,
    status: "claimed",
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
    status: "claimed",
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
    status: "claimed",
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
  const { address } = useAccount()

  const { symbol = "LSDC", decimals = 18 } = useTokenInfo(ADDR.LSDC)

  // Reads
  const { value: pendingRaw, loading: pendingLoading } = usePendingRewards(address as `0x${string}` | undefined, 6000)
  const { value: distributedRaw } = useTotalRewardsDistributed(10000)

  const pending = useMemo(() => fromUnit(pendingRaw, decimals), [pendingRaw, decimals])
  const distributed = useMemo(() => fromUnit(distributedRaw, decimals), [distributedRaw, decimals])

  // Write
  const { writeContractAsync, isPending: isSubmitting } = useWriteContract()
  const [isClaiming, setClaiming] = useState(false)

  const canClaim = !!address && pendingRaw > 0n && !isClaiming && !isSubmitting

  async function handleClaim() {
    if (!address) {
      toast({ title: "Connect wallet", description: "Please connect your wallet to claim.", variant: "destructive" })
      return
    }
    setClaiming(true)
    try {
      const hash = await writeContractAsync({
        address: ADDR.STAKE,
        abi: STAKE_ABI,
        functionName: "claimRewards",
        args: [],
      })
      await pub.waitForTransactionReceipt({ hash })
      toast({ title: "Rewards claimed!", description: `Sent to your wallet.` })
    } catch (e: any) {
      toast({
        title: "Claim failed",
        description: String(e?.shortMessage || e?.message || e),
        variant: "destructive",
      })
    } finally {
      setClaiming(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-green-500/20 bg-green-500/5">
          <CardContent className="p-6 text-center">
            <div className="inline-flex rounded-full bg-green-500/10 p-3 mb-4">
              <Coins className="h-6 w-6 text-green-500" />
            </div>
            <div className="text-2xl font-bold text-green-500">
              {pendingLoading ? "…" : pending.toFixed(6)} {symbol}
            </div>
            <div className="text-sm text-muted-foreground">Pending / Claimable</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <div className="inline-flex rounded-full bg-primary/10 p-3 mb-4">
              <TrendingUp className="h-6 w-6 text-primary" />
            </div>
            <div className="text-2xl font-bold">{distributed.toFixed(3)} {symbol}</div>
            <div className="text-sm text-muted-foreground">Total Rewards Distributed</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <div className="inline-flex rounded-full bg-accent/10 p-3 mb-4">
              <Calendar className="h-6 w-6 text-primary" />
            </div>
            <div className="text-2xl font-bold">{/* Optional extra metric */}—</div>
            <div className="text-sm text-muted-foreground">Last updated every few seconds</div>
          </CardContent>
        </Card>
      </div>

      {/* Claim Action */}
      <Card className="border-primary/20 bg-primary/5">
        <CardHeader>
          <CardTitle>Claim Your Rewards</CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-muted-foreground">You can claim your accrued {symbol} rewards.</div>
            </div>
            <Button
              onClick={handleClaim}
              disabled={!canClaim}
              className="bg-gradient-to-r from-primary to-accent hover:opacity-90"
            >
              {isClaiming || isSubmitting ? (
                <>
                  <Download className="mr-2 h-4 w-4 animate-spin" />
                  Claiming…
                </>
              ) : (
                <>
                  <Download className="mr-2 h-4 w-4" />
                  Claim {pending.toFixed(6)} {symbol}
                </>
              )}
            </Button>
          </div>
          {!address && (
            <div className="text-xs text-muted-foreground mt-2">
              Connect your wallet to see and claim rewards.
            </div>
          )}
        </CardContent>
      </Card>

      {/* History (placeholder for now; your contract doesn't expose a per-user claim history) */}
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




