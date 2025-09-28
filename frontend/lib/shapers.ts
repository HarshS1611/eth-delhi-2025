import type { Abi } from "viem"

export type DatasetStatus = "pending" | "approved" | "rejected" | "paused"

export function statusFromEnum(n: number): DatasetStatus {
  switch (n) {
    case 1: return "approved"
    case 2: return "rejected"
    case 3: return "paused"
    default: return "pending"
  }
}

// name-or-index safe accessor
export function pick<T = any>(obj: any, name: string, index: number, fallback?: T): T {
  const byName = obj?.[name]
  const byIdx = obj?.[index]
  return (byName !== undefined ? byName : (byIdx !== undefined ? byIdx : fallback)) as T
}

export type ShapedDataset = {
  id: string
  cid: string
  title: string
  tokenUri: string
  creator: `0x${string}`
  priceWei: bigint
  price: number 
  qualityScore: number
  status: DatasetStatus
  votes: number
  tokenGated: boolean
  minTokenForBuy: bigint
  minStakeForBuy: bigint
  raw: any
}

const ONE_E18 = 1e18

export function shapeDataset(id: bigint, d: any): ShapedDataset {
  const cid          = String(pick(d, "cid",           0, ""))
  const title        = String(pick(d, "title",         1, `Dataset #${id}`))
  const tokenUri     = String(pick(d, "tokenUri",      2, ""))
  const creator      = String(pick(d, "creator",       3, "0x0000000000000000000000000000000000000000")) as `0x${string}`
  const priceWei     = pick<bigint>(d, "price",        4, 0n)
  const qualityScore = Number(pick<number>(d, "qualityScore", 5, 0))
  const statusNum    = Number(pick<number>(d, "status", 6, 0))
  const votesBn      = pick<bigint>(d, "votes",        7, 0n)
  const tokenGated   = Boolean(pick(d, "tokenGated",   8, false))
  const minToken     = pick<bigint>(d, "minTokenForBuy", 9, 0n)
  const minStake     = pick<bigint>(d, "minStakeForBuy",10, 0n)

  return {
    id: id.toString(),
    cid,
    title,
    tokenUri,
    creator,
    priceWei,
    price: Number(priceWei) / ONE_E18,
    qualityScore,
    status: statusFromEnum(statusNum),
    votes: Number(votesBn),
    tokenGated,
    minTokenForBuy: minToken,
    minStakeForBuy: minStake,
    raw: d,
  }
}
