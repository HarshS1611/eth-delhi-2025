"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { useToast } from "@/hooks/use-toast"
import { Vote, Clock, Users, CheckCircle, XCircle, AlertCircle } from "lucide-react"

interface Proposal {
  id: string
  title: string
  description: string
  proposer: {
    name: string
    address: string
    verified: boolean
  }
  status: "active" | "passed" | "rejected" | "pending"
  category: "platform" | "treasury" | "technical" | "governance"
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

interface ProposalCardProps {
  proposal: Proposal
  onVote: (proposalId: string, vote: "for" | "against") => void
}

const categoryConfig = {
  platform: { label: "Platform", color: "bg-primary/10 text-primary" },
  treasury: { label: "Treasury", color: "bg-accent/10 text-accent" },
  technical: { label: "Technical", color: "bg-chart-2/10 text-chart-2" },
  governance: { label: "Governance", color: "bg-chart-3/10 text-chart-3" },
}

const statusConfig = {
  active: { label: "Active", color: "bg-green-500/10 text-green-500", icon: Clock },
  passed: { label: "Passed", color: "bg-blue-500/10 text-blue-500", icon: CheckCircle },
  rejected: { label: "Rejected", color: "bg-red-500/10 text-red-500", icon: XCircle },
  pending: { label: "Pending", color: "bg-yellow-500/10 text-yellow-500", icon: AlertCircle },
}

export function ProposalCard({ proposal, onVote }: ProposalCardProps) {
  const { toast } = useToast()
  const categoryStyle = categoryConfig[proposal.category]
  const statusStyle = statusConfig[proposal.status]
  const StatusIcon = statusStyle.icon

  const votePercentageFor = proposal.totalVotes > 0 ? (proposal.votesFor / proposal.totalVotes) * 100 : 0
  const votePercentageAgainst = proposal.totalVotes > 0 ? (proposal.votesAgainst / proposal.totalVotes) * 100 : 0
  const quorumPercentage = (proposal.quorum / proposal.requiredQuorum) * 100

  const timeRemaining = new Date(proposal.endDate).getTime() - new Date().getTime()
  const daysRemaining = Math.max(0, Math.ceil(timeRemaining / (1000 * 60 * 60 * 24)))

  const handleVote = (vote: "for" | "against") => {
    if (proposal.hasVoted) {
      toast({
        title: "Already voted",
        description: "You have already cast your vote on this proposal.",
        variant: "destructive",
      })
      return
    }

    if (proposal.status !== "active") {
      toast({
        title: "Voting closed",
        description: "This proposal is no longer accepting votes.",
        variant: "destructive",
      })
      return
    }

    onVote(proposal.id, vote)
  }

  return (
    <Card className="hover:shadow-lg transition-all duration-300 border-border/40 bg-card/50 backdrop-blur hover:bg-card/80">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <Badge variant="outline" className={categoryStyle.color}>
                {categoryStyle.label}
              </Badge>
              <Badge variant="outline" className={statusStyle.color}>
                <StatusIcon className="mr-1 h-3 w-3" />
                {statusStyle.label}
              </Badge>
            </div>
            <CardTitle className="text-lg mb-2 line-clamp-2">{proposal.title}</CardTitle>
            <p className="text-sm text-muted-foreground line-clamp-3 mb-4">{proposal.description}</p>
          </div>
        </div>

        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-2">
            <Avatar className="h-6 w-6">
              <AvatarFallback className="text-xs">{proposal.proposer.name.charAt(0)}</AvatarFallback>
            </Avatar>
            <span className="text-muted-foreground">by {proposal.proposer.name}</span>
          </div>
          <div className="flex items-center space-x-1 text-muted-foreground">
            <Clock className="h-3 w-3" />
            <span>{daysRemaining}d remaining</span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Voting Results */}
        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Votes For</span>
            <span className="font-medium text-green-500">
              {proposal.votesFor.toLocaleString()} ({votePercentageFor.toFixed(1)}%)
            </span>
          </div>
          <Progress value={votePercentageFor} className="h-2 bg-muted" />

          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Votes Against</span>
            <span className="font-medium text-red-500">
              {proposal.votesAgainst.toLocaleString()} ({votePercentageAgainst.toFixed(1)}%)
            </span>
          </div>
          <Progress value={votePercentageAgainst} className="h-2 bg-muted" />
        </div>

        {/* Quorum Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Quorum Progress</span>
            <span className="font-medium">
              {proposal.quorum.toLocaleString()} / {proposal.requiredQuorum.toLocaleString()}
            </span>
          </div>
          <Progress value={quorumPercentage} className="h-2" />
          <div className="text-xs text-muted-foreground">
            {quorumPercentage >= 100 ? (
              <span className="text-green-500">✓ Quorum reached</span>
            ) : (
              <span>{(100 - quorumPercentage).toFixed(1)}% more needed</span>
            )}
          </div>
        </div>

        {/* Voting Actions */}
        {proposal.status === "active" && (
          <div className="flex space-x-2 pt-2">
            {proposal.hasVoted ? (
              <div className="flex items-center justify-center w-full py-2 text-sm text-muted-foreground">
                <Vote className="mr-2 h-4 w-4" />
                You voted {proposal.userVote?.toUpperCase()}
              </div>
            ) : (
              <>
                <Button
                  onClick={() => handleVote("for")}
                  variant="outline"
                  className="flex-1 border-green-500/20 hover:bg-green-500/10 hover:text-green-500"
                >
                  <CheckCircle className="mr-2 h-4 w-4" />
                  Vote For
                </Button>
                <Button
                  onClick={() => handleVote("against")}
                  variant="outline"
                  className="flex-1 border-red-500/20 hover:bg-red-500/10 hover:text-red-500"
                >
                  <XCircle className="mr-2 h-4 w-4" />
                  Vote Against
                </Button>
              </>
            )}
          </div>
        )}

        {/* Additional Info */}
        <div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t">
          <div className="flex items-center space-x-1">
            <Users className="h-3 w-3" />
            <span>{proposal.totalVotes.toLocaleString()} total votes</span>
          </div>
          <span>Created {proposal.createdDate}</span>
        </div>
      </CardContent>
    </Card>
  )
}
