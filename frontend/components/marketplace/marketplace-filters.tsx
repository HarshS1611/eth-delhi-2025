"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Search, X, SlidersHorizontal } from "lucide-react"

interface FilterState {
  search: string
  category: string
  priceRange: [number, number]
  qualityScore: number
  tags: string[]
  sortBy: string
}

interface MarketplaceFiltersProps {
  filters: FilterState
  onFiltersChange: (filters: FilterState) => void
  totalResults: number
}

const categories = [
  "All Categories",
  "Voting Records",
  "Parliamentary Debates",
  "Committee Reports",
  "Legislation",
  "Member Information",
]

const popularTags = [
  "voting-patterns",
  "brexit",
  "budget",
  "healthcare",
  "education",
  "environment",
  "defense",
  "economy",
]

const sortOptions = [
  { value: "relevance", label: "Most Relevant" },
  { value: "newest", label: "Newest First" },
  { value: "price-low", label: "Price: Low to High" },
  { value: "price-high", label: "Price: High to Low" },
  { value: "quality", label: "Highest Quality" },
  { value: "popular", label: "Most Downloaded" },
]

export function MarketplaceFilters({ filters, onFiltersChange, totalResults }: MarketplaceFiltersProps) {
  const [showAdvanced, setShowAdvanced] = useState(false)

  const updateFilters = (updates: Partial<FilterState>) => {
    onFiltersChange({ ...filters, ...updates })
  }

  const addTag = (tag: string) => {
    if (!filters.tags.includes(tag)) {
      updateFilters({ tags: [...filters.tags, tag] })
    }
  }

  const removeTag = (tag: string) => {
    updateFilters({ tags: filters.tags.filter((t) => t !== tag) })
  }

  const clearFilters = () => {
    onFiltersChange({
      search: "",
      category: "All Categories",
      priceRange: [0, 100],
      qualityScore: 0,
      tags: [],
      sortBy: "relevance",
    })
  }

  const hasActiveFilters =
    filters.search ||
    filters.category !== "All Categories" ||
    filters.qualityScore > 0 ||
    filters.tags.length > 0 ||
    filters.priceRange[0] > 0 ||
    filters.priceRange[1] < 100

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search datasets..."
              value={filters.search}
              onChange={(e) => updateFilters({ search: e.target.value })}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Results and Sort */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          {totalResults.toLocaleString()} datasets found
          {hasActiveFilters && (
            <Button variant="link" onClick={clearFilters} className="ml-2 p-0 h-auto text-xs">
              Clear filters
            </Button>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <Label htmlFor="sort" className="text-sm">
            Sort by:
          </Label>
          <select
            id="sort"
            value={filters.sortBy}
            onChange={(e) => updateFilters({ sortBy: e.target.value })}
            className="text-sm border border-input bg-background px-2 py-1 rounded-md"
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Active Filters */}
      {hasActiveFilters && (
        <div className="flex flex-wrap gap-2">
          {filters.category !== "All Categories" && (
            <Badge variant="secondary" className="flex items-center space-x-1">
              <span>{filters.category}</span>
              <button onClick={() => updateFilters({ category: "All Categories" })}>
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
          {filters.qualityScore > 0 && (
            <Badge variant="secondary" className="flex items-center space-x-1">
              <span>Quality: {filters.qualityScore}%+</span>
              <button onClick={() => updateFilters({ qualityScore: 0 })}>
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
          {filters.tags.map((tag) => (
            <Badge key={tag} variant="secondary" className="flex items-center space-x-1">
              <span>{tag}</span>
              <button onClick={() => removeTag(tag)}>
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
        </div>
      )}

      {/* Advanced Filters */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Filters</CardTitle>
            <Button variant="ghost" size="sm" onClick={() => setShowAdvanced(!showAdvanced)} className="text-xs">
              <SlidersHorizontal className="mr-1 h-3 w-3" />
              {showAdvanced ? "Less" : "More"} Filters
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Category Filter */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Category</Label>
            <div className="grid grid-cols-2 gap-2">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => updateFilters({ category })}
                  className={`text-left text-xs p-2 rounded-md border transition-colors ${
                    filters.category === category
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border hover:bg-muted"
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>

          {showAdvanced && (
            <>
              <Separator />

              {/* Quality Score Filter */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">Minimum Quality Score</Label>
                <div className="flex items-center space-x-2">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    step="10"
                    value={filters.qualityScore}
                    onChange={(e) => updateFilters({ qualityScore: Number.parseInt(e.target.value) })}
                    className="flex-1"
                  />
                  <span className="text-sm font-medium w-12">{filters.qualityScore}%</span>
                </div>
              </div>

              <Separator />

              {/* Price Range Filter */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">Price Range (LUSDC)</Label>
                <div className="flex items-center space-x-2">
                  <Input
                    type="number"
                    placeholder="Min"
                    value={filters.priceRange[0]}
                    onChange={(e) =>
                      updateFilters({ priceRange: [Number.parseInt(e.target.value) || 0, filters.priceRange[1]] })
                    }
                    className="text-xs"
                  />
                  <span className="text-xs text-muted-foreground">to</span>
                  <Input
                    type="number"
                    placeholder="Max"
                    value={filters.priceRange[1]}
                    onChange={(e) =>
                      updateFilters({ priceRange: [filters.priceRange[0], Number.parseInt(e.target.value) || 100] })
                    }
                    className="text-xs"
                  />
                </div>
              </div>

              <Separator />

              {/* Tags Filter */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">Popular Tags</Label>
                <div className="flex flex-wrap gap-1">
                  {popularTags.map((tag) => (
                    <button
                      key={tag}
                      onClick={() => addTag(tag)}
                      disabled={filters.tags.includes(tag)}
                      className={`text-xs px-2 py-1 rounded-md border transition-colors ${
                        filters.tags.includes(tag)
                          ? "border-primary bg-primary/10 text-primary cursor-not-allowed"
                          : "border-border hover:bg-muted"
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
