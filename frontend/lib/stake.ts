"use client"

import { useEffect, useState } from "react"
import { usePublicClient } from "wagmi"
import { ADDR, STAKE_ABI } from "./contracts"

export function useStakeInfo() {
  const pc = usePublicClient()
  const [token, setToken] = useState<`0x${string}` | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let alive = true
    ;(async () => {
      if (!pc) return
      setLoading(true)
      try {
        const stakeToken = (await pc.readContract({
          address: ADDR.STAKE,
          abi: STAKE_ABI,
          functionName: "stakeToken",
        })) as `0x${string}`
        if (alive) setToken(stakeToken)
      } finally {
        if (alive) setLoading(false)
      }
    })()

    return () => {
      alive = false
    }
  }, [pc])

  return { token, loading, tokenInfo: {} as any }
}

export function useStakedBalance(user?: `0x${string}`) {
  const pc = usePublicClient()
  const [value, setValue] = useState<bigint>(0n)

  useEffect(() => {
    let alive = true
    ;(async () => {
      if (!pc || !user) {
        if (alive) setValue(0n)
        return
      }
      const v = (await pc.readContract({
        address: ADDR.STAKE,
        abi: STAKE_ABI,
        functionName: "stakedBalance",
        args: [user],
      })) as bigint
      if (alive) setValue(v)
    })()
    return () => {
      alive = false
    }
  }, [pc, user])

  return { value }
}
