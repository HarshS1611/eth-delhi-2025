import lighthouse from '@lighthouse-web3/sdk'
import axios from 'axios'

export interface DataCoinConfig {
  name: string
  symbol: string
  totalSupply: string
  network: 'base' | 'polygon' | 'sepolia' | 'worldchain'
  creatorAllocation: number
  liquidityAllocation: number  
  contributorAllocation: number
  lockingToken: 'USDC' | 'WETH' | 'LSDC'
  lockAmount: string
  website: string
  description: string
  iconImage?: File
  bannerImage?: File
  socialLinks?: {
    telegram?: string
    farcaster?: string
    twitter?: string
    github?: string
    linkedin?: string
  }
}

export interface DataCoinResponse {
  success: boolean
  tokenAddress: string
  txHash: string
  initialPrice: string
  liquidityPoolAddress: string
  minterRole?: string
}

export interface UploadResult {
  success: boolean
  datasetCID: string
  metadataCID: string
  rewardAmount: number
  suggestedPrice: string
  qualityScore: number
  gatewayUrl: string
}

export class LighthouseDataCoinManager {
  private apiKey: string
  private walletAddress: string

  constructor(apiKey: string, walletAddress: string) {
    this.apiKey = apiKey
    this.walletAddress = walletAddress
  }

  async createD3DataCoin(config: DataCoinConfig): Promise<DataCoinResponse> {
    try {
      console.log('🪙 Creating DataCoin with Lighthouse integration...')

      // This would integrate with 1MB.io API in production
      const createTokenPayload = {
        name: config.name,
        symbol: config.symbol,
        totalSupply: config.totalSupply,
        decimals: 18,
        network: config.network,

        // Token allocations
        allocations: {
          creator: config.creatorAllocation,
          liquidity: config.liquidityAllocation,
          contributor: config.contributorAllocation,
          treasury: 100 - (config.creatorAllocation + config.liquidityAllocation + config.contributorAllocation)
        },

        // Locking configuration
        lockingToken: config.lockingToken,
        lockAmount: config.lockAmount,

        // Project metadata
        website: config.website,
        description: config.description,
        socialLinks: config.socialLinks,

        // Creator info
        creatorAddress: this.walletAddress
      }

      // Mock response for development - replace with actual 1MB.io API call
      const mockResponse: DataCoinResponse = {
        success: true,
        tokenAddress: '0x' + Math.random().toString(16).substring(2, 42).padStart(40, '0'),
        txHash: '0x' + Math.random().toString(16).substring(2, 66).padStart(64, '0'),
        initialPrice: this.calculateInitialPrice(config.lockAmount, config.liquidityAllocation),
        liquidityPoolAddress: '0x' + Math.random().toString(16).substring(2, 42).padStart(40, '0'),
        minterRole: this.walletAddress
      }

      console.log('✅ DataCoin created successfully:', {
        name: config.name,
        symbol: config.symbol,
        tokenAddress: mockResponse.tokenAddress,
        initialPrice: mockResponse.initialPrice
      })

      return mockResponse

    } catch (error) {
      console.error('❌ DataCoin creation failed:', error)
      throw new Error(`Failed to create DataCoin: ${error}`)
    }
  }

  async uploadDatasetAndMintRewards(
    file: File,
    aiGeneratedMetadata: any,
    contributorAddress: string,
    aiAnalysisResult: any
  ): Promise<UploadResult> {
    try {
      console.log('📡 Uploading dataset to Lighthouse/IPFS...')

      // Upload dataset to Lighthouse
      const uploadResponse = await lighthouse.upload([file], this.apiKey)
      const cid = uploadResponse.data.Hash

      // Create comprehensive metadata including AI analysis
      const completeMetadata = {
        ...aiGeneratedMetadata,
        dataset: {
          cid,
          filename: file.name,
          size: file.size,
          uploadedAt: new Date().toISOString(),
          contributor: contributorAddress
        },
        aiAnalysis: {
          qualityScore: aiAnalysisResult.qualityScore,
          confidence: aiAnalysisResult.confidence,
          suggestedPrice: aiAnalysisResult.suggestedPrice,
          categories: aiAnalysisResult.categories,
          noveltyScore: aiAnalysisResult.noveltyScore,
          utilityScore: aiAnalysisResult.utilityScore,
          summary: aiAnalysisResult.summary,
          recommendations: aiAnalysisResult.recommendations
        },
        lighthouse: {
          network: 'ipfs',
          gateway: `https://gateway.lighthouse.storage/ipfs/${cid}`
        }
      }

      // Upload metadata to IPFS
      const metadataResponse = await lighthouse.uploadText(
        JSON.stringify(completeMetadata, null, 2),
        this.apiKey,
        `${file.name}-metadata.json`
      )

      // Calculate DataCoin rewards based on quality
      const rewardAmount = this.calculateDataCoinRewards(
        aiAnalysisResult.qualityScore,
        aiAnalysisResult.confidence,
        file.size
      )

      console.log('✅ Dataset uploaded successfully:', {
        cid,
        metadataCID: metadataResponse.data.Hash,
        rewardAmount,
        qualityScore: aiAnalysisResult.qualityScore
      })

      return {
        success: true,
        datasetCID: cid,
        metadataCID: metadataResponse.data.Hash,
        rewardAmount,
        suggestedPrice: aiAnalysisResult.suggestedPrice,
        qualityScore: aiAnalysisResult.qualityScore,
        gatewayUrl: `https://gateway.lighthouse.storage/ipfs/${cid}`
      }

    } catch (error) {
      console.error('❌ Dataset upload failed:', error)
      throw new Error(`Dataset upload failed: ${error}`)
    }
  }

