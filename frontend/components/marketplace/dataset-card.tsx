"use client"

import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Download, Calendar, Shield, Coins } from "lucide-react"

interface Dataset {
  id: string
  title: string
  description: string
  category: string
  tags: string[]
  contributor: {
    name: string
    avatar?: string
    verified: boolean
  }
  qualityScore: number
  price: number
  downloads: number
  uploadDate: string
  fileSize: string
  fileType: string
}

interface DatasetCardProps {
  dataset: Dataset
  onLicense: (dataset: Dataset) => void
}

export function DatasetCard({ dataset, onLicense }: DatasetCardProps) {
  const getQualityColor = (score: number) => {
    if (score >= 90) return "text-green-500"
    if (score >= 80) return "text-yellow-500"
    return "text-orange-500"
  }

  const getQualityBadge = (score: number) => {
    if (score >= 90) return { label: "Excellent", variant: "default" as const }
    if (score >= 80) return { label: "Good", variant: "secondary" as const }
    return { label: "Fair", variant: "outline" as const }
  }

  const qualityBadge = getQualityBadge(dataset.qualityScore)

  return (
    <Card className="group hover:shadow-lg transition-all duration-300 border-border/40 bg-card/50 backdrop-blur hover:bg-card/80">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-semibold text-lg mb-2 group-hover:text-primary transition-colors line-clamp-2">
              {dataset.title}
            </h3>
            <p className="text-sm text-muted-foreground line-clamp-2 mb-3">{dataset.description}</p>
          </div>
          <div className="flex flex-col items-end space-y-2">
            <Badge variant={qualityBadge.variant} className="text-xs">
              {qualityBadge.label}
            </Badge>
            <div className={`text-sm font-medium ${getQualityColor(dataset.qualityScore)}`}>
              {dataset.qualityScore}% Quality
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-1 mb-3">
          <Badge variant="outline" className="text-xs">
            {dataset.category}
          </Badge>
          {dataset.tags.slice(0, 2).map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              {tag}
            </Badge>
          ))}
          {dataset.tags.length > 2 && (
            <Badge variant="secondary" className="text-xs">
              +{dataset.tags.length - 2}
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Avatar className="h-6 w-6">
              <AvatarFallback className="text-xs">{dataset.contributor.name.charAt(0)}</AvatarFallback>
            </Avatar>
            <span className="text-sm text-muted-foreground">{dataset.contributor.name}</span>
            {dataset.contributor.verified && <Shield className="h-3 w-3 text-primary" />}
          </div>
          <div className="flex items-center space-x-1 text-xs text-muted-foreground">
            <Download className="h-3 w-3" />
            <span>{dataset.downloads}</span>
          </div>
        </div>

        <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
          <div className="flex items-center space-x-1">
            <Calendar className="h-3 w-3" />
            <span>{dataset.uploadDate}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>{dataset.fileSize}</span>
            <span>•</span>
            <span>{dataset.fileType}</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1">
            <Coins className="h-4 w-4 text-accent" />
            <span className="font-semibold text-lg">{dataset.price} LSDC</span>
          </div>
          <Button
            onClick={() => onLicense(dataset)}
            className="bg-gradient-to-r from-primary to-accent hover:opacity-90"
            size="sm"
          >
            License Dataset
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
