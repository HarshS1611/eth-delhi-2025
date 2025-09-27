"use client"

import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Calendar, Shield, Coins, ExternalLink } from "lucide-react"
import { lighthouseCidUrl } from "@/lib/lightHouse"

export interface Dataset {
  id?: string | number
  title?: string
  description?: string
  category?: string
  tags?: string[]
  contributor?: { name: string; avatar?: string; verified?: boolean }
  qualityScore?: number
  price?: number
  downloads?: number
  uploadDate?: string
  fileSize?: string
  fileType?: string
  cid?: string
  source?: "ipfs" | "onchain"
}

export function DatasetCard({
  dataset,
  onLicense,
}: {
  dataset: Dataset
  onLicense: (d: Dataset) => void
}) {
  const title = dataset.title || dataset.cid || "Untitled dataset"
  const desc =
    dataset.description ||
    (dataset.cid ? `CID: ${dataset.cid}` : "No description provided")
  const category = dataset.category || (dataset.source === "onchain" ? "On-Chain" : "IPFS")
  const tags = dataset.tags ?? []
  const qs = typeof dataset.qualityScore === "number" ? dataset.qualityScore : 80
  const price = typeof dataset.price === "number" ? dataset.price : 0
  const contributorName = dataset.contributor?.name || "Uploader"

  const qualityBadge =
    qs >= 90 ? { label: "Excellent", variant: "default" as const } :
    qs >= 80 ? { label: "Good", variant: "secondary" as const } :
               { label: "Fair", variant: "outline" as const }

  const getQualityColor = (score: number) =>
    score >= 90 ? "text-green-500" : score >= 80 ? "text-yellow-500" : "text-orange-500"

  return (
    <Card className="group hover:shadow-lg transition-all duration-300 border-border/40 bg-card/50 backdrop-blur hover:bg-card/80">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-semibold text-lg mb-2 group-hover:text-primary transition-colors line-clamp-2">
              {title}
            </h3>
            <p className="text-sm text-muted-foreground line-clamp-2 mb-3">{desc}</p>
          </div>
          <div className="flex flex-col items-end space-y-2">
            <Badge variant={qualityBadge.variant} className="text-xs">{qualityBadge.label}</Badge>
            <div className={`text-sm font-medium ${getQualityColor(qs)}`}>{qs}% Quality</div>
          </div>
        </div>
        <div className="flex flex-wrap gap-1 mb-3">
          <Badge variant="outline" className="text-xs">{category}</Badge>
          {tags.slice(0, 2).map((t) => (
            <Badge key={t} variant="secondary" className="text-xs">{t}</Badge>
          ))}
          {tags.length > 2 && <Badge variant="secondary" className="text-xs">+{tags.length - 2}</Badge>}
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Avatar className="h-6 w-6"><AvatarFallback className="text-xs">{contributorName.charAt(0)}</AvatarFallback></Avatar>
            <span className="text-sm text-muted-foreground">{contributorName}</span>
            {dataset.contributor?.verified && <Shield className="h-3 w-3 text-primary" />}
          </div>
          <div className="flex items-center space-x-2 text-xs text-muted-foreground">
            <Calendar className="h-3 w-3" />
            <span>{dataset.uploadDate || ""}</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1">
            <Coins className="h-4 w-4 text-primary" />
            <span className="font-semibold text-lg">{price} LSDC</span>
          </div>
          <div className="flex items-center gap-2">
            {dataset.cid && (
              <a href={lighthouseCidUrl(dataset.cid)} target="_blank" rel="noreferrer" className="text-xs inline-flex items-center underline text-primary">
                CID <ExternalLink className="ml-1 h-3 w-3" />
              </a>
            )}
            <Button onClick={() => onLicense(dataset)} size="sm" className="bg-gradient-to-r from-primary to-accent hover:opacity-90">
              License
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
