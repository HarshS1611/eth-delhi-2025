"use client"

import type { Dataset } from "@/components/marketplace/dataset-card"
import { listUploads } from "./lightHouse"
import { useSubmitDataset } from "./dao"

const fmtBytes = (bytes?: string | number) => {
  const num = typeof bytes === "string" ? Number(bytes) : bytes ?? 0
  if (!num || Number.isNaN(num)) return "-"
  const k = 1024
  const sizes = ["B", "KB", "MB", "GB", "TB"]
  const i = Math.floor(Math.log(num) / Math.log(k))
  return `${(num / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

const toDateStr = (ts?: string | number) => {
  if (!ts) return ""
  const d = new Date(ts)
  return Number.isNaN(d.getTime()) ? "" : d.toISOString().slice(0, 10)
}

export async function fetchLighthouseCards(lastKey: string | null = null): Promise<Dataset[]> {
  const resp: any = await listUploads()
  const fileList = resp?.data?.fileList ?? []

  const mapped: Dataset[] = fileList.map((f: any) => ({
    id: f.id ?? f.cid,
    title: f.fileName || f.cid,
    description: `CID: ${f.cid}`,
    category: "IPFS",
    tags: [],
    contributor: { name: f.publicKey?.slice(0, 10) || "Uploader", verified: !f.encryption },
    qualityScore: 80,
    price: 0,
    downloads: 0,
    uploadDate: toDateStr(f.createdAt),
    fileSize: fmtBytes(f.fileSizeInBytes),
    fileType: f.mimeType || "File",
    cid: f.cid,
    source: "ipfs",
  }))

  return mapped
}


import { useWriteContract } from "wagmi"
import { parseUnits } from "viem"
import { ADDR, DATA_DAO_ABI } from "@/lib/contracts"
import { useTokenInfo } from "@/lib/token"
import { pub } from "@/lib/dao"

type SubmitArgs = {
  cid: string
  title: string
  tokenUri: string          // ipfs://CID of ERC-721 metadata JSON
  price: number | string    // human units (e.g., 42.5)
  qualityScore: number      // 0..100 (uint8 safe)
  tokenGated?: boolean
  minTokenForBuy?: number | string  // DIP units (human)
  minStakeForBuy?: number | string  // DIP units (human)
}


/** Upload page helper – wraps the submitDataset hook cleanly */
export function useSubmitFlow() {
  const { writeContractAsync } = useWriteContract()
  // payment token = LSDC; DIP has 18d as well
  const { decimals: lsdDecimals = 18 } = useTokenInfo(ADDR.LSDC)

  async function submitNow(input: SubmitArgs) {
    const priceWei = parseUnits(String(input.price ?? 0), lsdDecimals)
    const q = Math.max(0, Math.min(255, Math.floor(input.qualityScore ?? 0))) // uint8 safe

    // DIP uses 18 decimals. If you changed DIP decimals, adjust here.
    const to18 = (x: number | string | undefined) => parseUnits(String(x ?? 0), 18)

    const hash = await writeContractAsync({
      address: ADDR.DATA_DAO,
      abi: DATA_DAO_ABI,
      functionName: "submitDataset",
      args: [
        input.cid,
        input.title,
        input.tokenUri,
        priceWei,
        q,
        Boolean(input.tokenGated),
        to18(input.minTokenForBuy),
        to18(input.minStakeForBuy),
      ],
    })

    await pub.waitForTransactionReceipt({ hash })
    return hash
  }

  return { submitNow }
}