// lib/licenses.ts
"use client"

import { useEffect, useMemo, useState } from "react"
import { useAccount, useBlockNumber, usePublicClient } from "wagmi"
import { ADDR } from "@/lib/contracts"

// Only the two reads we need
const NFT_ABI = [
  {
    type: "function",
    name: "ownerOf",
    stateMutability: "view",
    inputs: [{ name: "tokenId", type: "uint256" }],
    outputs: [{ type: "address" }],
  },
  {
    type: "function",
    name: "datasetOf",
    stateMutability: "view",
    inputs: [{ name: "tokenId", type: "uint256" }],
    outputs: [{ type: "uint256" }],
  },
] as const

/** Find the highest minted token id using datasetOf-probing (robust to gaps/burns). */
async function discoverLastMintedTokenId(client: any, nftAddr: `0x${string}`) {
  // Grow until we hit the first zero
  let high = 1n
  let lastNonZero = 0n

  // If even token 1 is empty → no mints
  let ds1 = 0n
  try {
    ds1 = (await client.readContract({
      address: nftAddr,
      abi: NFT_ABI,
      functionName: "datasetOf",
      args: [1n],
    })) as bigint
  } catch {}
  if (ds1 === 0n) return 0n

  lastNonZero = 1n
  high = 2n
  // Exponential grow; don't break on first 0 (burns can create gaps)
  for (let iter = 0; iter < 32; iter++) {
    let ds = 0n
    try {
      ds = (await client.readContract({
        address: nftAddr,
        abi: NFT_ABI,
        functionName: "datasetOf",
        args: [high],
      })) as bigint
    } catch { ds = 0n }

    if (ds !== 0n) {
      lastNonZero = high
      high <<= 1n
    } else {
      // Found an upper bound; binary search in (lastNonZero, high)
      let low = lastNonZero + 1n
      let right = high - 1n
      let last = lastNonZero
      while (low <= right) {
        const mid = (low + right) >> 1n
        let dsm = 0n
        try {
          dsm = (await client.readContract({
            address: nftAddr,
            abi: NFT_ABI,
            functionName: "datasetOf",
            args: [mid],
          })) as bigint
        } catch { dsm = 0n }

        if (dsm !== 0n) {
          last = mid
          low = mid + 1n
        } else {
          right = mid - 1n
        }
      }
      return last
    }
  }
  // Safety cap; if we somehow never saw a zero, assume lastNonZero
  return lastNonZero
}

/**
 * Returns the set of dataset IDs the connected user owns,
 * by iterating tokenIds 1..lastMinted and checking ownerOf → datasetOf.
 */
export function usePurchasedDatasetIds(addrOverride?: `0x${string}`) {
  const { address } = useAccount()
  const owner = (addrOverride ?? address)?.toLowerCase()
  const client = usePublicClient()
  const { data: tip } = useBlockNumber({ watch: true })

  const [ids, setIds] = useState<Set<number>>(new Set())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!client || !owner) {
      setIds(new Set())
      return
    }

    let cancelled = false

    const chunk = <T,>(arr: T[], size: number) =>
      Array.from({ length: Math.ceil(arr.length / size) }, (_, i) => arr.slice(i * size, (i + 1) * size))

    ;(async () => {
      setLoading(true)
      setError(null)
      try {
        const nft = ADDR.NFT as `0x${string}`
        const last = await discoverLastMintedTokenId(client, nft)
        if (last === 0n) {
          if (!cancelled) setIds(new Set())
          return
        }

        const tokenIds = Array.from({ length: Number(last) }, (_, i) => BigInt(i + 1))

        // Step 1: find tokens currently owned by user
        const owned: bigint[] = []
        for (const batch of chunk(tokenIds, 300)) {
          const res = await client.multicall({
            allowFailure: true,
            contracts: batch.map((t) => ({
              address: nft,
              abi: NFT_ABI,
              functionName: "ownerOf",
              args: [t] as const,
            })),
          })
          res.forEach((r, i) => {
            if (r.status === "success" && String(r.result).toLowerCase() === owner) {
              owned.push(batch[i])
            }
          })
        }

        if (owned.length === 0) {
          if (!cancelled) setIds(new Set())
          return
        }

        // Step 2: map owned tokens to datasetIds
        const dsIds: number[] = []
        for (const batch of chunk(owned, 300)) {
          const res = await client.multicall({
            allowFailure: true,
            contracts: batch.map((t) => ({
              address: nft,
              abi: NFT_ABI,
              functionName: "datasetOf",
              args: [t] as const,
            })),
          })
          res.forEach((r) => {
            if (r.status === "success") {
              const v = r.result as bigint
              if (v && v !== 0n) dsIds.push(Number(v))
            }
          })
        }

        if (!cancelled) setIds(new Set(dsIds))
      } catch (e: any) {
        if (!cancelled) setError(String(e?.message || e))
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()

    return () => { cancelled = true }
  }, [client, owner, tip?.toString()])

  return { ids, loading, error }
}

/** Convenience hook: boolean for a given datasetId */
export function useIsDatasetPurchased(datasetId?: number | string | null) {
  const { ids } = usePurchasedDatasetIds()
  const idNum = typeof datasetId === "string" ? Number(datasetId) : datasetId ?? null
  return useMemo(() => (idNum == null ? false : ids.has(Number(idNum))), [ids, idNum])
}
