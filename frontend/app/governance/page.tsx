"use client"

import { useEffect, useMemo, useState } from "react"
import { useAccount, useWriteContract } from "wagmi"
import { Header } from "@/components/global/header"
import { ProposalCard } from "@/components/governance/proposal-card"
import { GovernanceStats } from "@/components/governance/governance-stats"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useToast } from "@/hooks/use-toast"
import { Plus, Vote } from "lucide-react"
import { DaoOnchainWidget } from "@/components/governance/dao-onchain-widget"
import { Button } from "@/components/ui/button"
import { ADDR, DATA_DAO_ABI } from "@/lib/contracts"
import { pub } from "@/lib/dao"       
import { shapeDataset, statusFromEnum, type ShapedDataset } from "@/lib/shapers"
import { useRouter } from "next/navigation"

type UiProposal = {
  id: string
  title: string
  description: string
  proposer: { name: string; address: string; verified: boolean }
  status: "active" | "passed" | "rejected" | "pending"
  category: "governance"
  votesFor: number
  votesAgainst: number
  totalVotes: number
  quorum: number
  requiredQuorum: number
  endDate: string
  createdDate: string
  hasVoted: boolean
}

function short(addr: string) {
  return addr ? `${addr.slice(0,6)}…${addr.slice(-4)}` : ""
}

export default function GovernancePage() {
  const router = useRouter()
  const { address } = useAccount()
  const { toast } = useToast()
  const write = useWriteContract()

  const [loading, setLoading] = useState(false)
  const [items, setItems] = useState<ShapedDataset[]>([])
  const [requiredQuorum, setRequiredQuorum] = useState<number>(1)

  async function load() {
    setLoading(true)
    try {
      const nextId = (await pub.readContract({
        address: ADDR.DATA_DAO,
        abi: DATA_DAO_ABI,
        functionName: "nextDatasetId",
      })) as bigint

      const req = (await pub.readContract({
        address: ADDR.DATA_DAO,
        abi: DATA_DAO_ABI,
        functionName: "approvalVotes",
      })) as bigint
      setRequiredQuorum(Number(req))

      const count = Number(nextId - 1n)
      if (count <= 0) { setItems([]); return }

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
      setItems(rows)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  // For each dataset, check if this user has voted
  const [votedMap, setVotedMap] = useState<Record<string, boolean>>({})
  useEffect(() => {
    let alive = true
    if (!address || items.length === 0) { setVotedMap({}); return }
    (async () => {
      const out: Record<string, boolean> = {}
      await Promise.all(items.map(async (it) => {
        const hv = await pub.readContract({
          address: ADDR.DATA_DAO,
          abi: DATA_DAO_ABI,
          functionName: "hasVoted",
          args: [BigInt(it.id), address as `0x${string}`],
        }) as boolean
        out[it.id] = hv
      }))
      if (alive) setVotedMap(out)
    })()
    return () => { alive = false }
  }, [address, items])

  const proposals: UiProposal[] = useMemo(() => {
    return items.map((d) => {
      const status =
        d.status === "approved" ? "passed" :
        d.status === "rejected" ? "rejected" :
        d.status === "paused"   ? "pending" : "active"

      return {
        id: d.id,
        title: d.title,
        description: d.tokenUri || `CID: ${d.cid}`,
        proposer: { name: short(d.creator), address: d.creator, verified: true },
        status,
        category: "governance",
        votesFor: d.votes,     // DAO stores approvals
        votesAgainst: 0,
        totalVotes: d.votes,
        quorum: d.votes,
        requiredQuorum,
        endDate: "",
        createdDate: "",
        hasVoted: !!votedMap[d.id],
      }
    })
  }, [items, votedMap, requiredQuorum])

  const activeProposals = proposals.filter(p => p.status === "active")
  const completedProposals = proposals.filter(p => p.status === "passed" || p.status === "rejected")

  async function onVote(proposalId: string, vote: "for" | "against") {
    try {
      // Contract only tracks approvals; ignore "against" on-chain
      const approve = (vote === "for")

      const hash = await write.writeContractAsync({
        address: ADDR.DATA_DAO,
        abi: DATA_DAO_ABI,
        functionName: "vote",
        args: [BigInt(proposalId), approve],
      })
      await pub.waitForTransactionReceipt({ hash })
      toast({ title: "Vote cast!", description: approve ? "Approved" : "Recorded (against ignored on-chain)" })
      await load()
    } catch (e: any) {
      toast({ title: "Vote failed", description: String(e?.message || e), variant: "destructive" })
    }
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main className="container py-8">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
            DAO <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Governance</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Datasets are proposals. Vote to approve them.
          </p>
        </div>

        <div className="mb-6"><DaoOnchainWidget /></div>

        <Tabs defaultValue="proposals" className="space-y-8">
          <div className="flex items-center justify-between">
            <TabsList className="grid w-auto grid-cols-2">
              <TabsTrigger value="proposals">Proposals</TabsTrigger>
              <TabsTrigger value="stats">Statistics</TabsTrigger>
            </TabsList>
            <Button
              onClick={() => router.push("/upload")}
              className="bg-gradient-to-r from-primary to-accent hover:opacity-90"
            >
              <Plus className="mr-2 h-4 w-4" /> Create Proposal
            </Button>
          </div>

          <TabsContent value="proposals" className="space-y-8">
            {loading && <div className="text-center py-6 text-muted-foreground">Loading on-chain proposals…</div>}

            <div className="space-y-6">
              <div className="flex items-center space-x-2">
                <Vote className="h-5 w-5 text-primary" />
                <h2 className="text-xl font-semibold">Active Proposals ({activeProposals.length})</h2>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {activeProposals.map((p) => (
                  <ProposalCard key={p.id} proposal={p as any} onVote={onVote} />
                ))}
              </div>

              {activeProposals.length === 0 && !loading && (
                <div className="text-center py-12">
                  <p className="text-muted-foreground">No active proposals.</p>
                </div>
              )}
            </div>

            <div className="space-y-6">
              <h2 className="text-xl font-semibold">Recent Decisions ({completedProposals.length})</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {completedProposals.slice(0, 4).map((p) => (
                  <ProposalCard key={p.id} proposal={p as any} onVote={onVote} />
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="stats" className="space-y-6">
            <GovernanceStats />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
