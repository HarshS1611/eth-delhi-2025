"use client"

import { useEffect, useMemo, useState } from "react"
import { Header } from "@/components/global/header"
import { DatasetCard, type Dataset } from "@/components/marketplace/dataset-card"
import { PaymentModal } from "@/components/marketplace/payment-modal"
import { MarketplaceFilters, type FilterState } from "@/components/marketplace/marketplace-filters"
import { fetchLighthouseCards } from "@/lib/marketplace"
import { useDatasets } from "@/lib/dao"
import { usePurchasedDatasetIds } from "@/lib/license"

export default function MarketplacePage() {
  const [selected, setSelected] = useState<Dataset | null>(null)
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false)
  const [filters, setFilters] = useState<FilterState>({ search: "", category: "All", sortBy: "relevance" })
  const { ids: purchased } = usePurchasedDatasetIds()

  console.log(purchased)
  // Lighthouse
  const [lhCards, setLhCards] = useState<Dataset[]>([])
  const [lhLoading, setLhLoading] = useState(false)
  const [lhError, setLhError] = useState<string | null>(null)
  useEffect(() => {
    let cancel = false
      ; (async () => {
        setLhLoading(true)
        setLhError(null)
        try {
          const cards = await fetchLighthouseCards()
          if (!cancel) setLhCards(cards)
        } catch (e: any) {
          if (!cancel) setLhError(String(e?.message || e))
        } finally {
          if (!cancel) setLhLoading(false)
        }
      })()
    return () => { cancel = true }
  }, [])

  // On-chain
  const { items: onchainItems, isLoading: chainLoading } = useDatasets()
  const onchainCards: Dataset[] = useMemo(
    () =>
      (onchainItems || []).map((it) => ({
        id: it.id,
        title: it.title,
        description: it.description,
        category: "On-Chain",
        tags: [],
        contributor: { name: it.creator || "Creator", verified: true },
        qualityScore: it.qualityScore,
        price: it.price,
        downloads: it.downloads,
        uploadDate: "",
        fileSize: "",
        fileType: "IPFS",
        cid: it.cid,
        source: "onchain",
      })),
    [onchainItems]
  )

  const allCards = useMemo(() => {
    const list = [...lhCards, ...onchainCards]
    const filtered = list.filter((d) => {
      if (filters.search) {
        const needle = filters.search.toLowerCase()
        const hay = `${d.title || ""} ${d.cid || ""}`.toLowerCase()
        if (!hay.includes(needle)) return false
      }
      if (filters.category === "IPFS" && d.source === "onchain") return false
      if (filters.category === "On-Chain" && d.source !== "onchain") return false
      return true
    })
    const sorted = [...filtered].sort((a, b) => {
      switch (filters.sortBy) {
        case "price-low": return (a.price || 0) - (b.price || 0)
        case "price-high": return (b.price || 0) - (a.price || 0)
        case "quality": return (b.qualityScore || 0) - (a.qualityScore || 0)
        case "newest": return String(b.title).localeCompare(String(a.title))
        default: return 0
      }
    })
    return sorted
  }, [lhCards, onchainCards, filters])



  const handleLicense = (d: Dataset) => {
    setSelected(d)
    setIsPaymentModalOpen(true)
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main className="container py-8">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
            Data <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Marketplace</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Find Lighthouse files and on-chain listings. Fully decentralized.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1">
            <MarketplaceFilters filters={filters} onFiltersChange={setFilters} totalResults={allCards.length} />
          </div>

          <div className="lg:col-span-3">
            {/* {lhError && <div className="text-red-500 text-sm mb-4">{lhError}</div>} */}
            {(lhLoading || chainLoading) && allCards.length === 0 && (
              <div className="text-center py-12 text-muted-foreground">Loading datasets…</div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {allCards.map((d, idx) => {
                // mark owned only for on-chain datasets that have a numeric id
                const idNum = d?.id != null ? Number(d.id) : NaN
                return (
                  <DatasetCard
                    key={`${d.source}-${d.cid || d.id || idx}`}
                    dataset={d}
                    onLicense={handleLicense}
                    isPurchased={d.source === "onchain" && d.id != null && purchased.has(Number(d.id))}

                  />
                )
              })}
            </div>

            {allCards.length === 0 && !(lhLoading || chainLoading) && (
              <div className="text-center py-12">
                <p className="text-muted-foreground mb-4">No datasets match your filters.</p>
                <button onClick={() => setFilters({ search: "", category: "All", sortBy: "relevance" })} className="text-primary hover:underline">
                  Clear all filters
                </button>
              </div>
            )}
          </div>
        </div>
      </main>

      <PaymentModal
        dataset={selected}
        isOpen={isPaymentModalOpen}
        onClose={() => {
          setIsPaymentModalOpen(false)
          setSelected(null)
        }}
      />
    </div>
  )
}
