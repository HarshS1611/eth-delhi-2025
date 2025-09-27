import { Header } from "@/components/global/header"
import { HeroSection } from "@/components/global/hero-section"
import { FeaturesSection } from "@/components/global/features-section"
import { StatsSection } from "@/components/global/stats-section"
import { CTASection } from "@/components/global/cta-section"
import { CompleteUploadFlow } from "@/components/complete-flow/CompleteUploadFlow"

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        {/* <CompleteUploadFlow /> */}
        <HeroSection />
        <FeaturesSection />
        <StatsSection />
        <CTASection />
      </main>
    </div>
  )
}
