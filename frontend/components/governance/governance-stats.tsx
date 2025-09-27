import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Vote, Users, TrendingUp, Clock, CheckCircle, XCircle } from "lucide-react"

const governanceStats = {
  totalProposals: 47,
  activeProposals: 5,
  passedProposals: 32,
  rejectedProposals: 10,
  totalVoters: 1847,
  averageParticipation: 68.5,
  totalVotingPower: 18500000,
  quorumThreshold: 1850000,
}

const recentActivity = [
  {
    type: "passed",
    title: "Reduce Platform Fees to 4%",
    votes: 15420,
    date: "2 days ago",
  },
  {
    type: "active",
    title: "Implement AI Quality Threshold",
    votes: 8930,
    date: "5 days remaining",
  },
  {
    type: "rejected",
    title: "Increase Staking Rewards by 5%",
    votes: 12100,
    date: "1 week ago",
  },
]

export function GovernanceStats() {
  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6 text-center">
            <div className="inline-flex rounded-full bg-primary/10 p-3 mb-4">
              <Vote className="h-6 w-6 text-primary" />
            </div>
            <div className="text-2xl font-bold">{governanceStats.totalProposals}</div>
            <div className="text-sm text-muted-foreground">Total Proposals</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <div className="inline-flex rounded-full bg-primary/10 p-3 mb-4">
              <Users className="h-6 w-6 text-primary" />
            </div>
            <div className="text-2xl font-bold">{governanceStats.totalVoters.toLocaleString()}</div>
            <div className="text-sm text-muted-foreground">Active Voters</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <div className="inline-flex rounded-full bg-chart-2/10 p-3 mb-4">
              <TrendingUp className="h-6 w-6 text-chart-2" />
            </div>
            <div className="text-2xl font-bold">{governanceStats.averageParticipation}%</div>
            <div className="text-sm text-muted-foreground">Avg Participation</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <div className="inline-flex rounded-full bg-chart-3/10 p-3 mb-4">
              <Clock className="h-6 w-6 text-chart-3" />
            </div>
            <div className="text-2xl font-bold">{governanceStats.activeProposals}</div>
            <div className="text-sm text-muted-foreground">Active Proposals</div>
          </CardContent>
        </Card>
      </div>

      {/* Proposal Status Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-green-500/20 bg-green-500/5">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Passed</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500 mb-1">{governanceStats.passedProposals}</div>
            <div className="text-sm text-muted-foreground">
              {((governanceStats.passedProposals / governanceStats.totalProposals) * 100).toFixed(1)}% success rate
            </div>
          </CardContent>
        </Card>

        <Card className="border-red-500/20 bg-red-500/5">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center space-x-2">
              <XCircle className="h-4 w-4 text-red-500" />
              <span>Rejected</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500 mb-1">{governanceStats.rejectedProposals}</div>
            <div className="text-sm text-muted-foreground">
              {((governanceStats.rejectedProposals / governanceStats.totalProposals) * 100).toFixed(1)}% rejection rate
            </div>
          </CardContent>
        </Card>

        <Card className="border-yellow-500/20 bg-yellow-500/5">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center space-x-2">
              <Clock className="h-4 w-4 text-yellow-500" />
              <span>Active</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-500 mb-1">{governanceStats.activeProposals}</div>
            <div className="text-sm text-muted-foreground">Currently voting</div>
          </CardContent>
        </Card>
      </div>

      {/* Voting Power Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Voting Power Distribution</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Total Voting Power</span>
                <span className="font-medium">{(governanceStats.totalVotingPower / 1000000).toFixed(1)}M DataCoin</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Quorum Threshold</span>
                <span className="font-medium">{(governanceStats.quorumThreshold / 1000000).toFixed(1)}M DataCoin</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Active Voters</span>
                <span className="font-medium">{governanceStats.totalVoters.toLocaleString()}</span>
              </div>
            </div>

            <div className="space-y-3">
              <div className="text-sm font-medium">Tier Distribution</div>
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Diamond (3x power)</span>
                  <span>12% of voters</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Gold (2x power)</span>
                  <span>28% of voters</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Silver (1.5x power)</span>
                  <span>35% of voters</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Bronze (1x power)</span>
                  <span>25% of voters</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivity.map((activity, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg border border-border/40">
                <div className="flex items-center space-x-3">
                  {activity.type === "passed" && <CheckCircle className="h-4 w-4 text-green-500" />}
                  {activity.type === "active" && <Clock className="h-4 w-4 text-yellow-500" />}
                  {activity.type === "rejected" && <XCircle className="h-4 w-4 text-red-500" />}
                  <div>
                    <div className="font-medium text-sm">{activity.title}</div>
                    <div className="text-xs text-muted-foreground">{activity.votes.toLocaleString()} votes</div>
                  </div>
                </div>
                <div className="text-right">
                  <Badge
                    variant={
                      activity.type === "passed" ? "default" : activity.type === "active" ? "secondary" : "destructive"
                    }
                    className="text-xs"
                  >
                    {activity.type}
                  </Badge>
                  <div className="text-xs text-muted-foreground mt-1">{activity.date}</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
