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

/** Upload page helper – wraps the submitDataset hook cleanly */
export function useSubmitFlow() {
  const { submit } = useSubmitDataset()

  async function submitNow(args: {
    cid: string
    title: string
    tokenUri: string
    price: number
    qualityScore: number
  }) {
    await submit({
      cid: args.cid,
      title: args.title,
      tokenUri: args.tokenUri || `ipfs://${args.cid}`,
      priceEther: String(args.price ?? 0),
      qualityScore: Math.round(args.qualityScore ?? 80),
      tokenGated: false,
      minTokenForBuy: "0",
      minStakeForBuy: "0",
    })
    return true
  }

  return { submitNow }
}
