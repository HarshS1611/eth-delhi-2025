import { Button } from "@/components/ui/button"
import { ArrowRight, Upload, Search } from "lucide-react"

export function CTASection() {
  return (
    <section className="py-24 lg:py-32">
      <div className="container">
        <div className="mx-auto max-w-4xl">
          <div className="relative overflow-hidden rounded-3xl border border-border/40 bg-gradient-to-br from-card/50 to-card/30 backdrop-blur">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5" />

            <div className="relative p-8 sm:p-12 lg:p-16">
              <div className="text-center">
                <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
                  Ready to Join the{" "}
                  <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                    Data Revolution?
                  </span>
                </h2>
                <p className="mx-auto max-w-2xl text-lg text-muted-foreground mb-8 text-pretty">
                  Whether you're a data contributor looking to monetize your datasets or a researcher seeking
                  high-quality datasets, D³ Data DAO has everything you need.
                </p>

                <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
                  <Button size="lg" className="bg-gradient-to-r from-primary to-accent hover:opacity-90">
                    <Upload className="mr-2 h-4 w-4" />
                    Upload Dataset
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                  <Button size="lg" variant="outline" className="border-border/40 hover:bg-card/50 bg-transparent">
                    <Search className="mr-2 h-4 w-4" />
                    Browse Marketplace
                  </Button>
                </div>

                <div className="mt-8 flex items-center justify-center space-x-8 text-sm text-muted-foreground">
                  <div className="flex items-center">
                    <div className="mr-2 h-2 w-2 rounded-full bg-green-400" />
                    AI Quality Scoring
                  </div>
                  <div className="flex items-center">
                    <div className="mr-2 h-2 w-2 rounded-full bg-blue-400" />
                    LUSDC Payments
                  </div>
                  <div className="flex items-center">
                    <div className="mr-2 h-2 w-2 rounded-full bg-purple-400" />
                    DAO Governance
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
