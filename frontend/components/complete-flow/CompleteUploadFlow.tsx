"use client"

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  Upload, 
  FileText, 
  Brain, 
  Coins,
  CheckCircle,
  Loader2,
  DollarSign,
  Shield,
  Cloud,
  Trophy,
  Zap,
  Wallet
} from 'lucide-react'
import D3DataCoinIntegration, { type CompleteUploadResult } from '@/lib/datacoin-integration'
import { useToast } from '@/hooks/use-toast'

interface UploadStep {
  id: number
  title: string
  description: string
  icon: any
  completed: boolean
  current: boolean
}

export function CompleteUploadFlow() {
  const [currentStep, setCurrentStep] = useState(1)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadResult, setUploadResult] = useState<CompleteUploadResult | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const { toast } = useToast()

  const steps: UploadStep[] = [
    { id: 1, title: 'Upload Dataset', description: 'Select your parliamentary dataset', icon: Upload, completed: false, current: true },
    { id: 2, title: 'AI Analysis', description: 'Quality assessment & pricing', icon: Brain, completed: false, current: false },
    { id: 3, title: 'Lighthouse Storage', description: 'Permanent IPFS storage', icon: Cloud, completed: false, current: false },
    { id: 4, title: 'Mint DataCoins', description: 'Receive DataCoin rewards', icon: Coins, completed: false, current: false },
    { id: 5, title: 'Success!', description: 'Dataset live in marketplace', icon: Trophy, completed: false, current: false }
  ]

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (file.size > 100 * 1024 * 1024) { // 100MB limit
        toast({
          title: 'File Too Large',
          description: 'Maximum file size is 100MB',
          variant: 'destructive'
        })
        return
      }

      setSelectedFile(file)
      toast({
        title: 'File Selected',
        description: `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`
      })
    }
  }

  const updateStep = (stepId: number, completed: boolean = false) => {
    setCurrentStep(stepId)
  }

  const handleCompleteUpload = async () => {
    if (!selectedFile) {
      toast({
        title: 'No File Selected',
        description: 'Please select a dataset file to upload',
        variant: 'destructive'
      })
      return
    }

    setIsProcessing(true)
    setUploadProgress(10)
    console.log('🚀 Starting complete upload flow...')

    try {
      // Initialize DataCoin integration
      const integration = new D3DataCoinIntegration(
        '0x...', // User address from wallet
        process.env.NEXT_PUBLIC_LIGHTHOUSE_API_KEY || '',
        process.env.NEXT_PUBLIC_AI_AGENT_ENDPOINT || 'http://localhost:8000',
        process.env.NEXT_PUBLIC_AI_AGENT_API_KEY || 'demo-key',
        window.ethereum ? new ethers.BrowserProvider(window.ethereum) : null as any
      )

      // Step 2: AI Analysis
      updateStep(2)
      setUploadProgress(30)

      // Step 3: Lighthouse Storage  
      updateStep(3)
      setUploadProgress(60)

      // Step 4: Mint DataCoins
      updateStep(4)
      setUploadProgress(80)

      // Complete upload flow - AI generates metadata automatically
      const result = await integration.completeDatasetUpload(selectedFile)

      setUploadProgress(100)
      setUploadResult(result)
      updateStep(5, true)

      toast({
        title: 'Upload Successful!',
        description: `Dataset uploaded! Earned ${result.dataCoinRewards} DataCoins. Quality: ${result.qualityScore}%`
      })

    } catch (error) {
      toast({
        title: 'Upload Failed',
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        variant: 'destructive'
      })
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 p-6">
      {/* Header */}
      <div className="text-center space-y-4">
        <Badge variant="outline" className="mb-4">
          <Zap className="w-4 h-4 mr-2" />
          DataCoin Integration
        </Badge>
        <h1 className="text-4xl font-bold">
          Upload to
          <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent"> D³ DAO</span>
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          AI-powered dataset analysis, Lighthouse storage, LSDC payments, and DataCoin rewards - all in one seamless flow
        </p>
      </div>

      {/* Progress Steps */}
      <div className="relative">
        <div className="flex justify-between items-center mb-8">
          {steps.map((step, index) => {
            const Icon = step.icon
            return (
              <div key={step.id} className="flex flex-col items-center relative">
                <div className={`flex items-center justify-center w-16 h-16 rounded-full border-3 transition-all duration-300 ${
                  step.completed ? 'bg-green-500 border-green-500 text-white' :
                  currentStep === step.id ? 'bg-primary border-primary text-white' :
                  'border-gray-300 text-gray-400'
                }`}>
                  {step.completed ? <CheckCircle className="h-8 w-8" /> : <Icon className="h-8 w-8" />}
                </div>
                <div className="text-center mt-2">
                  <p className="text-sm font-medium">{step.title}</p>
                  <p className="text-xs text-muted-foreground">{step.description}</p>
                </div>
                {index < steps.length - 1 && (
                  <div className={`absolute top-8 left-16 w-full h-1 -ml-8 ${
                    step.completed ? 'bg-green-500' : 'bg-gray-300'
                  }`} style={{width: 'calc(100vw / 5)'}} />
                )}
              </div>
            )
          })}
        </div>

        {/* Progress Bar */}
        {isProcessing && (
          <div className="mb-6">
            <Progress value={uploadProgress} className="w-full h-3" />
            <p className="text-center mt-2 text-sm text-muted-foreground">
              Processing... {uploadProgress}%
            </p>
          </div>
        )}
      </div>

      <AnimatePresence mode="wait">
        {/* Step 1: File Upload Only */}
        {currentStep <= 1 && (
          <motion.div
            key="upload"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  Upload Dataset
                </CardTitle>
                <CardDescription>
                  Select your UK Parliament dataset file. Our AI will automatically analyze and generate metadata.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* File Upload */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-primary transition-colors cursor-pointer">
                  <input
                    type="file"
                    onChange={handleFileUpload}
                    accept=".json,.csv,.xml,.txt"
                    className="hidden"
                    id="dataset-upload"
                  />
                  <label htmlFor="dataset-upload" className="cursor-pointer">
                    <FileText className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                    <p className="text-xl font-medium mb-2">Click to upload dataset</p>
                    <p className="text-sm text-gray-500">JSON, CSV, XML up to 100MB</p>
                    <p className="text-xs text-muted-foreground mt-2">
                      ✨ AI will automatically generate title, description, and tags
                    </p>
                  </label>
                </div>

                {selectedFile && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex items-center justify-between p-4 bg-muted rounded-lg"
                  >
                    <div>
                      <p className="font-medium">{selectedFile.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <CheckCircle className="h-6 w-6 text-green-500" />
                  </motion.div>
                )}

                {/* LSDC Info Box */}
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center gap-3 mb-2">
                    <Wallet className="h-5 w-5 text-blue-600" />
                    <span className="font-medium text-blue-800">Using Lighthouse DataCoin (LSDC)</span>
                  </div>
                  <p className="text-sm text-blue-700">
                    Payments processed with LSDC mock tokens. Contributors earn DataCoins for quality datasets.
                    Need LSDC? Use the faucet in your wallet section.
                  </p>
                </div>

                {/* Action Button */}
                <div className="flex justify-center pt-4">
                  <Button 
                    onClick={handleCompleteUpload}
                    disabled={!selectedFile || isProcessing}
                    size="lg"
                    className="px-12"
                  >
                    {isProcessing ? (
                      <><Loader2 className="h-5 w-5 animate-spin mr-2" />Processing...</>
                    ) : (
                      <>🤖 Start AI Analysis & Upload</>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Processing Steps Display */}
        {isProcessing && currentStep > 1 && (
          <motion.div
            key="processing"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <Card>
              <CardContent className="p-8">
                <div className="text-center space-y-6">
                  <div className="relative">
                    <Loader2 className="h-16 w-16 animate-spin mx-auto text-primary" />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-8 h-8 bg-primary rounded-full opacity-20 animate-ping" />
                    </div>
                  </div>

                  <div>
                    <h3 className="text-2xl font-bold mb-2">{steps[currentStep - 1]?.title}</h3>
                    <p className="text-muted-foreground">{steps[currentStep - 1]?.description}</p>
                  </div>

                  <div className="grid md:grid-cols-3 gap-4 max-w-2xl mx-auto">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <Brain className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                      <p className="font-medium">AI Analysis</p>
                      <p className="text-sm text-muted-foreground">Auto-generating metadata</p>
                    </div>

                    <div className="p-4 bg-green-50 rounded-lg">
                      <Cloud className="h-8 w-8 text-green-500 mx-auto mb-2" />
                      <p className="font-medium">IPFS Storage</p>
                      <p className="text-sm text-muted-foreground">Permanent decentralized storage</p>
                    </div>

                    <div className="p-4 bg-purple-50 rounded-lg">
                      <Coins className="h-8 w-8 text-purple-500 mx-auto mb-2" />
                      <p className="font-medium">DataCoin Mint</p>
                      <p className="text-sm text-muted-foreground">Minting reward tokens</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Success Results */}
        {uploadResult && currentStep === 5 && (
          <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <Card className="border-green-200 bg-green-50">
              <CardContent className="p-8">
                <div className="text-center space-y-6">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 300, damping: 20, delay: 0.2 }}
                    className="relative"
                  >
                    <Trophy className="h-20 w-20 text-yellow-500 mx-auto" />
                    <div className="absolute -top-2 -right-2">
                      <CheckCircle className="h-8 w-8 text-green-500 bg-white rounded-full" />
                    </div>
                  </motion.div>

                  <div>
                    <h2 className="text-3xl font-bold text-green-600 mb-2">Upload Successful!</h2>
                    <p className="text-lg text-muted-foreground">
                      Your dataset is now live in the D³ marketplace
                    </p>
                  </div>

                  {/* Results Grid */}
                  <div className="grid md:grid-cols-4 gap-4 max-w-4xl mx-auto">
                    <div className="p-4 bg-white rounded-lg border">
                      <Coins className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                      <p className="font-bold text-2xl text-blue-600">{uploadResult.dataCoinRewards}</p>
                      <p className="text-sm text-muted-foreground">DataCoins Earned</p>
                    </div>

                    <div className="p-4 bg-white rounded-lg border">
                      <Brain className="h-8 w-8 text-purple-500 mx-auto mb-2" />
                      <p className="font-bold text-2xl text-purple-600">{uploadResult.qualityScore}%</p>
                      <p className="text-sm text-muted-foreground">AI Quality Score</p>
                    </div>

                    <div className="p-4 bg-white rounded-lg border">
                      <DollarSign className="h-8 w-8 text-green-500 mx-auto mb-2" />
                      <p className="font-bold text-2xl text-green-600">${uploadResult.suggestedPriceLSDC}</p>
                      <p className="text-sm text-muted-foreground">Suggested Price (LSDC)</p>
                    </div>

                    <div className="p-4 bg-white rounded-lg border">
                      <Shield className="h-8 w-8 text-orange-500 mx-auto mb-2" />
                      <p className="font-bold text-xs text-orange-600">{uploadResult.cid.substring(0, 12)}...</p>
                      <p className="text-sm text-muted-foreground">IPFS CID</p>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex justify-center gap-4">
                    <Button variant="outline" onClick={() => window.open(uploadResult.gatewayUrl)}>
                      View on IPFS
                    </Button>
                    <Button onClick={() => window.location.href = '/marketplace'}>
                      Browse Marketplace
                    </Button>
                    <Button 
                      onClick={() => {
                        setCurrentStep(1)
                        setSelectedFile(null)
                        setUploadResult(null)
                        setUploadProgress(0)
                      }}
                      variant="secondary"
                    >
                      Upload Another
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}