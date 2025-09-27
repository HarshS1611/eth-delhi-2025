"use client"

import { useState } from "react"
import { Header } from "@/components/global/header"
import { ProposalCard } from "@/components/governance/proposal-card"
import { CreateProposalModal } from "@/components/governance/create-proposal-modal"
import { GovernanceStats } from "@/components/governance/governance-stats"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useToast } from "@/hooks/use-toast"
import { Plus, Vote } from "lucide-react"

// Mock proposals data
const mockProposals = [
  {
    id: "1",
    title: "Implement AI Quality Score Threshold of 85%",
    description:
      "Proposal to set a minimum AI quality score of 85% for all datasets uploaded to the marketplace. This will ensure higher data quality and improve user trust in the platform.",
    proposer: {
      name: "DataQuality Labs",
      address: "0x1234...5678",
      verified: true,
    },
    status: "active" as const,
    category: "platform" as const,
    votesFor: 8930,
    votesAgainst: 2140,
    totalVotes: 11070,
    quorum: 11070,
    requiredQuorum: 15000,
    endDate: "2024-01-25",
    createdDate: "2024-01-18",
    hasVoted: false,
  },
  {
    id: "2",
    title: "Allocate 500K LSDC for Marketing Campaign",
    description:
      "Proposal to allocate 500,000 LSDC from the DAO treasury for a comprehensive marketing campaign to increase platform adoption and attract more data contributors.",
    proposer: {
      name: "Growth Committee",
      address: "0xabcd...efgh",
      verified: true,
    },
    status: "active" as const,
    category: "treasury" as const,
    votesFor: 12450,
    votesAgainst: 8920,
    totalVotes: 21370,
    quorum: 21370,
    requiredQuorum: 18500,
    endDate: "2024-01-27",
    createdDate: "2024-01-20",
    hasVoted: true,
    userVote: "for" as const,
  },
  {
    id: "3",
    title: "Reduce Platform Fees from 5% to 4%",
    description:
      "Proposal to reduce the platform fee from 5% to 4% to make the marketplace more competitive and attract more contributors. This would increase contributor earnings while maintaining platform sustainability.",
    proposer: {
      name: "Community Council",
      address: "0x9876...5432",
      verified: true,
    },
    status: "passed" as const,
    category: "platform" as const,
    votesFor: 15420,
    votesAgainst: 4580,
    totalVotes: 20000,
    quorum: 20000,
    requiredQuorum: 15000,
    endDate: "2024-01-15",
    createdDate: "2024-01-08",
    hasVoted: true,
    userVote: "for" as const,
  },
  {
    id: "4",
    title: "Upgrade Smart Contract to V2.0",
    description:
      "Technical proposal to upgrade the main platform smart contract to version 2.0, which includes gas optimizations, security improvements, and new features for better user experience.",
    proposer: {
      name: "Tech Team",
      address: "0xtech...1234",
      verified: true,
    },
    status: "active" as const,
    category: "technical" as const,
    votesFor: 6780,
    votesAgainst: 1230,
    totalVotes: 8010,
    quorum: 8010,
    requiredQuorum: 12000,
    endDate: "2024-01-30",
    createdDate: "2024-01-23",
    hasVoted: false,
  },
]

export default function GovernancePage() {
  const { toast } = useToast()
  const [proposals, setProposals] = useState(mockProposals)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [activeTab, setActiveTab] = useState("proposals")

  const handleVote = (proposalId: string, vote: "for" | "against") => {
    setProposals((prev) =>
      prev.map((proposal) => {
        if (proposal.id === proposalId) {
          const newVotesFor = proposal.votesFor + (vote === "for" ? 1500 : 0) // Simulate user's voting power
          const newVotesAgainst = proposal.votesAgainst + (vote === "against" ? 1500 : 0)
          return {
            ...proposal,
            votesFor: newVotesFor,
            votesAgainst: newVotesAgainst,
            totalVotes: newVotesFor + newVotesAgainst,
            quorum: newVotesFor + newVotesAgainst,
            hasVoted: true,
            userVote: vote,
          }
        }
        return proposal
      }),
    )

    toast({
      title: "Vote cast successfully!",
      description: `Your vote ${vote.toUpperCase()} has been recorded on the blockchain.`,
    })
  }

  const handleCreateProposal = (proposalData: {
    title: string
    description: string
    category: string
    duration: number
  }) => {
    const newProposal = {
      id: (proposals.length + 1).toString(),
      title: proposalData.title,
      description: proposalData.description,
      proposer: {
        name: "You",
        address: "0xyour...address",
        verified: true,
      },
      status: "active" as const,
      category: proposalData.category as "platform" | "treasury" | "technical" | "governance",
      votesFor: 0,
      votesAgainst: 0,
      totalVotes: 0,
      quorum: 0,
      requiredQuorum: 15000,
      endDate: new Date(Date.now() + proposalData.duration * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
      createdDate: new Date().toISOString().split("T")[0],
      hasVoted: false,
    }

    setProposals((prev) => [newProposal, ...prev])
  }

  const activeProposals = proposals.filter((p) => p.status === "active")
  const completedProposals = proposals.filter((p) => p.status === "passed" || p.status === "rejected")

  return (
    <div className="min-h-screen">
      <Header />
      <main className="container py-8">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
            DAO{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Governance</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Participate in decentralized governance by voting on proposals that shape the future of the D³ Data DAO
            platform. Your voting power is determined by your staked DataCoin tokens.
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
          <div className="flex items-center justify-between">
            <TabsList className="grid w-auto grid-cols-2">
              <TabsTrigger value="proposals">Proposals</TabsTrigger>
              <TabsTrigger value="stats">Statistics</TabsTrigger>
            </TabsList>

            <Button
              onClick={() => setIsCreateModalOpen(true)}
              className="bg-gradient-to-r from-primary to-accent hover:opacity-90"
            >
              <Plus className="mr-2 h-4 w-4" />
              Create Proposal
            </Button>
          </div>

          <TabsContent value="proposals" className="space-y-8">
            {/* Active Proposals */}
            <div className="space-y-6">
              <div className="flex items-center space-x-2">
                <Vote className="h-5 w-5 text-primary" />
                <h2 className="text-xl font-semibold">Active Proposals ({activeProposals.length})</h2>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {activeProposals.map((proposal) => (
                  <ProposalCard key={proposal.id} proposal={proposal} onVote={handleVote} />
                ))}
              </div>

              {activeProposals.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-muted-foreground">No active proposals at the moment.</p>
                </div>
              )}
            </div>

            {/* Completed Proposals */}
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">Recent Decisions ({completedProposals.length})</h2>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {completedProposals.slice(0, 4).map((proposal) => (
                  <ProposalCard key={proposal.id} proposal={proposal} onVote={handleVote} />
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="stats" className="space-y-6">
            <GovernanceStats />
          </TabsContent>
        </Tabs>
      </main>

      <CreateProposalModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateProposal}
      />
    </div>
  )
}
