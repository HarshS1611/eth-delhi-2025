"use client"

import { useState } from "react"
import { Header } from "@/components/global/header"
import { DatasetCard } from "@/components/marketplace/dataset-card"
import { PaymentModal } from "@/components/marketplace/payment-modal"
import { MarketplaceFilters } from "@/components/marketplace/marketplace-filters"

// Mock data for demonstration
const mockDatasets = [
  {
    id: "1",
    title: "UK Parliament Voting Records 2024",
    description:
      "Comprehensive voting records from the UK Parliament including division lists, member votes, and bill outcomes for the 2024 session.",
    category: "Voting Records",
    tags: ["voting-patterns", "2024", "parliament", "divisions"],
    contributor: {
      name: "DataGov UK",
      verified: true,
    },
    qualityScore: 95,
    price: 45.99,
    downloads: 1247,
    uploadDate: "2024-01-15",
    fileSize: "12.4 MB",
    fileType: "JSON",
  },
  {
    id: "2",
    title: "Parliamentary Debates Transcripts Q1 2024",
    description:
      "Full transcripts of parliamentary debates from January to March 2024, including speaker identification and topic classification.",
    category: "Parliamentary Debates",
    tags: ["debates", "transcripts", "Q1-2024", "hansard"],
    contributor: {
      name: "Parliament Analytics",
      verified: true,
    },
    qualityScore: 88,
    price: 32.5,
    downloads: 892,
    uploadDate: "2024-04-02",
    fileSize: "8.7 MB",
    fileType: "CSV",
  },
  {
    id: "3",
    title: "Committee Report Analysis Dataset",
    description:
      "Structured data from parliamentary committee reports with sentiment analysis, key topics, and recommendation tracking.",
    category: "Committee Reports",
    tags: ["committees", "reports", "analysis", "sentiment"],
    contributor: {
      name: "PolicyData Labs",
      verified: false,
    },
    qualityScore: 82,
    price: 28.75,
    downloads: 634,
    uploadDate: "2024-03-20",
    fileSize: "5.2 MB",
    fileType: "JSON",
  },
  {
    id: "4",
    title: "Brexit Legislation Timeline",
    description:
      "Complete timeline of Brexit-related legislation, amendments, and voting patterns from 2016-2024 with detailed metadata.",
    category: "Legislation",
    tags: ["brexit", "legislation", "timeline", "amendments"],
    contributor: {
      name: "Brexit Research Group",
      verified: true,
    },
    qualityScore: 91,
    price: 55.0,
    downloads: 2103,
    uploadDate: "2024-02-10",
    fileSize: "18.9 MB",
    fileType: "XML",
  },
  {
    id: "5",
    title: "MP Constituency Data 2024",
    description:
      "Comprehensive dataset of MP information, constituency details, party affiliations, and electoral statistics for 2024.",
    category: "Member Information",
    tags: ["MPs", "constituencies", "elections", "statistics"],
    contributor: {
      name: "Electoral Insights",
      verified: true,
    },
    qualityScore: 93,
    price: 38.25,
    downloads: 1567,
    uploadDate: "2024-01-28",
    fileSize: "7.1 MB",
    fileType: "CSV",
  },
  {
    id: "6",
    title: "Healthcare Policy Debates 2023-2024",
    description:
      "Focused dataset on healthcare-related parliamentary discussions, policy proposals, and voting outcomes.",
    category: "Parliamentary Debates",
    tags: ["healthcare", "policy", "debates", "NHS"],
    contributor: {
      name: "Health Policy Watch",
      verified: false,
    },
    qualityScore: 79,
    price: 22.99,
    downloads: 445,
    uploadDate: "2024-03-05",
    fileSize: "4.8 MB",
    fileType: "JSON",
  },
]

interface FilterState {
  search: string
  category: string
  priceRange: [number, number]
  qualityScore: number
  tags: string[]
  sortBy: string
}

export default function MarketplacePage() {
  const [selectedDataset, setSelectedDataset] = useState<(typeof mockDatasets)[0] | null>(null)
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false)
  const [filters, setFilters] = useState<FilterState>({
    search: "",
    category: "All Categories",
    priceRange: [0, 100],
    qualityScore: 0,
    tags: [],
    sortBy: "relevance",
  })

  const handleLicenseDataset = (dataset: (typeof mockDatasets)[0]) => {
    setSelectedDataset(dataset)
    setIsPaymentModalOpen(true)
  }

  // Filter and sort datasets based on current filters
  const filteredDatasets = mockDatasets
    .filter((dataset) => {
      // Search filter
      if (filters.search && !dataset.title.toLowerCase().includes(filters.search.toLowerCase())) {
        return false
      }

      // Category filter
      if (filters.category !== "All Categories" && dataset.category !== filters.category) {
        return false
      }

      // Quality score filter
      if (dataset.qualityScore < filters.qualityScore) {
        return false
      }

      // Price range filter
      if (dataset.price < filters.priceRange[0] || dataset.price > filters.priceRange[1]) {
        return false
      }

      // Tags filter
      if (filters.tags.length > 0 && !filters.tags.some((tag) => dataset.tags.includes(tag))) {
        return false
      }

      return true
    })
    .sort((a, b) => {
      switch (filters.sortBy) {
        case "newest":
          return new Date(b.uploadDate).getTime() - new Date(a.uploadDate).getTime()
        case "price-low":
          return a.price - b.price
        case "price-high":
          return b.price - a.price
        case "quality":
          return b.qualityScore - a.qualityScore
        case "popular":
          return b.downloads - a.downloads
        default:
          return 0
      }
    })

  return (
    <div className="min-h-screen">
      <Header />
      <main className="container py-8">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
            Data{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Marketplace</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Discover and license high-quality datasets curated by our AI and verified by the community.
            All payments are processed securely using LSDC stablecoin.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <MarketplaceFilters filters={filters} onFiltersChange={setFilters} totalResults={filteredDatasets.length} />
          </div>

          {/* Dataset Grid */}
          <div className="lg:col-span-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredDatasets.map((dataset) => (
                <DatasetCard key={dataset.id} dataset={dataset} onLicense={handleLicenseDataset} />
              ))}
            </div>

            {filteredDatasets.length === 0 && (
              <div className="text-center py-12">
                <p className="text-muted-foreground mb-4">No datasets match your current filters.</p>
                <button
                  onClick={() =>
                    setFilters({
                      search: "",
                      category: "All Categories",
                      priceRange: [0, 100],
                      qualityScore: 0,
                      tags: [],
                      sortBy: "relevance",
                    })
                  }
                  className="text-primary hover:underline"
                >
                  Clear all filters
                </button>
              </div>
            )}
          </div>
        </div>
      </main>

      <PaymentModal
        dataset={selectedDataset}
        isOpen={isPaymentModalOpen}
        onClose={() => {
          setIsPaymentModalOpen(false)
          setSelectedDataset(null)
        }}
      />
    </div>
  )
}
