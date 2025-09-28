"use client"

import { useMemo, useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { useToast } from "@/hooks/use-toast"
import { Coins, Shield, Download, CheckCircle, Loader2, Wallet, ArrowRight } from "lucide-react"
import { lighthouseCidUrl } from "@/lib/lightHouse"
import { ADDR, DATA_DAO_ABI, ERC20_ABI } from "@/lib/contracts"
import type { Dataset } from "./dataset-card"
import { useAccount, useWriteContract } from "wagmi"
import { pub } from "@/lib/dao"

export function PaymentModal({
  dataset,
  isOpen,
  onClose,
}: {
  dataset: Dataset | null
  isOpen: boolean
  onClose: () => void
}) {
  const { toast } = useToast()
  const { address } = useAccount()
  const { writeContractAsync } = useWriteContract()

  const price = typeof dataset?.price === "number" ? dataset!.price : 0
  const priceWei = useMemo(() => {
    try {
      return BigInt(Math.round(price * 1e18))
    } catch {
      return 0n
    }
  }, [price])

  const datasetId = useMemo(() => {
    try {
      if (dataset?.id === undefined || dataset?.id === null) return null
      return BigInt(dataset.id as any)
    } catch {
      return null
    }
  }, [dataset])

  const hasOnchain = datasetId !== null

  const [isProcessing, setIsProcessing] = useState(false)
  const [isCompleted, setIsCompleted] = useState(false)

  const handlePayment = async () => {
    if (!dataset) return
    if (!address) {
      toast({ title: "Connect wallet", description: "Please connect your wallet to continue.", variant: "destructive" })
      return
    }

    setIsProcessing(true)
    try {
      if (hasOnchain) {
        // 1) Approve LSDC to the DAO for `priceWei`
        const approveHash = await writeContractAsync({
          address: ADDR.LSDC,
          abi: ERC20_ABI,
          functionName: "approve",
          args: [ADDR.DATA_DAO, priceWei],
        })
        await pub.waitForTransactionReceipt({ hash: approveHash })

        // 2) Purchase dataset on the DAO
        const purchaseHash = await writeContractAsync({
          address: ADDR.DATA_DAO,
          abi: DATA_DAO_ABI,
          functionName: "purchase",
          args: [datasetId!],
        })
        await pub.waitForTransactionReceipt({ hash: purchaseHash })
      } else {
        // Off-chain-only entry (fallback demo)
        await new Promise((r) => setTimeout(r, 800))
      }

      setIsCompleted(true)
      toast({
        title: "Payment successful!",
        description: hasOnchain ? "Purchase recorded on-chain." : "Access granted.",
      })
      setTimeout(() => {
        setIsCompleted(false)
        onClose()
      }, 1200)
    } catch (e: any) {
      toast({
        title: "Payment failed",
        description: String(e?.shortMessage || e?.message || e),
        variant: "destructive",
      })
    } finally {
      setIsProcessing(false)
    }
  }

  if (isCompleted) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="sm:max-w-md">
          <div className="text-center py-6">
            <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Payment Successful!</h3>
            {dataset?.cid ? (
              <a
                className="inline-flex items-center bg-gradient-to-r from-primary to-accent text-white px-4 py-2 rounded-md"
                href={lighthouseCidUrl(dataset.cid)}
                target="_blank"
                rel="noreferrer"
              >
                <Download className="mr-2 h-4 w-4" /> Open on Gateway
              </a>
            ) : (
              <Button disabled>
                <Download className="mr-2 h-4 w-4" /> Link unavailable
              </Button>
            )}
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  const title = dataset?.title || dataset?.cid || "Dataset"
  const quality = dataset?.qualityScore ?? 80
  const fileSize = dataset?.fileSize || "-"
  const fileType = dataset?.fileType || "-"

  const totalAmount = price
  const platformFee = price * 0.05

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Coins className="h-5 w-5 text-primary" />
            <span>License Dataset</span>
          </DialogTitle>
          <DialogDescription>
            {hasOnchain
              ? "Pay with LSDC to unlock this dataset. The purchase is recorded on-chain."
              : "This entry is not yet on-chain; payment will unlock the IPFS link."}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          <div className="space-y-3">
            <h4 className="font-medium">{title}</h4>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Contributor</span>
              <div className="flex items-center space-x-1">
                <span>{dataset?.contributor?.name || "Uploader"}</span>
                {dataset?.contributor?.verified && <Shield className="h-3 w-3 text-primary" />}
              </div>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Quality Score</span>
              <Badge variant="default">{quality}%</Badge>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">File</span>
              <span>
                {fileSize} • {fileType}
              </span>
            </div>
          </div>

          <Separator />

          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Dataset Price</span>
              <span>{price.toFixed(2)} LSDC</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Platform Fee (5%)</span>
              <span>{platformFee.toFixed(2)} LSDC</span>
            </div>
            <Separator />
            <div className="flex justify-between font-medium">
              <span>Total Amount</span>
              <span>{totalAmount.toFixed(2)} LSDC</span>
            </div>
          </div>

          <div className="space-y-3">
            <Button
              onClick={handlePayment}
              disabled={isProcessing || !dataset}
              className="w-full bg-gradient-to-r from-primary to-accent hover:opacity-90"
              size="lg"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing…
                </>
              ) : (
                <>
                  <Wallet className="mr-2 h-4 w-4" />
                  Pay {totalAmount.toFixed(2)} LSDC
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
