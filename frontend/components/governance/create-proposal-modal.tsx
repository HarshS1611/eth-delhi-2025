"use client"

import type React from "react"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { Plus, Loader2 } from "lucide-react"

interface CreateProposalModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (proposal: {
    title: string
    description: string
    category: string
    duration: number
  }) => void
}

const categories = [
  { value: "platform", label: "Platform Changes" },
  { value: "treasury", label: "Treasury Management" },
  { value: "technical", label: "Technical Upgrades" },
  { value: "governance", label: "Governance Rules" },
]

export function CreateProposalModal({ isOpen, onClose, onSubmit }: CreateProposalModalProps) {
  const { toast } = useToast()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    category: "",
    duration: 7,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.title.trim() || !formData.description.trim() || !formData.category) {
      toast({
        title: "Missing information",
        description: "Please fill in all required fields.",
        variant: "destructive",
      })
      return
    }

    if (formData.title.length < 10) {
      toast({
        title: "Title too short",
        description: "Proposal title must be at least 10 characters long.",
        variant: "destructive",
      })
      return
    }

    if (formData.description.length < 50) {
      toast({
        title: "Description too short",
        description: "Proposal description must be at least 50 characters long.",
        variant: "destructive",
      })
      return
    }

    setIsSubmitting(true)

    await new Promise((resolve) => setTimeout(resolve, 2000))

    onSubmit(formData)
    setIsSubmitting(false)

    setFormData({
      title: "",
      description: "",
      category: "",
      duration: 7,
    })

    onClose()

    toast({
      title: "Proposal created!",
      description: "Your proposal has been submitted and is now live for voting.",
    })
  }

  const updateFormData = (field: string, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Plus className="h-5 w-5 text-primary" />
            <span>Create New Proposal</span>
          </DialogTitle>
          <DialogDescription>
            Submit a proposal for the DAO community to vote on. Proposals require a minimum stake of 1,000 DataCoin tokens to
            create.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="title">Proposal Title *</Label>
            <Input
              id="title"
              placeholder="e.g., Reduce platform fees to 3% for Q2 2024"
              value={formData.title}
              onChange={(e) => updateFormData("title", e.target.value)}
              maxLength={100}
            />
            <div className="text-xs text-muted-foreground">{formData.title.length}/100 characters</div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="category">Category *</Label>
            <select
              id="category"
              value={formData.category}
              onChange={(e) => updateFormData("category", e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <option value="">Select a category</option>
              {categories.map((category) => (
                <option key={category.value} value={category.value}>
                  {category.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Detailed Description *</Label>
            <Textarea
              id="description"
              placeholder="Provide a detailed explanation of your proposal, including rationale, implementation details, and expected outcomes..."
              rows={6}
              value={formData.description}
              onChange={(e) => updateFormData("description", e.target.value)}
              maxLength={2000}
            />
            <div className="text-xs text-muted-foreground">{formData.description.length}/2000 characters</div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="duration">Voting Duration</Label>
            <select
              id="duration"
              value={formData.duration}
              onChange={(e) => updateFormData("duration", Number.parseInt(e.target.value))}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <option value={3}>3 days</option>
              <option value={7}>7 days (recommended)</option>
              <option value={14}>14 days</option>
              <option value={30}>30 days</option>
            </select>
          </div>

          <div className="bg-muted/50 rounded-lg p-4 space-y-2">
            <h4 className="text-sm font-medium">Proposal Requirements</h4>
            <ul className="space-y-1 text-xs text-muted-foreground">
              <li>• Minimum 1,000 DataCoin tokens staked to create proposal</li>
              <li>• Quorum of 10% of total staked tokens required to pass</li>
              <li>• Simple majority &gt;50% needed for approval</li>
              <li>• Proposal cannot be modified once submitted</li>
            </ul>
          </div>

          <div className="flex justify-end space-x-3">
            <Button type="Button" variant="outline" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="bg-gradient-to-r from-primary to-accent hover:opacity-90"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Proposal
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
