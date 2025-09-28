"use client"

import { useEffect, useState } from "react"
import { useBalance, useBlockNumber } from "wagmi"
import { pub } from "./dao"
import { ERC20_ABI } from "./contracts"

/**
 * ERC-20 balance for `owner`.
 */
export function useTokenBalance(
  token: `0x${string}`,
  owner?: `0x${string}` | undefined
) {
  const bal = useBalance({
    address: owner,           // REQUIRED for ERC-20 balances
    token,                    // ERC-20 contract address
    query: {
      enabled: Boolean(owner && token), // don’t fetch until connected
      staleTime: 5_000,                
    },
  })

  // Live updates on every new block
  const { data: blockNumber } = useBlockNumber({ watch: true })
  useEffect(() => {
    if (owner && token) bal.refetch()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [blockNumber, owner, token])

  return { ...bal, value: bal.data?.value ?? 0n }
}

export function useTokenInfo(token: `0x${string}`) {
  const [symbol, setSymbol] = useState<string>("TOKEN")
  const [decimals, setDecimals] = useState<number>(18)

  useEffect(() => {
    let alive = true
    async function run() {
      try {
        const [sym, dec] = await Promise.all([
          pub.readContract({ address: token, abi: ERC20_ABI, functionName: "symbol" }) as Promise<string>,
          pub.readContract({ address: token, abi: ERC20_ABI, functionName: "decimals" }) as Promise<number>,
        ])
        if (alive) {
          setSymbol(sym)
          setDecimals(Number(dec))
        }
      } catch {/* noop */}
    }
    run()
    return () => { alive = false }
  }, [token])

  return { symbol, decimals }
}

export function toUnit(amount: number, decimals = 18) {
  const mul = 10n ** BigInt(decimals)
  return BigInt(Math.trunc(amount * 1e6)) * (mul / 1_000_000n) // reduce FP drift
}
export function fromUnit(val: bigint | number, decimals = 18) {
  const n = typeof val === "bigint" ? Number(val) : val
  return n / 10 ** decimals
}
