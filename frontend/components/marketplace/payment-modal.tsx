"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { useToast } from "@/hooks/use-toast"
import { Coins, Shield, Download, CheckCircle, Loader2, Wallet, ArrowRight } from "lucide-react"

interface Dataset {
  id: string
  title: string
  description: string
  contributor: {
    name: string
    verified: boolean
  }
  qualityScore: number
  price: number
  fileSize: string
  fileType: string
}

interface PaymentModalProps {
  dataset: Dataset | null
  isOpen: boolean
  onClose: () => void
}

export function PaymentModal({ dataset, isOpen, onClose }: PaymentModalProps) {
  const { toast } = useToast()
  const [isProcessing, setIsProcessing] = useState(false)
  const [isCompleted, setIsCompleted] = useState(false)

  if (!dataset) return null

  const platformFee = dataset.price * 0.05 // 5% platform fee
  const contributorShare = dataset.price * 0.85 // 85% to contributor
  const daoTreasury = dataset.price * 0.1 // 10% to DAO treasury
  const totalAmount = dataset.price

  const handlePayment = async () => {
    setIsProcessing(true)

    // Simulate payment processing
    await new Promise((resolve) => setTimeout(resolve, 3000))

    setIsProcessing(false)
    setIsCompleted(true)

    toast({
      title: "Payment successful!",
      description: "You now have access to the dataset. NFT license has been minted to your wallet.",
    })

    // Auto-close after success
    setTimeout(() => {
      setIsCompleted(false)
      onClose()
    }, 3000)
  }

  if (isCompleted) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="sm:max-w-md">
          <div className="text-center py-6">
            <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Payment Successful!</h3>
            <p className="text-muted-foreground mb-4">
              Your NFT license has been minted and the dataset is now available for download.
            </p>
            <Button className="bg-gradient-to-r from-primary to-accent">
              <Download className="mr-2 h-4 w-4" />
              Download Dataset
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Coins className="h-5 w-5 text-accent" />
            <span>License Dataset</span>
          </DialogTitle>
          <DialogDescription>
            Purchase a license to access and download this dataset. Payment is processed using LUSDC stablecoin.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Dataset Info */}
          <div className="space-y-3">
            <h4 className="font-medium">{dataset.title}</h4>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Contributor</span>
              <div className="flex items-center space-x-1">
                <span>{dataset.contributor.name}</span>
                {dataset.contributor.verified && <Shield className="h-3 w-3 text-primary" />}
              </div>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Quality Score</span>
              <Badge variant="default">{dataset.qualityScore}%</Badge>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">File Details</span>
              <span>
                {dataset.fileSize} • {dataset.fileType}
              </span>
            </div>
          </div>

          <Separator />

          {/* Payment Breakdown */}
          <div className="space-y-3">
            <h4 className="font-medium">Payment Breakdown</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Dataset Price</span>
                <span>{dataset.price.toFixed(2)} LUSDC</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Platform Fee (5%)</span>
                <span>{platformFee.toFixed(2)} LUSDC</span>
              </div>
              <Separator />
              <div className="flex justify-between font-medium">
                <span>Total Amount</span>
                <span>{totalAmount.toFixed(2)} LUSDC</span>
              </div>
            </div>
          </div>

          {/* Fund Distribution */}
          <div className="bg-muted/50 rounded-lg p-4 space-y-2">
            <h5 className="text-sm font-medium">Fund Distribution</h5>
            <div className="space-y-1 text-xs text-muted-foreground">
              <div className="flex justify-between">
                <span>To Contributor ({dataset.contributor.name})</span>
                <span>{contributorShare.toFixed(2)} LUSDC (85%)</span>
              </div>
              <div className="flex justify-between">
                <span>To DAO Treasury</span>
                <span>{daoTreasury.toFixed(2)} LUSDC (10%)</span>
              </div>
              <div className="flex justify-between">
                <span>Platform Operations</span>
                <span>{platformFee.toFixed(2)} LUSDC (5%)</span>
              </div>
            </div>
          </div>

          {/* Payment Button */}
          <div className="space-y-3">
            <Button
              onClick={handlePayment}
              disabled={isProcessing}
              className="w-full bg-gradient-to-r from-primary to-accent hover:opacity-90"
              size="lg"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing Payment...
                </>
              ) : (
                <>
                  <Wallet className="mr-2 h-4 w-4" />
                  Pay {totalAmount.toFixed(2)} LUSDC
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>

            <div className="flex items-center justify-center space-x-2 text-xs text-muted-foreground">
              <Shield className="h-3 w-3" />
              <span>Secure payment powered by blockchain technology</span>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
