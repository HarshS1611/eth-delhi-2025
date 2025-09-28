// frontend/components/marketplace/upload-flow.tsx
"use client"

import type React from "react"
import { useState, useCallback, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { useToast } from "@/hooks/use-toast"
import { Upload, FileText, Brain, Cloud, CheckCircle, ArrowRight, X, Plus, ExternalLink } from "lucide-react"
import { lighthouseCidUrl, uploadFileToLighthouse, uploadJsonToLighthouse } from "@/lib/lightHouse"
import { useSubmitFlow } from "@/lib/marketplace"
import { useTokenInfo } from "@/lib/token"
import { ADDR } from "@/lib/contracts"

interface UploadStep {
  id: number
  title: string
  description: string
  status: "pending" | "active" | "completed" | "error"
}

interface DatasetMetadata {
  title: string
  description: string
  tags: string[]
  category: string
  source: string
}

interface AIAnalysis {
  qualityScore: number
  completeness: number
  relevance: number
  suggestedPrice: number
  insights: string[]
}

export function UploadFlow() {
  const { toast } = useToast()
  const { submitNow } = useSubmitFlow()
  const { symbol: paySym = "LSDC" } = useTokenInfo(ADDR.LSDC)

  const [currentStep, setCurrentStep] = useState(0)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [metadata, setMetadata] = useState<DatasetMetadata>({
    title: "",
    description: "",
    tags: [],
    category: "",
    source: "",
  })
  const [newTag, setNewTag] = useState("")
  const [aiAnalysis, setAIAnalysis] = useState<AIAnalysis | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  // CIDs we produce
  const [fileCid, setFileCid] = useState<string | null>(null)        // raw dataset file
  const [manifestCid, setManifestCid] = useState<string | null>(null)// dataset manifest (rich app metadata)
  const [nftMetaCid, setNftMetaCid] = useState<string | null>(null)  // ERC-721 metadata JSON (tokenURI)

  // NEW: pricing / gating inputs (contract needs these)
  const [priceHuman, setPriceHuman] = useState<string>("") // in LSDC (human)
  const [tokenGated, setTokenGated] = useState<boolean>(false)
  const [minTokenBuy, setMinTokenBuy] = useState<string>("0")  // DIP (human)
  const [minStakeBuy, setMinStakeBuy] = useState<string>("0")  // DIP (human)

  const steps: UploadStep[] = [
    { id: 0, title: "Upload Dataset", description: "Select and upload your dataset file", status: currentStep === 0 ? "active" : currentStep > 0 ? "completed" : "pending" },
    { id: 1, title: "Add Metadata", description: "Provide dataset information and tags", status: currentStep === 1 ? "active" : currentStep > 1 ? "completed" : "pending" },
    { id: 2, title: "AI Analysis", description: "AI quality scoring and price suggestion", status: currentStep === 2 ? "active" : currentStep > 2 ? "completed" : "pending" },
    { id: 3, title: "IPFS Upload", description: "Store dataset + NFT metadata via Lighthouse", status: currentStep === 3 ? "active" : currentStep > 3 ? "completed" : "pending" },
    { id: 4, title: "Complete", description: "Publish to marketplace", status: currentStep === 4 ? "completed" : "pending" },
  ]

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    const valid = ["application/json", "text/csv", "application/xml", "text/xml"]
    if (!valid.includes(file.type)) {
      toast({ title: "Invalid file type", description: "Please upload a JSON, CSV, or XML file.", variant: "destructive" })
      return
    }
    if (file.size > 50 * 1024 * 1024) {
      toast({ title: "File too large", description: "Please upload a file smaller than 50MB.", variant: "destructive" })
      return
    }
    setUploadedFile(file)
    setFileCid(null)
    setManifestCid(null)
    setNftMetaCid(null)
    setUploadProgress(0)
    toast({ title: "File ready", description: `${file.name} selected.` })
  }, [toast])

  const handleAddTag = () => {
    if (newTag.trim() && !metadata.tags.includes(newTag.trim())) {
      setMetadata((prev) => ({ ...prev, tags: [...prev.tags, newTag.trim()] }))
      setNewTag("")
    }
  }
  const handleRemoveTag = (t: string) => setMetadata((p) => ({ ...p, tags: p.tags.filter((x) => x !== t) }))

  async function simulateAIAnalysis() {
    setIsAnalyzing(true)
    await new Promise((r) => setTimeout(r, 500))
    setAIAnalysis({
      qualityScore: 92,
      completeness: 88,
      relevance: 90,
      suggestedPrice: 42,
      insights: ["High data completeness", "Strong correlation", "Well structured"],
    })
    setIsAnalyzing(false)
  }

  // ---- NFT metadata helpers ----
  function svgPreview(title: string) {
    const safe = (title || "Dataset").slice(0, 120).replace(/[<&>]/g, s => ({'<':'&lt;','>':'&gt;','&':'&amp;'}[s] as string))
    return `
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="420">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#6EE7F9"/>
      <stop offset="100%" stop-color="#A78BFA"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#g)" />
  <text x="40" y="140" font-size="32" font-family="Inter, system-ui, sans-serif" fill="#0f172a">DIP Dataset License</text>
  <text x="40" y="200" font-size="28" font-family="Inter, system-ui, sans-serif" fill="#111827" font-weight="700">${safe}</text>
  <text x="40" y="260" font-size="16" font-family="Inter, system-ui, sans-serif" fill="#111827">IPFS pinned via Lighthouse</text>
</svg>`.trim()
  }

  function buildNftMetadata(params: {
    title: string
    description: string
    fileCid: string
    fileName: string
    category: string
    tags: string[]
    qualityScore: number
  }) {
    const { title, description, fileCid, fileName, category, tags, qualityScore } = params
    return {
      name: title,
      description: description || `License NFT for dataset ${title}`,
      external_url: lighthouseCidUrl(fileCid),
      // You can also upload a PNG and set `image: "ipfs://..."`. Using inline SVG keeps it simple:
      image_data: svgPreview(title),
      attributes: [
        { trait_type: "Category", value: category || "Uncategorized" },
        { trait_type: "Quality Score", value: String(qualityScore ?? 0) },
        { trait_type: "File", value: fileName },
        { trait_type: "CID", value: fileCid },
        ...(tags || []).map((t) => ({ trait_type: "Tag", value: t })),
      ],
    }
  }

  async function doLighthouseUpload(): Promise<{ fileCid: string; manifestCid: string | null; nftMetaCid: string }> {
    if (!uploadedFile) throw new Error("No file selected")

    // 1) Upload raw file
    const up = await uploadFileToLighthouse(uploadedFile, (p) => setUploadProgress(Math.round(p)))
    setFileCid(up.cid)

    // 2) Upload dataset manifest (rich app metadata; optional but useful for UI/search)
    const manifest = {
      ...metadata,
      ai: aiAnalysis,
      file: { name: up.name, size: up.size, cid: up.cid, mime: (uploadedFile as File).type },
      createdAt: new Date().toISOString(),
      // link forward to NFT metadata later (filled after upload)
    }
    let mCid: string | null = null
    try {
      const res = await uploadJsonToLighthouse(manifest, `${metadata.title || up.name}-manifest.json`)
      mCid = res.cid
      setManifestCid(mCid)
    } catch {
      // manifest is optional; don't block
    }

    // 3) Upload ERC-721 metadata JSON (this becomes tokenUri used by DAO/NFT)
    const nftMeta = buildNftMetadata({
      title: metadata.title || up.name,
      description: metadata.description,
      fileCid: up.cid,
      fileName: up.name,
      category: metadata.category,
      tags: metadata.tags,
      qualityScore: aiAnalysis?.qualityScore ?? 0,
    })
    const nftRes = await uploadJsonToLighthouse(nftMeta, `${metadata.title || up.name}-nft.json`)
    const tokenMetaCid = nftRes.cid
    setNftMetaCid(tokenMetaCid)

    return { fileCid: up.cid, manifestCid: mCid, nftMetaCid: tokenMetaCid }
  }

  const handleNextStep = async () => {
    try {
      if (currentStep === 0 && !uploadedFile) {
        toast({ title: "No file selected", description: "Please upload a dataset file to continue.", variant: "destructive" })
        return
      }
      if (currentStep === 1 && (!metadata.title || !metadata.description || !metadata.category)) {
        toast({ title: "Missing information", description: "Fill in title, description and category.", variant: "destructive" })
        return
      }
      if (currentStep === 2 && !aiAnalysis) {
        await simulateAIAnalysis()
        return
      }
      if (currentStep === 3) {
        // Require price and ensure it’s a valid number
        const p = Number(priceHuman)
        if (!Number.isFinite(p) || p <= 0) {
          toast({ title: "Set a price", description: `Enter a valid ${paySym} price (e.g., 42)`, variant: "destructive" })
          return
        }

        const { fileCid: fCid, manifestCid: mCid, nftMetaCid: nCid } = await doLighthouseUpload()
        setUploadProgress(100)

        // Submit to DAO with the proper tokenUri (ERC-721 metadata)
        await submitNow({
          cid: fCid,
          title: metadata.title || uploadedFile!.name,
          tokenUri: `ipfs://${nCid}`,
          price: p, // human LSDC; hook converts to wei
          qualityScore: aiAnalysis?.qualityScore ?? 80,
          tokenGated,
          minTokenForBuy: minTokenBuy,
          minStakeForBuy: minStakeBuy,
        })
      }

      setCurrentStep((s) => Math.min(s + 1, steps.length - 1))
    } catch (err: any) {
      console.error(err)
      toast({ title: "Upload failed", description: String(err?.message || err), variant: "destructive" })
    }
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-6">
            <div className="border-2 border-dashed border-border/40 rounded-lg p-8 text-center hover:border-primary/50 transition-colors">
              <input id="file-upload" className="hidden" type="file" accept=".json,.csv,.xml" onChange={handleFileUpload} />
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-lg font-medium mb-2">Upload your dataset</p>
                <p className="text-sm text-muted-foreground mb-4">Drag and drop or click to select JSON, CSV, or XML files (max 50MB)</p>
                <Button variant="outline">Choose File</Button>
              </label>
            </div>

            {/* NEW: pricing + gating setup so user gives all contract params up-front */}
            <Card>
              <CardHeader><CardTitle>Pricing & Access</CardTitle></CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Price ({paySym}) *</Label>
                  <Input
                    type="number"
                    min="0"
                    step="0.000000000000000001"
                    value={priceHuman}
                    onChange={(e) => setPriceHuman(e.target.value)}
                    placeholder={`e.g., ${aiAnalysis?.suggestedPrice ?? 10}`}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Token Gated?</Label>
                  <select
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={tokenGated ? "yes" : "no"}
                    onChange={(e) => setTokenGated(e.target.value === "yes")}
                  >
                    <option value="no">No (default)</option>
                    <option value="yes">Yes</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label>Min Stake (DIP)</Label>
                  <Input
                    type="number"
                    min="0"
                    step="0.000000000000000001"
                    value={minStakeBuy}
                    onChange={(e) => setMinStakeBuy(e.target.value)}
                    disabled={!tokenGated}
                    placeholder="0"
                  />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <Label>Min Token Balance (DIP)</Label>
                  <Input
                    type="number"
                    min="0"
                    step="0.000000000000000001"
                    value={minTokenBuy}
                    onChange={(e) => setMinTokenBuy(e.target.value)}
                    disabled={!tokenGated}
                    placeholder="0"
                  />
                </div>
              </CardContent>
            </Card>

            {uploadedFile && (
              <Card className="border-primary/20 bg-primary/5">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <FileText className="h-8 w-8 text-primary" />
                    <div className="flex-1">
                      <p className="font-medium">{uploadedFile.name}</p>
                      <p className="text-sm text-muted-foreground">{(uploadedFile.size / 1024 / 1024).toFixed(2)} MB • {uploadedFile.type}</p>
                    </div>
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )
      case 1:
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="title">Dataset Title *</Label>
                <Input id="title" value={metadata.title} onChange={(e) => setMetadata((p) => ({ ...p, title: e.target.value }))} placeholder="e.g., UK Parliament Voting Records 2024" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="category">Category *</Label>
                <select id="category" className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" value={metadata.category} onChange={(e) => setMetadata((p) => ({ ...p, category: e.target.value }))}>
                  <option value="">Select category</option>
                  <option value="voting-records">Voting Records</option>
                  <option value="debates">Parliamentary Debates</option>
                  <option value="committees">Committee Reports</option>
                  <option value="legislation">Legislation</option>
                  <option value="members">Member Information</option>
                </select>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description *</Label>
              <Textarea id="description" rows={4} value={metadata.description} onChange={(e) => setMetadata((p) => ({ ...p, description: e.target.value }))} placeholder="Describe your dataset..." />
            </div>
            <div className="space-y-2">
              <Label htmlFor="source">Data Source</Label>
              <Input id="source" value={metadata.source} onChange={(e) => setMetadata((p) => ({ ...p, source: e.target.value }))} placeholder="e.g., Official Records" />
            </div>
            <div className="space-y-2">
              <Label>Tags</Label>
              <div className="flex space-x-2">
                <Input value={newTag} onChange={(e) => setNewTag(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleAddTag()} placeholder="Add a tag..." />
                <Button onClick={handleAddTag} size="icon" variant="outline"><Plus className="h-4 w-4" /></Button>
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                {metadata.tags.map((t) => (
                  <Badge key={t} variant="secondary" className="flex items-center space-x-1">
                    <span>{t}</span>
                    <Button onClick={() => handleRemoveTag(t)} className="ml-1 hover:text-destructive"><X className="h-3 w-3" /></Button>
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        )
      case 2:
        return (
          <div className="space-y-6">
            {isAnalyzing ? (
              <Card className="border-primary/20 bg-primary/5">
                <CardContent className="p-6 text-center">
                  <Brain className="mx-auto h-12 w-12 text-primary mb-4 animate-pulse" />
                  <h3 className="text-lg font-semibold mb-2">AI Analysis in Progress</h3>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div className="bg-primary h-2 rounded-full animate-pulse" style={{ width: "60%" }} />
                  </div>
                </CardContent>
              </Card>
            ) : aiAnalysis ? (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2"><Brain className="h-5 w-5 text-primary" /><span>AI Quality Analysis</span></CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center"><div className="text-2xl font-bold text-primary">{aiAnalysis.qualityScore}%</div><div className="text-sm text-muted-foreground">Overall Quality</div></div>
                    <div className="text-center"><div className="text-2xl font-bold text-primary">{aiAnalysis.completeness}%</div><div className="text-sm text-muted-foreground">Completeness</div></div>
                    <div className="text-center"><div className="text-2xl font-bold text-primary">{aiAnalysis.relevance}%</div><div className="text-sm text-muted-foreground">Relevance</div></div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card><CardContent className="p-6 text-center"><Brain className="mx-auto h-12 w-12 text-muted-foreground mb-4" /><h3 className="text-lg font-semibold mb-2">Ready for AI Analysis</h3></CardContent></Card>
            )}
          </div>
        )
      case 3:
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2"><Cloud className="h-5 w-5 text-primary" /><span>IPFS Upload (Lighthouse)</span></CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">We will upload the dataset file, a dataset manifest, and your NFT metadata JSON.</p>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm"><span>Upload Progress</span><span>{uploadProgress}%</span></div>
                  <Progress value={uploadProgress} className="w-full" />
                </div>
                {(fileCid || manifestCid || nftMetaCid) && (
                  <div className="rounded-md bg-muted/50 p-3 text-sm flex flex-col gap-2">
                    {fileCid && <div className="flex items-center gap-2"><span className="font-medium">File CID</span><code className="break-all">{fileCid}</code></div>}
                    {manifestCid && <div className="flex items-center gap-2"><span className="font-medium">Manifest CID</span><code className="break-all">{manifestCid}</code></div>}
                    {nftMetaCid && <div className="flex items-center gap-2"><span className="font-medium">NFT Metadata CID</span><code className="break-all">{nftMetaCid}</code></div>}
                    <div className="flex flex-wrap gap-3">
                      {fileCid && <a className="inline-flex items-center text-primary text-sm underline" href={lighthouseCidUrl(fileCid)} target="_blank" rel="noreferrer">
                        View file <ExternalLink className="ml-1 h-3 w-3" />
                      </a>}
                      {manifestCid && <a className="inline-flex items-center text-primary text-sm underline" href={lighthouseCidUrl(manifestCid)} target="_blank" rel="noreferrer">
                        View manifest <ExternalLink className="ml-1 h-3 w-3" />
                      </a>}
                      {nftMetaCid && <a className="inline-flex items-center text-primary text-sm underline" href={lighthouseCidUrl(nftMetaCid)} target="_blank" rel="noreferrer">
                        View NFT metadata <ExternalLink className="ml-1 h-3 w-3" />
                      </a>}
                    </div>
                  </div>
                )}
                {uploadProgress === 100 && (
                  <div className="flex items-center space-x-2 text-green-600"><CheckCircle className="h-4 w-4" /><span className="text-sm">Successfully uploaded to Lighthouse</span></div>
                )}
              </CardContent>
            </Card>
          </div>
        )
      case 4:
        return (
          <div className="space-y-6">
            <Card className="border-green-500/20 bg-green-500/5">
              <CardContent className="p-6 text-center">
                <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-4" />
                <h3 className="text-2xl font-bold mb-2">Dataset Published Successfully!</h3>
                <p className="text-muted-foreground mb-6">Your dataset is uploaded and submitted on-chain.</p>
                <div className="flex justify-center gap-3 mb-4">
                  {fileCid && <a className="text-primary underline inline-flex items-center" href={lighthouseCidUrl(fileCid)} target="_blank" rel="noreferrer">Open File <ExternalLink className="ml-1 h-3 w-3" /></a>}
                  {manifestCid && <a className="text-primary underline inline-flex items-center" href={lighthouseCidUrl(manifestCid)} target="_blank" rel="noreferrer">Manifest JSON <ExternalLink className="ml-1 h-3 w-3" /></a>}
                  {nftMetaCid && <a className="text-primary underline inline-flex items-center" href={lighthouseCidUrl(nftMetaCid)} target="_blank" rel="noreferrer">NFT Metadata <ExternalLink className="ml-1 h-3 w-3" /></a>}
                </div>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Button className="bg-gradient-to-r from-primary to-accent">View in Marketplace<ArrowRight className="ml-2 h-4 w-4" /></Button>
                  <Button variant="outline" onClick={() => {
                    setCurrentStep(0)
                    setUploadedFile(null)
                    setFileCid(null)
                    setManifestCid(null)
                    setNftMetaCid(null)
                    setUploadProgress(0)
                    setAIAnalysis(null)
                    setPriceHuman("")
                    setTokenGated(false)
                    setMinTokenBuy("0")
                    setMinStakeBuy("0")
                    setMetadata({ title: "", description: "", tags: [], category: "", source: "" })
                  }}>Upload Another Dataset</Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        {steps.map((step, i) => (
          <div key={step.id} className="flex items-center">
            <div className="flex flex-col items-center">
              <div className={`flex h-10 w-10 items-center justify-center rounded-full border-2 ${step.status === "completed" ? "border-green-500 bg-green-500 text-white" : step.status === "active" ? "border-primary bg-primary text-white" : "border-border bg-background text-muted-foreground"}`}>
                {step.status === "completed" ? <CheckCircle className="h-5 w-5" /> : <span className="text-sm font-medium">{step.id + 1}</span>}
              </div>
              <div className="mt-2 text-center">
                <div className="text-sm font-medium">{step.title}</div>
                <div className="text-xs text-muted-foreground hidden sm:block">{step.description}</div>
              </div>
            </div>
            {i < steps.length - 1 && <div className={`mx-4 h-0.5 w-16 ${step.status === "completed" ? "bg-green-500" : "bg-border"}`} />}
          </div>
        ))}
      </div>

      <Card>
        <CardHeader><CardTitle>{steps[currentStep].title}</CardTitle></CardHeader>
        <CardContent>{renderStepContent()}</CardContent>
      </Card>

      <div className="flex justify-between">
        <Button variant="outline" onClick={() => setCurrentStep((s) => Math.max(s - 1, 0))} disabled={currentStep === 0}>Previous</Button>
        <Button onClick={handleNextStep} disabled={currentStep === steps.length - 1} className="bg-gradient-to-r from-primary to-accent hover:opacity-90">
          {currentStep === steps.length - 2 ? "Publish Dataset" : "Continue"}
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
