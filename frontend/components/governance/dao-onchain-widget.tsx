"use client"

import { Card, CardContent } from "@/components/ui/card"
import { useReadContract } from "wagmi"
import { ADDR, DATA_DAO_ABI } from "@/lib/contracts"

export function DaoOnchainWidget() {
  const next = useReadContract({
    address: ADDR.DATA_DAO,
    abi: DATA_DAO_ABI,
    functionName: "nextDatasetId",
  })
  return (
    <Card className="border-primary/20 bg-primary/5">
      <CardContent className="p-4 flex items-center justify-between">
        <div>
          <div className="text-sm text-muted-foreground">On-chain datasets submitted</div>
          <div className="text-2xl font-bold">{Number(next.data ?? 0).toLocaleString()}</div>
        </div>
        <div className="text-xs text-muted-foreground">
          Contract: <span className="font-mono">{ADDR.DATA_DAO.slice(0,6)}…{ADDR.DATA_DAO.slice(-4)}</span>
        </div>
      </CardContent>
    </Card>
  )
}
