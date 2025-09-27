import { Header } from "@/components/global/header"
import { UploadFlow } from "@/components/global/upload-flow"

export default function UploadPage() {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="container py-8">
        <div className="mx-auto max-w-4xl">
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
              Upload Your{" "}
              <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Dataset</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Share your dataset with the community. Our AI will analyze quality, suggest pricing, and help
              you earn rewards through our decentralized marketplace.
            </p>
          </div>

          <UploadFlow />
        </div>
      </main>
    </div>
  )
}
