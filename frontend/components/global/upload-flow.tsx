"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { useToast } from "@/hooks/use-toast"
import { Upload, FileText, Brain, Cloud, CheckCircle, Coins, ArrowRight, X, Plus } from "lucide-react"

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

  const steps: UploadStep[] = [
    {
      id: 0,
      title: "Upload Dataset",
      description: "Select and upload your dataset file",
      status: currentStep === 0 ? "active" : currentStep > 0 ? "completed" : "pending",
    },
    {
      id: 1,
      title: "Add Metadata",
      description: "Provide dataset information and tags",
      status: currentStep === 1 ? "active" : currentStep > 1 ? "completed" : "pending",
    },
    {
      id: 2,
      title: "AI Analysis",
      description: "AI quality scoring and price suggestion",
      status: currentStep === 2 ? "active" : currentStep > 2 ? "completed" : "pending",
    },
    {
      id: 3,
      title: "IPFS Upload",
      description: "Store dataset on decentralized network",
      status: currentStep === 3 ? "active" : currentStep > 3 ? "completed" : "pending",
    },
    {
      id: 4,
      title: "Complete",
      description: "Receive rewards and publish dataset",
      status: currentStep === 4 ? "completed" : "pending",
    },
  ]

  const handleFileUpload = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0]
      if (file) {
        const validTypes = ["application/json", "text/csv", "application/xml", "text/xml"]
        if (!validTypes.includes(file.type)) {
          toast({
            title: "Invalid file type",
            description: "Please upload a JSON, CSV, or XML file.",
            variant: "destructive",
          })
          return
        }

        if (file.size > 50 * 1024 * 1024) {
          // 50MB limit
          toast({
            title: "File too large",
            description: "Please upload a file smaller than 50MB.",
            variant: "destructive",
          })
          return
        }

        setUploadedFile(file)
        toast({
          title: "File uploaded successfully",
          description: `${file.name} is ready for processing.`,
        })
      }
    },
    [toast],
  )

  const handleAddTag = () => {
    if (newTag.trim() && !metadata.tags.includes(newTag.trim())) {
      setMetadata((prev) => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()],
      }))
      setNewTag("")
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setMetadata((prev) => ({
      ...prev,
      tags: prev.tags.filter((tag) => tag !== tagToRemove),
    }))
  }

  const simulateAIAnalysis = async () => {
    setIsAnalyzing(true)

    // Simulate AI analysis with realistic delay
    await new Promise((resolve) => setTimeout(resolve, 3000))

    const mockAnalysis: AIAnalysis = {
      qualityScore: Math.floor(Math.random() * 30) + 70, // 70-100
      completeness: Math.floor(Math.random() * 20) + 80, // 80-100
      relevance: Math.floor(Math.random() * 25) + 75, // 75-100
      suggestedPrice: Math.floor(Math.random() * 50) + 25, // 25-75 PYUSD
      insights: [
        "High data completeness with minimal missing values",
        "Strong correlation with parliamentary voting patterns",
        "Excellent temporal coverage spanning multiple sessions",
        "Well-structured format suitable for analysis",
      ],
    }

    setAIAnalysis(mockAnalysis)
    setIsAnalyzing(false)
  }

  const simulateIPFSUpload = async () => {
    for (let i = 0; i <= 100; i += 10) {
      setUploadProgress(i)
      await new Promise((resolve) => setTimeout(resolve, 200))
    }
  }

  const handleNextStep = async () => {
    if (currentStep === 0 && !uploadedFile) {
      toast({
        title: "No file selected",
        description: "Please upload a dataset file to continue.",
        variant: "destructive",
      })
      return
    }

    if (currentStep === 1) {
      if (!metadata.title || !metadata.description || !metadata.category) {
        toast({
          title: "Missing information",
          description: "Please fill in all required fields.",
          variant: "destructive",
        })
        return
      }
    }

    if (currentStep === 2 && !aiAnalysis) {
      await simulateAIAnalysis()
    }

    if (currentStep === 3) {
      await simulateIPFSUpload()
    }

    setCurrentStep((prev) => Math.min(prev + 1, steps.length - 1))
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-6">
            <div className="border-2 border-dashed border-border/40 rounded-lg p-8 text-center hover:border-primary/50 transition-colors">
              <input
                type="file"
                accept=".json,.csv,.xml"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-lg font-medium mb-2">Upload your dataset</p>
                <p className="text-sm text-muted-foreground mb-4">
                  Drag and drop or click to select JSON, CSV, or XML files (max 50MB)
                </p>
                <Button variant="outline">Choose File</Button>
              </label>
            </div>

            {uploadedFile && (
              <Card className="border-primary/20 bg-primary/5">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <FileText className="h-8 w-8 text-primary" />
                    <div className="flex-1">
                      <p className="font-medium">{uploadedFile.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB • {uploadedFile.type}
                      </p>
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
                <Input
                  id="title"
                  placeholder="e.g., UK Parliament Voting Records 2024"
                  value={metadata.title}
                  onChange={(e) => setMetadata((prev) => ({ ...prev, title: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">Category *</Label>
                <select
                  id="category"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  value={metadata.category}
                  onChange={(e) => setMetadata((prev) => ({ ...prev, category: e.target.value }))}
                >
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
              <Textarea
                id="description"
                placeholder="Describe your dataset, its contents, and potential use cases..."
                rows={4}
                value={metadata.description}
                onChange={(e) => setMetadata((prev) => ({ ...prev, description: e.target.value }))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="source">Data Source</Label>
              <Input
                id="source"
                placeholder="e.g., UK Parliament API, Official Records"
                value={metadata.source}
                onChange={(e) => setMetadata((prev) => ({ ...prev, source: e.target.value }))}
              />
            </div>

            <div className="space-y-2">
              <Label>Tags</Label>
              <div className="flex space-x-2">
                <Input
                  placeholder="Add a tag..."
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleAddTag()}
                />
                <Button onClick={handleAddTag} size="icon" variant="outline">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                {metadata.tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="flex items-center space-x-1">
                    <span>{tag}</span>
                    <button onClick={() => handleRemoveTag(tag)} className="ml-1 hover:text-destructive">
                      <X className="h-3 w-3" />
                    </button>
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
                  <p className="text-muted-foreground mb-4">
                    Our AI is analyzing your dataset for quality, completeness, and market value...
                  </p>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div className="bg-primary h-2 rounded-full animate-pulse" style={{ width: "60%" }} />
                  </div>
                </CardContent>
              </Card>
            ) : aiAnalysis ? (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Brain className="h-5 w-5 text-primary" />
                      <span>AI Quality Analysis</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-primary">{aiAnalysis.qualityScore}%</div>
                        <div className="text-sm text-muted-foreground">Overall Quality</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-accent">{aiAnalysis.completeness}%</div>
                        <div className="text-sm text-muted-foreground">Completeness</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-chart-2">{aiAnalysis.relevance}%</div>
                        <div className="text-sm text-muted-foreground">Relevance</div>
                      </div>
                    </div>

                    <div className="border-t pt-4">
                      <h4 className="font-semibold mb-2">AI Insights</h4>
                      <ul className="space-y-1">
                        {aiAnalysis.insights.map((insight, index) => (
                          <li key={index} className="flex items-start space-x-2 text-sm">
                            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                            <span>{insight}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-accent/20 bg-accent/5">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-semibold flex items-center space-x-2">
                          <Coins className="h-5 w-5 text-accent" />
                          <span>Suggested Price</span>
                        </h3>
                        <p className="text-sm text-muted-foreground">Based on quality and market analysis</p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-accent">{aiAnalysis.suggestedPrice} PYUSD</div>
                        <div className="text-sm text-muted-foreground">per license</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <Card>
                <CardContent className="p-6 text-center">
                  <Brain className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Ready for AI Analysis</h3>
                  <p className="text-muted-foreground mb-4">
                    Click continue to start the AI quality analysis of your dataset.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        )

      case 3:
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Cloud className="h-5 w-5 text-primary" />
                  <span>IPFS Upload</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">
                  Uploading your dataset to the InterPlanetary File System (IPFS) via Lighthouse for permanent,
                  decentralized storage.
                </p>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Upload Progress</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <Progress value={uploadProgress} className="w-full" />
                </div>

                {uploadProgress === 100 && (
                  <div className="flex items-center space-x-2 text-green-600">
                    <CheckCircle className="h-4 w-4" />
                    <span className="text-sm">Successfully uploaded to IPFS</span>
                  </div>
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
                <p className="text-muted-foreground mb-6">
                  Your dataset has been uploaded, analyzed, and is now available on the marketplace.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">+150 DataCoin</div>
                    <div className="text-sm text-muted-foreground">Governance Tokens Earned</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">#{Math.floor(Math.random() * 1000) + 1000}</div>
                    <div className="text-sm text-muted-foreground">Dataset ID</div>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Button className="bg-gradient-to-r from-primary to-accent">
                    View in Marketplace
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                  <Button variant="outline">Upload Another Dataset</Button>
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
      {/* Progress Steps */}
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-full border-2 ${
                  step.status === "completed"
                    ? "border-green-500 bg-green-500 text-white"
                    : step.status === "active"
                      ? "border-primary bg-primary text-white"
                      : "border-border bg-background text-muted-foreground"
                }`}
              >
                {step.status === "completed" ? (
                  <CheckCircle className="h-5 w-5" />
                ) : (
                  <span className="text-sm font-medium">{step.id + 1}</span>
                )}
              </div>
              <div className="mt-2 text-center">
                <div className="text-sm font-medium">{step.title}</div>
                <div className="text-xs text-muted-foreground hidden sm:block">{step.description}</div>
              </div>
            </div>
            {index < steps.length - 1 && (
              <div className={`mx-4 h-0.5 w-16 ${step.status === "completed" ? "bg-green-500" : "bg-border"}`} />
            )}
          </div>
        ))}
      </div>

      {/* Step Content */}
      <Card>
        <CardHeader>
          <CardTitle>{steps[currentStep].title}</CardTitle>
        </CardHeader>
        <CardContent>{renderStepContent()}</CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={() => setCurrentStep((prev) => Math.max(prev - 1, 0))}
          disabled={currentStep === 0}
        >
          Previous
        </Button>
        <Button
          onClick={handleNextStep}
          disabled={currentStep === steps.length - 1}
          className="bg-gradient-to-r from-primary to-accent hover:opacity-90"
        >
          {currentStep === steps.length - 2 ? "Publish Dataset" : "Continue"}
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
