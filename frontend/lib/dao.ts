"use client"

import { parseUnits } from "viem"
import { useEffect, useState } from "react"
import { usePublicClient, useWriteContract, useAccount } from "wagmi"
import { ADDR, DATA_DAO_ABI, ERC20_ABI } from "./contracts"
import { createPublicClient, http } from "viem"
import { sepolia } from "wagmi/chains"
import { shapeDataset } from "./shapers" 

const chain = sepolia
export const pub = createPublicClient({ chain, transport: http() })

type OnchainRow = any

function useDataset(id: bigint, d: OnchainRow) {
  const title = d.title ?? d[1]
  const tokenUri = d.tokenUri ?? d[2]
  const creator = d.creator ?? d[3]
  const price = d.price ?? d[4]
  const qualityScore = Number(d.qualityScore ?? d[5] ?? 0)
  const votes = d.votes ?? d[7] ?? 0n
  const cid = d.cid ?? d[0]

  return {
    id: id.toString(),
    title: String(title),
    description: String(tokenUri),
    category: "On-Chain",
    tags: [],
    contributor: { name: String(creator), verified: true },
    qualityScore,
    price: Number(price) / 1e18,
    downloads: Number(votes),
    uploadDate: "",
    fileSize: "",
    fileType: "IPFS",
    cid: String(cid),
    raw: d,
    source: "onchain" as const,
  }
}

export function useDatasets() {
  const pc = usePublicClient()
  const [items, setItems] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    ;(async () => {
      if (!pc) return
      setIsLoading(true)
      setError(null)
      try {
        const nextId = (await pc.readContract({
          address: ADDR.DATA_DAO,
          abi: DATA_DAO_ABI,
          functionName: "nextDatasetId",
        })) as bigint

        const count = Number(nextId - 1n) 
        if (count === 0) {
          if (alive) setItems([])
          return
        }

        const ids = Array.from({ length: count }, (_, i) => BigInt(i + 1)) 
        const rows = await Promise.all(
          ids.map(async (id) => {
            const d = await pub.readContract({
              address: ADDR.DATA_DAO,
              abi: DATA_DAO_ABI,
              functionName: "datasets",
              args: [id],
            })
            return shapeDataset(id, d)      
          })
        )

        if (alive) setItems(rows)      
      } catch (e: any) {
        if (alive) setError(String(e?.shortMessage ?? e?.message ?? e))
      } finally {
        if (alive) setIsLoading(false)
      }
    })()

    return () => {
      alive = false
    }
  }, [pc])

  return { items, isLoading, error }
}

/** Submit dataset -> waits for receipt */
export function useSubmitDataset() {
  const pc = usePublicClient()
  const { writeContractAsync } = useWriteContract()

  const submit = async (args: {
    cid: string
    title: string
    tokenUri: string
    priceEther: string
    qualityScore: number
    tokenGated?: boolean
    minTokenForBuy?: string
    minStakeForBuy?: string
  }) => {
    if (!pc) throw new Error("Public client not ready")
    const hash = await writeContractAsync({
      address: ADDR.DATA_DAO,
      abi: DATA_DAO_ABI,
      functionName: "submitDataset",
      args: [
        args.cid,
        args.title,
        args.tokenUri,
        parseUnits(args.priceEther || "0", 18),
        args.qualityScore,
        Boolean(args.tokenGated ?? false),
        BigInt(args.minTokenForBuy ?? "0"),
        BigInt(args.minStakeForBuy ?? "0"),
      ],
    })
    return pc.waitForTransactionReceipt({ hash })
  }

  return { submit }
}

/** Approve + purchase flow (each waits for receipt) */
export function usePurchase(datasetId: bigint) {
  const pc = usePublicClient()
  const { address } = useAccount()
  const { writeContractAsync } = useWriteContract()

  const paymentToken = ADDR.LSDC

  const approve = async (amount: bigint) => {
    if (!pc) throw new Error("Public client not ready")
    const hash = await writeContractAsync({
      address: paymentToken,
      abi: ERC20_ABI,
      functionName: "approve",
      args: [ADDR.DATA_DAO, amount],
    })
    return pc.waitForTransactionReceipt({ hash })
  }

  const buy = async () => {
    if (!pc) throw new Error("Public client not ready")
    const hash = await writeContractAsync({
      address: ADDR.DATA_DAO,
      abi: DATA_DAO_ABI,
      functionName: "purchase",
      args: [datasetId],
    })
    return pc.waitForTransactionReceipt({ hash })
  }

  return { approve, buy, address }
}