  async setupDataCoinGating(
    cid: string,
    requiredDataCoinAmount: string,
    userAddress: string,
    signedMessage?: string
  ) {
    try {
      console.log('🔐 Setting up DataCoin token gating...')

      // Access conditions for DataCoin token gating
      const accessConditions = [
        {
          id: 1,
          chain: "base", // or the network where DataCoin is deployed
          method: "balanceOf",
          standardContractType: "ERC20",
          contractAddress: process.env.NEXT_PUBLIC_DATACOIN_ADDRESS || '',
          returnValueTest: {
            comparator: ">=",
            value: ethers.parseEther(requiredDataCoinAmount).toString()
          },
          parameters: [":userAddress"]
        }
      ]

      const aggregator = "([1])"

      // Apply access conditions using Lighthouse
      if (signedMessage) {
        const response = await lighthouse.applyAccessCondition(
          userAddress,
          cid,
          signedMessage,
          accessConditions,
          aggregator
        )

        console.log('✅ DataCoin gating applied successfully')
        return {
          success: true,
          accessConditions,
          cid,
          requiredAmount: requiredDataCoinAmount
        }
      } else {
        // Mock response for development
        console.log('✅ DataCoin gating configured (mock):', {
          cid,
          requiredAmount: requiredDataCoinAmount,
          conditions: accessConditions
        })

        return {
          success: true,
          accessConditions,
          cid,
          requiredAmount: requiredDataCoinAmount
        }
      }

    } catch (error) {
      console.error('❌ DataCoin gating setup failed:', error)
      throw new Error(`Token gating setup failed: ${error}`)
    }
  }

  async getLSDCFromFaucet(walletAddress: string, amount: string = "1000"): Promise<any> {
    try {
      console.log(`🚰 Requesting ${amount} LSDC from faucet for ${walletAddress}`)

      // Mock LSDC faucet - in production this would call the actual faucet contract
      const mockFaucetResponse = {
        success: true,
        txHash: '0x' + Math.random().toString(16).substring(2, 66).padStart(64, '0'),
        amount,
        tokenAddress: process.env.NEXT_PUBLIC_LSDC_ADDRESS || '0x' + '0'.repeat(40),
        network: 'testnet'
      }

      console.log('✅ LSDC faucet request successful:', mockFaucetResponse)
      return mockFaucetResponse

    } catch (error) {
      console.error('❌ LSDC faucet request failed:', error)
      throw new Error(`LSDC faucet failed: ${error}`)
    }
  }

  async getDatasetInfo(cid: string): Promise<any> {
    try {
      // Get file info from Lighthouse
      const fileInfo = await lighthouse.getFileInfo(cid)

      return {
        success: true,
        cid,
        fileInfo,
        gatewayUrl: `https://gateway.lighthouse.storage/ipfs/${cid}`
      }

    } catch (error) {
      console.error('❌ Failed to get dataset info:', error)
      throw error
    }
  }

  private calculateDataCoinRewards(
    qualityScore: number,
    confidence: number,
    fileSize: number
  ): number {
    // Base reward calculation
    const baseReward = 100 // Base DataCoins

    // Quality multiplier
    const qualityMultiplier = qualityScore >= 90 ? 2.0 : 
                             qualityScore >= 80 ? 1.5 : 
                             qualityScore >= 70 ? 1.0 : 0.5

    // Confidence bonus
    const confidenceBonus = confidence >= 95 ? 1.2 : 
                           confidence >= 85 ? 1.1 : 1.0

    // Size factor (larger datasets get slight bonus)
    const sizeMB = fileSize / (1024 * 1024)
    const sizeBonus = Math.min(1.5, 1.0 + (sizeMB / 100))

    const totalReward = Math.floor(baseReward * qualityMultiplier * confidenceBonus * sizeBonus)

    return Math.max(50, totalReward) // Minimum 50 DataCoins
  }

  private calculateInitialPrice(lockAmount: string, liquidityAllocation: number): string {
    const lock = parseFloat(lockAmount)
    const liquidity = liquidityAllocation / 100
    const initialPrice = (lock * liquidity) / 1000000 // Basic price calculation
    return initialPrice.toFixed(6)
  }
}

export default LighthouseDataCoinManager