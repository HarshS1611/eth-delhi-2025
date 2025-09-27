import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Coins, TrendingUp, Users, PieChart, ArrowUpRight, ArrowDownRight } from "lucide-react"

const tokenomicsData = {
  totalSupply: 100000000,
  circulatingSupply: 45000000,
  stakedTokens: 18500000,
  treasuryReserve: 25000000,
  currentPrice: 0.85,
  priceChange24h: 5.2,
  marketCap: 38250000,
  stakingRatio: 41.1,
}

const distributionData = [
  { label: "Community Rewards", percentage: 40, amount: 40000000, color: "bg-primary" },
  { label: "DAO Treasury", percentage: 25, amount: 25000000, color: "bg-accent" },
  { label: "Team & Advisors", percentage: 15, amount: 15000000, color: "bg-chart-2" },
  { label: "Ecosystem Development", percentage: 10, amount: 10000000, color: "bg-chart-3" },
  { label: "Public Sale", percentage: 10, amount: 10000000, color: "bg-chart-4" },
]

export function TokenomicsOverview() {
  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6 text-center">
            <div className="inline-flex rounded-full bg-primary/10 p-3 mb-4">
              <Coins className="h-6 w-6 text-primary" />
            </div>
            <div className="text-2xl font-bold">${tokenomicsData.currentPrice}</div>
            <div className="text-sm text-muted-foreground mb-2">D3 Token Price</div>
            <div className="flex items-center justify-center space-x-1">
              {tokenomicsData.priceChange24h > 0 ? (
                <ArrowUpRight className="h-3 w-3 text-green-500" />
              ) : (
                <ArrowDownRight className="h-3 w-3 text-red-500" />
              )}
              <span className={`text-xs ${tokenomicsData.priceChange24h > 0 ? "text-green-500" : "text-red-500"}`}>
                {Math.abs(tokenomicsData.priceChange24h)}% (24h)
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <div className="inline-flex rounded-full bg-accent/10 p-3 mb-4">
              <TrendingUp className="h-6 w-6 text-primary" />
            </div>
            <div className="text-2xl font-bold">${(tokenomicsData.marketCap / 1000000).toFixed(1)}M</div>
            <div className="text-sm text-muted-foreground">Market Cap</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <div className="inline-flex rounded-full bg-chart-2/10 p-3 mb-4">
              <Users className="h-6 w-6 text-chart-2" />
            </div>
            <div className="text-2xl font-bold">{(tokenomicsData.circulatingSupply / 1000000).toFixed(0)}M</div>
            <div className="text-sm text-muted-foreground">Circulating Supply</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <div className="inline-flex rounded-full bg-chart-3/10 p-3 mb-4">
              <PieChart className="h-6 w-6 text-chart-3" />
            </div>
            <div className="text-2xl font-bold">{tokenomicsData.stakingRatio}%</div>
            <div className="text-sm text-muted-foreground">Staking Ratio</div>
          </CardContent>
        </Card>
      </div>

      {/* Token Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Token Distribution</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Distribution Chart */}
            <div className="space-y-4">
              {distributionData.map((item, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">{item.label}</span>
                    <span className="text-muted-foreground">{item.percentage}%</span>
                  </div>
                  <Progress value={item.percentage} className="h-2" />
                  <div className="text-xs text-muted-foreground">{(item.amount / 1000000).toFixed(0)}M D3 tokens</div>
                </div>
              ))}
            </div>

            {/* Key Information */}
            <div className="space-y-4">
              <div className="bg-muted/50 rounded-lg p-4 space-y-3">
                <h4 className="font-semibold">Token Utility</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start space-x-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                    <span>Governance voting on platform decisions</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                    <span>Staking for LSDC rewards and voting power</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                    <span>Rewards for data contributions and curation</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                    <span>Access to premium platform features</span>
                  </li>
                </ul>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-muted/30 rounded-lg">
                  <div className="text-lg font-bold">{(tokenomicsData.stakedTokens / 1000000).toFixed(1)}M</div>
                  <div className="text-xs text-muted-foreground">Tokens Staked</div>
                </div>
                <div className="text-center p-3 bg-muted/30 rounded-lg">
                  <div className="text-lg font-bold">{(tokenomicsData.treasuryReserve / 1000000).toFixed(0)}M</div>
                  <div className="text-xs text-muted-foreground">Treasury Reserve</div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Staking Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Total Value Locked</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold mb-2">
              ${((tokenomicsData.stakedTokens * tokenomicsData.currentPrice) / 1000000).toFixed(1)}M
            </div>
            <div className="text-sm text-muted-foreground">
              {(tokenomicsData.stakedTokens / 1000000).toFixed(1)}M D3 tokens staked
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Average APY</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold mb-2 text-green-500">14.2%</div>
            <div className="text-sm text-muted-foreground">Weighted across all tiers</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Active Stakers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold mb-2">3,247</div>
            <div className="text-sm text-muted-foreground">
              <Badge variant="secondary" className="text-xs">
                +12% this month
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
