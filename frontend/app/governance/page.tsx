// app/governance/page.tsx
"use client"

import { useEffect, useMemo, useState } from "react"
import { useAccount, usePublicClient, useWriteContract } from "wagmi"
import { Header } from "@/components/global/header"
import { ProposalCard } from "@/components/governance/proposal-card"
import { GovernanceStats } from "@/components/governance/governance-stats"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { Plus, Vote } from "lucide-react"
import Link from "next/link"

import { ADDR, DATA_DAO_ABI } from "@/lib/contracts"

type Status = "active" | "passed" | "rejected" | "pending"
type Category = "platform" | "treasury" | "technical" | "governance"

type UiProposal = {
  id: string
  title: string
  description: string
  proposer: { name: string; address: string; verified: boolean }
  status: Status
  category: Category
  votesFor: number
  votesAgainst: number
  totalVotes: number
  quorum: number
  requiredQuorum: number
  endDate: string
  createdDate: string
  hasVoted: boolean
  userVote?: "for" | "against"
}

function short(addr: string) {
  return addr ? `${addr.slice(0, 6)}…${addr.slice(-4)}` : "-"
}

function statusFromEnum(val: number): Status {
  // DIPDataDAO.Status { Pending(0), Approved(1), Rejected(2), Paused(3) }
  if (val === 0) return "active"   // Pending → voting open
  if (val === 1) return "passed"   // Approved
  if (val === 2) return "rejected" // Rejected
  if (val === 3) return "pending"  // Paused (not open for voting)
  return "active"
}

