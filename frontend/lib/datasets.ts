// lib/datasets.ts
"use client"

export type LighthouseItem = {
  id?: string | number
  fileName?: string
  cid: string
  fileSizeInBytes?: number | string
  createdAt?: string | number
  mimeType?: string
  publicKey?: string
}

export function lighthouseCidUrl(cid?: string) {
  return cid ? `https://gateway.lighthouse.storage/ipfs/${cid}` : "#"
}

export function formatBytes(bytes: number) {
  if (!bytes) return "0 B"
  const k = 1024
  const sizes = ["B", "KB", "MB", "GB", "TB"]
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

export function toDateStr(ts?: string | number) {
  if (!ts) return ""
  const d = new Date(ts)
  if (isNaN(d.getTime())) return ""
  return d.toISOString().slice(0, 10)
}

export function mapLighthouseToCard(item: LighthouseItem) {
  const sizeNum = Number(item.fileSizeInBytes ?? 0)
  return {
    id: String(item.id ?? item.cid),
    title: item.fileName || "Untitled file",
    description: `CID: ${item.cid}`,
    category: item.mimeType || "All Categories",
    tags: [],
    contributor: { name: item.publicKey?.slice(0, 10) || "Uploader", verified: true },
    qualityScore: 80,
    price: 0, // Lighthouse files: free to open
    downloads: 0,
    uploadDate: toDateStr(item.createdAt),
    fileSize: formatBytes(sizeNum),
    fileType: item.mimeType || "file",
    cid: item.cid,
    url: lighthouseCidUrl(item.cid),
  }
}
