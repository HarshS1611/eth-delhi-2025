"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export interface FilterState {
  search: string
  category: string
  sortBy: string
}

function FiltersBase({
  filters,
  onFiltersChange,
  totalResults,
}: {
  filters: FilterState
  onFiltersChange: (f: FilterState) => void
  totalResults: number
}) {
  const update = (patch: Partial<FilterState>) => onFiltersChange({ ...filters, ...patch })
  return (
    <Card>
      <CardContent className="space-y-4 p-4">
        <div className="text-sm text-muted-foreground">{totalResults} datasets</div>
        <div className="space-y-2">
          <Label>Search</Label>
          <Input
            placeholder="Search by title or CID…"
            value={filters.search}
            onChange={(e) => update({ search: e.target.value })}
          />
        </div>
        <div className="space-y-2">
          <Label>Category</Label>
          <select
            className="text-sm border border-input bg-background px-2 py-2 rounded-md w-full"
            value={filters.category}
            onChange={(e) => update({ category: e.target.value })}
          >
            <option>All</option>
            <option>IPFS</option>
            <option>On-Chain</option>
          </select>
        </div>
        <div className="space-y-2">
          <Label>Sort by</Label>
          <select
            className="text-sm border border-input bg-background px-2 py-2 rounded-md w-full"
            value={filters.sortBy}
            onChange={(e) => update({ sortBy: e.target.value })}
          >
            <option value="relevance">Most Relevant</option>
            <option value="newest">Newest First</option>
            <option value="price-low">Price: Low to High</option>
            <option value="price-high">Price: High to Low</option>
            <option value="quality">Highest Quality</option>
          </select>
        </div>
      </CardContent>
    </Card>
  )
}

export const MinimalFilters = FiltersBase
export const MarketplaceFilters = FiltersBase