export default function GovernancePage() {
  const { address } = useAccount()
  const client = usePublicClient()
  const { toast } = useToast()

  const { writeContractAsync } = useWriteContract()

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [proposals, setProposals] = useState<UiProposal[]>([])
  const [activeTab, setActiveTab] = useState("proposals")
  const [pendingVoteIds, setPendingVoteIds] = useState<Record<string, boolean>>({})
  const [refreshKey, setRefreshKey] = useState(0)

  // Fetch datasets as proposals
  useEffect(() => {
    let alive = true
    async function run() {
      if (!client) return
      setLoading(true)
      setError(null)
      try {
        // 1) Get current quorum target (approvalVotes)
        const requiredQuorumBn = (await client.readContract({
          address: ADDR.DATA_DAO,
          abi: DATA_DAO_ABI,
          functionName: "approvalVotes",
        })) as bigint
        const requiredQuorum = Number(requiredQuorumBn ?? 1n)

        // 2) Determine id range: 1..nextDatasetId-1
        const nextIdBn = (await client.readContract({
          address: ADDR.DATA_DAO,
          abi: DATA_DAO_ABI,
          functionName: "nextDatasetId",
        })) as bigint

        const nextId = Number(nextIdBn ?? 1n)
        const maxId = Math.max(0, nextId - 1)
        if (maxId === 0) {
          if (alive) setProposals([])
          return
        }

        const ids = Array.from({ length: maxId }, (_, i) => BigInt(i + 1))

        // 3) Read datasets (and hasVoted for current wallet)
        const rows = await Promise.all(
          ids.map(async (id) => {
            const d: any = await client.readContract({
              address: ADDR.DATA_DAO,
              abi: DATA_DAO_ABI,
              functionName: "datasets",
              args: [id],
            })

            console.log("d", d.votes)

            const votes = Number(d.votes ?? 0n)
            const status = statusFromEnum(Number(d.status ?? 0))
            const voterHasVoted =
              address
                ? ((await client.readContract({
                    address: ADDR.DATA_DAO,
                    abi: DATA_DAO_ABI,
                    functionName: "hasVoted",
                    args: [id, address as `0x${string}`],
                  })) as boolean)
                : false

            const p: UiProposal = {
              id: id.toString(),
              title: String(d.title || `Dataset #${id}`),
              description: d.tokenUri ? String(d.tokenUri) : `CID: ${String(d.cid || "")}`,
              proposer: { name: short(String(d.creator)), address: String(d.creator), verified: true },
              status,
              category: "governance",
              votesFor: votes,
              votesAgainst: 0,      // contract only stores approvals
              totalVotes: votes,     // same as votesFor
              quorum: votes,         // show progress against requiredQuorum
              requiredQuorum,        // from approvalVotes()
              endDate: "",           // not tracked on-chain
              createdDate: "",       // not tracked on-chain
              hasVoted: voterHasVoted,
            }
            return p
          })
        )

        if (alive) setProposals(rows)
      } catch (e: any) {
        if (alive) setError(String(e?.message || e))
      } finally {
        if (alive) setLoading(false)
      }
    }
    run()
    return () => {
      alive = false
    }
  }, [client, address, refreshKey])

  const activeProposals = useMemo(
    () => proposals.filter((p) => p.status === "active"),
    [proposals]
  )
  const completedProposals = useMemo(
    () => proposals.filter((p) => p.status === "passed" || p.status === "rejected"),
    [proposals]
  )

  // Send tx and wait properly
  async function castVote(datasetId: bigint, support: boolean) {
    if (!client) throw new Error("RPC client not ready")
    const hash = await writeContractAsync({
      address: ADDR.DATA_DAO,
      abi: DATA_DAO_ABI,
      functionName: "vote",
      args: [datasetId, support],
    })
    // Now the hash is defined; wait for inclusion
    await client.waitForTransactionReceipt({ hash })
  }

  const handleVote = async (proposalId: string, vote: "for" | "against") => {
    if (!address) {
      toast({ title: "Connect wallet", description: "Please connect your wallet to vote.", variant: "destructive" })
      return
    }

    setPendingVoteIds((m) => ({ ...m, [proposalId]: true }))
    try {
      await castVote(BigInt(proposalId), vote === "for")
      toast({ title: "Vote submitted", description: `Your vote ${vote.toUpperCase()} is on-chain.` })

      // refetch from chain
      setRefreshKey((x) => x + 1)

      // optimistic local bump (kept small, real state comes from refetch)
      setProposals((prev) =>
        prev.map((p) =>
          p.id === proposalId
            ? {
                ...p,
                hasVoted: true,
                userVote: vote,
                votesFor: p.votesFor + (vote === "for" ? 1 : 0),
                totalVotes: p.totalVotes + (vote === "for" ? 1 : 0),
                quorum: p.quorum + (vote === "for" ? 1 : 0),
              }
            : p
        )
      )
    } catch (e: any) {
      toast({
        title: "Voting failed",
        description: String(e?.shortMessage || e?.message || e) || "Transaction failed.",
        variant: "destructive",
      })
    } finally {
      setPendingVoteIds((m) => ({ ...m, [proposalId]: false }))
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
            Datasets are proposals. Vote to move high-quality data to “Approved”.
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
          <div className="flex items-center justify-between">
            <TabsList className="grid w-auto grid-cols-2">
              <TabsTrigger value="proposals">Proposals</TabsTrigger>
              <TabsTrigger value="stats">Statistics</TabsTrigger>
            </TabsList>

            {/* Creating proposals = uploading datasets */}
            <Link href="/upload">
              <Button className="bg-gradient-to-r from-primary to-accent hover:opacity-90">
                <Plus className="mr-2 h-4 w-4" /> Upload Dataset
              </Button>
            </Link>
          </div>

          <TabsContent value="proposals" className="space-y-8">
            {error && (
              <div className="text-sm text-red-500 border border-red-500/30 rounded-md p-3">
                {error}
              </div>
            )}

            {loading && proposals.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                Loading on-chain proposals…
              </div>
            ) : (
              <>
                <div className="space-y-6">
                  <div className="flex items-center space-x-2">
                    <Vote className="h-5 w-5 text-primary" />
                    <h2 className="text-xl font-semibold">
                      Active Proposals ({activeProposals.length})
                    </h2>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {activeProposals.map((proposal) => (
                      <ProposalCard
                        key={proposal.id}
                        proposal={{
                          ...proposal,
                          // while tx is pending, mark as voted to disable buttons
                          hasVoted: proposal.hasVoted || !!pendingVoteIds[proposal.id],
                        } as any}
                        onVote={handleVote}
                      />
                    ))}
                  </div>

                  {activeProposals.length === 0 && (
                    <div className="text-center py-12">
                      <p className="text-muted-foreground">No active proposals on-chain.</p>
                    </div>
                  )}
                </div>

                <div className="space-y-6">
                  <h2 className="text-xl font-semibold">
                    Recent Decisions ({completedProposals.length})
                  </h2>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {completedProposals.slice(0, 6).map((proposal) => (
                      <ProposalCard key={proposal.id} proposal={proposal as any} onVote={handleVote} />
                    ))}
                  </div>
                </div>
              </>
            )}
          </TabsContent>

          <TabsContent value="stats" className="space-y-6">
            <GovernanceStats />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
