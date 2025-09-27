"use client"

import { useEffect, useState } from "react"
import { useAccount, useBalance } from "wagmi"
import { usePublicClient } from "wagmi"
import { ERC20_ABI } from "./contracts"

export function useTokenBalance(token: `0x${string}`) {
  const { address } = useAccount()
  const q = useBalance({ address, token })
  return { ...q, value: q.data?.value ?? 0n }
}

export function useTokenInfo(token: `0x${string}`) {
  const pc = usePublicClient()
  const [symbol, setSymbol] = useState<string>("TOKEN")
  const [decimals, setDecimals] = useState<number>(18)

  useEffect(() => {
    let alive = true
    ;(async () => {
      try {
        if (!pc) return
        const [sym, dec] = await Promise.all([
          pc.readContract({ address: token, abi: ERC20_ABI, functionName: "symbol" }) as Promise<string>,
          pc.readContract({ address: token, abi: ERC20_ABI, functionName: "decimals" }) as Promise<number>,
        ])
        if (alive) {
          setSymbol(sym)
          setDecimals(Number(dec))
        }
      } catch {
        /* ignore */
      }
    })()
    return () => {
      alive = false
    }
  }, [pc, token])

  return { symbol, decimals }
}

export function toUnit(amount: number, decimals = 18) {
  const mul = BigInt(10) ** BigInt(decimals)
  return BigInt(Math.round(amount * 1e6)) * (mul / 1_000_000n)
}
export function fromUnit(val: bigint | number, decimals = 18) {
  const n = typeof val === "bigint" ? Number(val) : val
  return n / 10 ** decimals
}
