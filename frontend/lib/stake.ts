"use client"

import { useEffect, useMemo, useState } from "react"
import { pub } from "./dao"
import { ADDR, STAKE_ABI } from "./contracts"

export type Tier = { name: string; minStake: bigint; rewardsMultiplier: bigint }

export function useStakeInfo() {
  const [stakeToken, setStakeToken]     = useState<`0x${string}` | null>(null)
  const [rewardsToken, setRewardsToken] = useState<`0x${string}` | null>(null)
  const [tiers, setTiers]               = useState<Tier[]>([])
  const [loading, setLoading]           = useState(true)

  useEffect(() => {
    let alive = true
    async function run() {
      setLoading(true)
      try {
        const [stk, rwd] = await Promise.all([
          pub.readContract({ address: ADDR.STAKE, abi: STAKE_ABI, functionName: "stakeToken" }) as Promise<`0x${string}`>,
          pub.readContract({ address: ADDR.STAKE, abi: STAKE_ABI, functionName: "rewardsToken" }) as Promise<`0x${string}`>,
        ])
        const tierIdx = [0n,1n,2n,3n]
        const t = await Promise.all(tierIdx.map(async (i) => {
          const ti = await pub.readContract({ address: ADDR.STAKE, abi: STAKE_ABI, functionName: "tiers", args: [i] }) as any
          return {
            name: String(ti.name ?? ti[0]),
            minStake: BigInt(ti.minStake ?? ti[1] ?? 0n),
            rewardsMultiplier: BigInt(ti.rewardsMultiplier ?? ti[2] ?? 100n),
          } as Tier
        }))
        if (!alive) return
        setStakeToken(stk)
        setRewardsToken(rwd)
        setTiers(t)
      } finally {
        if (alive) setLoading(false)
      }
    }
    run()
    return () => { alive = false }
  }, [])

  return { stakeToken, rewardsToken, tiers, loading }
}

export function useStakedBalance(user?: `0x${string}`) {
  const [value, setValue] = useState<bigint>(0n)
  useEffect(() => {
    let alive = true
    async function run() {
      if (!user) { setValue(0n); return }
      const v = (await pub.readContract({
        address: ADDR.STAKE,
        abi: STAKE_ABI,
        functionName: "stakedBalance",
        args: [user],
      })) as bigint
      if (alive) setValue(v)
    }
    run()
    return () => { alive = false }
  }, [user])
  return { value }
}

export type UserStake = {
  amount: bigint
  tierIndex: number
  stakedAt: bigint
  lastRPT: bigint
  boostUntil: bigint
  boostBps: bigint
}

export function useStakeUser(user?: `0x${string}`) {
  const [info, setInfo] = useState<UserStake | null>(null)
  const [pending, setPending] = useState<bigint>(0n)

  useEffect(() => {
    let alive = true
    async function run() {
      if (!user) { setInfo(null); setPending(0n); return }
      const [u, p] = await Promise.all([
        pub.readContract({ address: ADDR.STAKE, abi: STAKE_ABI, functionName: "users", args: [user] }) as Promise<any>,
        pub.readContract({ address: ADDR.STAKE, abi: STAKE_ABI, functionName: "pendingRewards", args: [user] }) as Promise<bigint>,
      ])
      if (!alive) return
      setInfo({
        amount: BigInt(u.amount ?? u[0] ?? 0n),
        tierIndex: Number(u.tierIndex ?? u[1] ?? 0n),
        stakedAt: BigInt(u.stakedAt ?? u[2] ?? 0n),
        lastRPT: BigInt(u.lastRPT ?? u[3] ?? 0n),
        boostUntil: BigInt(u.boostUntil ?? u[4] ?? 0n),
        boostBps: BigInt(u.boostBps ?? u[5] ?? 0n),
      })
      setPending(p ?? 0n)
    }
    run()
    return () => { alive = false }
  }, [user])

  return { info, pending }
}


export function usePendingRewards(user?: `0x${string}`, pollMs = 8000) {
  const [value, setValue] = useState<bigint>(0n)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    let timer: number | null = null

    async function tick() {
      if (!user) { if (alive) setValue(0n); return }
      try {
        if (alive) setLoading(true), setError(null)
        const v = await pub.readContract({
          address: ADDR.STAKE,
          abi: STAKE_ABI,
          functionName: "pendingRewards",
          args: [user],
        }) as bigint
        if (alive) setValue(v)
      } catch (e: any) {
        if (alive) setError(String(e?.message || e))
      } finally {
        if (alive) setLoading(false)
      }
    }

    tick()
    if (pollMs > 0) {
      // @ts-ignore - window typing in Node
      timer = setInterval(tick, pollMs)
    }
    return () => {
      alive = false
      if (timer) clearInterval(timer)
    }
  }, [user, pollMs])

  return { value, loading, error }
}

export function useTotalRewardsDistributed(pollMs = 12000) {
  const [value, setValue] = useState<bigint>(0n)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    let timer: number | null = null

    async function tick() {
      try {
        if (alive) setLoading(true), setError(null)
        const v = await pub.readContract({
          address: ADDR.STAKE,
          abi: STAKE_ABI,
          functionName: "totalRewardsDistributed",
        }) as bigint
        if (alive) setValue(v)
      } catch (e: any) {
        if (alive) setError(String(e?.message || e))
      } finally {
        if (alive) setLoading(false)
      }
    }

    tick()
    if (pollMs > 0) {
      // @ts-ignore
      timer = setInterval(tick, pollMs)
    }
    return () => {
      alive = false
      if (timer) clearInterval(timer)
    }
  }, [pollMs])

  return { value, loading, error }
}
