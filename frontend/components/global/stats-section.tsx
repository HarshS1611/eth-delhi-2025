import { Card, CardContent } from "@/components/ui/card"
import { TrendingUp, Users, Database, DollarSign } from "lucide-react"

const stats = [
  {
    icon: Database,
    value: "2,847",
    label: "Datasets Available",
    change: "+12% this month",
    color: "text-primary",
  },
  {
    icon: Users,
    value: "1,234",
    label: "Active Contributors",
    change: "+8% this month",
    color: "text-accent",
  },
  {
    icon: DollarSign,
    value: "$89.2K",
    label: "LSDC Volume",
    change: "+24% this month",
    color: "text-chart-2",
  },
  {
    icon: TrendingUp,
    value: "45.8K",
    label: "Total Downloads",
    change: "+18% this month",
    color: "text-chart-3",
  },
]

export function StatsSection() {
  return (
    <section className="py-24 lg:py-32 gradient-bg">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">Platform Impact</h2>
          <p className="text-lg text-muted-foreground">
            Real-time metrics showing the growth and adoption of our decentralized data marketplace.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat, index) => (
            <Card
              key={index}
              className="group border-border/40 bg-card/50 backdrop-blur hover:bg-card/80 transition-all duration-300"
            >
              <CardContent className="p-6 text-center">
                <div className={`inline-flex rounded-full bg-background/50 p-3 mb-4 ${stat.color}`}>
                  <stat.icon className="h-6 w-6" />
                </div>

                <div className="space-y-2">
                  <div className="text-3xl font-bold group-hover:scale-105 transition-transform">{stat.value}</div>
                  <div className="text-sm font-medium text-muted-foreground">{stat.label}</div>
                  <div className="text-xs text-green-400">{stat.change}</div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
