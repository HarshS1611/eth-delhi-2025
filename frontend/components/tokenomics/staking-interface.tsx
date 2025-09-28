"use client"

import { useState, useMemo } from "react"
import { useAccount, useWriteContract } from "wagmi"
import { parseUnits } from "viem"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { Coins, Shield, Zap, Crown, Star, Lock, Download, Undo2 } from "lucide-react"
import { useStakeInfo, useStakedBalance, useStakeUser } from "@/lib/stake"
import { useTokenBalance, useTokenInfo, fromUnit } from "@/lib/token"
import { ADDR, ERC20_ABI, STAKE_ABI } from "@/lib/contracts"

const TierIcon = [Shield, Star, Crown, Zap]

export function StakingInterface() {
  const { toast } = useToast()
  const { address } = useAccount()

  const { stakeToken, rewardsToken, tiers, loading } = useStakeInfo()
  const stakeTokenAddr = stakeToken ?? ADDR.DIP            // <-- DIP is the stake token
  const rewardsTokenAddr = rewardsToken ?? ADDR.LSDC       // LSDC is rewards

  const walletBal = useTokenBalance(stakeTokenAddr, address as `0x${string}` | undefined)
  const stakeTokenInfo = useTokenInfo(stakeTokenAddr)
  const rewardsTokenInfo = useTokenInfo(rewardsTokenAddr)

  const staked = useStakedBalance(address as `0x${string}` | undefined)
  const user   = useStakeUser(address as `0x${string}` | undefined)

  const decimals = stakeTokenInfo.decimals || 18
  const stakedHuman  = Number(fromUnit(staked.value, decimals))
  const balanceHuman = Number(fromUnit(walletBal.value, decimals))
  const pendingHuman = Number(fromUnit(user.pending, rewardsTokenInfo.decimals || 18))

  const tierFromIndex = (i: number | null | undefined) => {
    const idx = typeof i === "number" && i >=0 && i < 4 ? i : 0
    return tiers[idx] || { name: "Bronze", minStake: 0n, rewardsMultiplier: 100n }
  }
  const currentTier = tierFromIndex(user.info?.tierIndex)

  // local inputs per tier (stake & unstake)
  const [stakeAmount, setStakeAmount]     = useState<Record<number, string>>({0:"",1:"",2:"",3:""})
  const [unstakeAmount, setUnstakeAmount] = useState<string>("")

  const write = useWriteContract()

  async function handleStake(tierIndex: number) {
    try {
      if (!address) throw new Error("Connect wallet first")
      const amtStr = stakeAmount[tierIndex] || ""
      const amt = Number(amtStr)
      if (!amtStr || isNaN(amt) || amt <= 0) throw new Error("Enter stake amount")
      const min = Number(fromUnit(tiers[tierIndex].minStake, decimals))
      if (amt < min) throw new Error(`Minimum for ${tiers[tierIndex].name} is ${min} ${stakeTokenInfo.symbol}`)

      const amountWei = parseUnits(amtStr, decimals)

      // 1) Approve DIP to staking contract
      const approveHash = await write.writeContractAsync({
        address: stakeTokenAddr,
        abi: ERC20_ABI,
        functionName: "approve",
        args: [ADDR.STAKE, amountWei],
      })
      await waitReceipt(approveHash)

      // 2) Stake
      const stakeHash = await write.writeContractAsync({
        address: ADDR.STAKE,
        abi: STAKE_ABI,
        functionName: "stake",
        args: [amountWei, BigInt(tierIndex)],
      })
      await waitReceipt(stakeHash)

      toast({ title: "Staked!", description: `Staked ${amt} ${stakeTokenInfo.symbol} in ${tiers[tierIndex].name}.` })
      setStakeAmount((s) => ({ ...s, [tierIndex]: "" }))
    } catch (e: any) {
      toast({ title: "Stake failed", description: String(e?.message || e), variant: "destructive" })
    }
  }

  async function handleUnstake() {
    try {
      if (!address) throw new Error("Connect wallet first")
      const amt = Number(unstakeAmount)
      if (!unstakeAmount || isNaN(amt) || amt <= 0) throw new Error("Enter unstake amount")
      const amountWei = parseUnits(unstakeAmount, decimals)

      const tx = await write.writeContractAsync({
        address: ADDR.STAKE,
        abi: STAKE_ABI,
        functionName: "unstake",
        args: [amountWei],
      })
      await waitReceipt(tx)
      toast({ title: "Unstaked!", description: `Unstaked ${amt} ${stakeTokenInfo.symbol}.` })
      setUnstakeAmount("")
    } catch (e: any) {
      toast({ title: "Unstake failed", description: String(e?.message || e), variant: "destructive" })
    }
  }

  async function handleClaim() {
    try {
      if (!address) throw new Error("Connect wallet first")
      const tx = await write.writeContractAsync({
        address: ADDR.STAKE,
        abi: STAKE_ABI,
        functionName: "claimRewards",
        args: [],
      })
      await waitReceipt(tx)
      toast({ title: "Rewards claimed!", description: `Claimed ${pendingHuman.toFixed(4)} ${rewardsTokenInfo.symbol}.` })
    } catch (e: any) {
      toast({ title: "Claim failed", description: String(e?.message || e), variant: "destructive" })
    }
  }

  async function waitReceipt(hash: `0x${string}`) {
    const { pub } = await import("@/lib/dao")
    await pub.waitForTransactionReceipt({ hash })
  }

  return (
    <div className="space-y-6">
      <Card className="border-primary/20 bg-primary/5">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>Current Stake</span>
            {user.info && (
              <Badge variant="secondary">{tierFromIndex(user.info.tierIndex).name}</Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary">
              {stakedHuman.toLocaleString(undefined, { maximumFractionDigits: 4 })}
            </div>
            <div className="text-sm text-muted-foreground">{stakeTokenInfo.symbol} Staked</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-chart-2">
              {(Number(currentTier.rewardsMultiplier) / 100).toFixed(2)}x
            </div>
            <div className="text-sm text-muted-foreground">Tier Multiplier</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{Number(user.info?.boostBps ?? 0) / 100}%</div>
            <div className="text-sm text-muted-foreground">Gov Boost</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-chart-3">
              {pendingHuman.toLocaleString(undefined, { maximumFractionDigits: 4 })}
            </div>
            <div className="text-sm text-muted-foreground">Claimable ({rewardsTokenInfo.symbol})</div>
          </div>
        </CardContent>
      </Card>

      {/* Wallet balance */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">Available Balance</h3>
              <p className="text-sm text-muted-foreground">
                {stakeTokenInfo.symbol} ready for staking
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">
                {balanceHuman.toLocaleString(undefined, { maximumFractionDigits: 4 })}
              </div>
              <div className="text-sm text-muted-foreground">{stakeTokenInfo.symbol}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tiers from chain */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {tiers.map((tier, idx) => {
          const Icon = TierIcon[idx] || Shield
          const minHuman = Number(fromUnit(tier.minStake, decimals))
          const isCurrent = user.info?.tierIndex === idx
          const inputVal = stakeAmount[idx] ?? ""

          return (
            <Card key={idx} className={`transition-all ${isCurrent ? "border-accent/50 bg-accent/5" : "border-border/40"}`}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-muted/50">
                      <Icon className="h-5 w-5 text-primary" />
                    </div>
                    <span>{tier.name}</span>
                  </div>
                  {isCurrent && <Badge variant="secondary">Current</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-muted-foreground">Min Stake</div>
                    <div className="font-semibold">
                      {minHuman.toLocaleString()} {stakeTokenInfo.symbol}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Multiplier</div>
                    <div className="font-semibold text-green-500">
                      {(Number(tier.rewardsMultiplier)/100).toFixed(2)}x
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Stake Amount</label>
                  <Input
                    type="number"
                    min={minHuman}
                    step="any"
                    placeholder={`Min: ${minHuman}`}
                    value={inputVal}
                    onChange={(e) => setStakeAmount((s) => ({ ...s, [idx]: e.target.value }))}
                  />
                  <Button
                    onClick={() => handleStake(idx)}
                    className="w-full bg-gradient-to-r from-primary to-accent hover:opacity-90"
                  >
                    <Lock className="mr-2 h-4 w-4" />
                    Stake
                  </Button>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Actions: claim + unstake */}
      <Card>
        <CardContent className="p-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* <div className="flex flex-col">
            <span className="text-sm text-muted-foreground mb-2">Claimable</span>
            <div className="text-xl font-semibold mb-2">
              {pendingHuman.toLocaleString(undefined, { maximumFractionDigits: 4 })} {rewardsTokenInfo.symbol}
            </div>
            <Button onClick={handleClaim} className="w-full">
              <Download className="mr-2 h-4 w-4" /> Claim Rewards
            </Button>
          </div> */}

          <div className="md:col-span-2">
            <span className="text-sm text-muted-foreground">Unstake Amount</span>
            <div className="mt-2 flex gap-2">
              <Input
                type="number"
                step="any"
                placeholder="0.0"
                value={unstakeAmount}
                onChange={(e) => setUnstakeAmount(e.target.value)}
              />
              <Button variant="outline" onClick={() => setUnstakeAmount(String(stakedHuman))}>
                Max
              </Button>
              <Button onClick={handleUnstake}>
                <Undo2 className="mr-2 h-4 w-4" /> Unstake
              </Button>
            </div>
            <div className="text-xs text-muted-foreground mt-2">
              Note: Unstake is locked for 7 days from your first stake (contract `LOCK_PERIOD`).
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
