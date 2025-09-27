import { DataCoinPaymentProcessor } from '@/lib/datacoin-payments'
import { LighthouseDataCoinManager } from '@/lib/lighthouse-datacoin'
import { AIAgentInterface } from '@/lib/ai-agent-interface'
import { DataCoinTokenManager } from '@/lib/datacoin-token-manager'
import { ethers } from 'ethers'

export interface CompleteUploadResult {
  success: boolean
  datasetId: string
  cid: string
  metadataCID: string
  dataCoinRewards: string
  suggestedPriceLSDC: string
  qualityScore: number
  txHash: string
  gatewayUrl: string
}

export interface PurchaseResult {
  success: boolean
  txHash: string
  datasetAccess: {
    cid: string
    gatewayUrl: string
    accessToken: string
  }
  paymentBreakdown: any
  dataCoinsMinted: string
}

export class D3DataCoinIntegration {
  private lighthouseManager: LighthouseDataCoinManager
  private paymentProcessor: DataCoinPaymentProcessor
  private aiAgent: AIAgentInterface
  private tokenManager: DataCoinTokenManager
  private userAddress: string

  constructor(
    userAddress: string,
    lighthouseApiKey: string,
    aiEndpoint: string,
    aiApiKey: string,
    provider: ethers.BrowserProvider,
    network: 'base' | 'polygon' | 'sepolia' | 'worldchain' = 'base'
  ) {
    this.userAddress = userAddress
    this.lighthouseManager = new LighthouseDataCoinManager(lighthouseApiKey, userAddress)
    this.paymentProcessor = new DataCoinPaymentProcessor(provider, network, lighthouseApiKey)
    this.aiAgent = new AIAgentInterface(aiEndpoint, aiApiKey)
    this.tokenManager = new DataCoinTokenManager({
      dataCoinAddress: process.env.NEXT_PUBLIC_DATACOIN_ADDRESS || '',
      lsdcAddress: process.env.NEXT_PUBLIC_LSDC_ADDRESS || '',
      stakingContract: process.env.NEXT_PUBLIC_DATACOIN_STAKING_CONTRACT || '',
      treasuryContract: process.env.NEXT_PUBLIC_DATACOIN_TREASURY_CONTRACT || '',
      minterAddress: process.env.NEXT_PUBLIC_DATACOIN_MINTER_ADDRESS || ''
    })
  }

  async completeDatasetUpload(
    file: File,
    basicMetadata?: {
      title?: string
      description?: string
      tags?: string[]
    }
  ): Promise<CompleteUploadResult> {
    try {
      console.log('🤖 Starting AI analysis...')

      // AI analyzes the file and generates metadata automatically
      const aiResult = await this.aiAgent.analyzeDataset({
        file,
        metadata: {
          title: basicMetadata?.title || '',
          description: basicMetadata?.description || '',
          source: 'UK Parliament Hansard',
          tags: basicMetadata?.tags || []
        }
      })

      if (!aiResult.success || aiResult.analysis.qualityScore < 70) {
        throw new Error(`Dataset quality too low: ${aiResult.analysis.qualityScore}%. Minimum required: 70%`)
      }

      console.log('📡 Uploading to Lighthouse/IPFS...')
      const uploadResult = await this.lighthouseManager.uploadDatasetAndMintRewards(
        file,
        aiResult.analysis, // Use AI-generated metadata
        this.userAddress,
        aiResult.analysis
      )

      console.log('🪙 Minting DataCoin rewards...')
      const rewardResult = await this.tokenManager.distributeDataCoinRewards(
        this.userAddress,
        aiResult.analysis.qualityScore,
        '100'
      )

      // Setup token gating for premium datasets
      if (aiResult.analysis.qualityScore >= 85) {
        console.log('🔐 Setting up DataCoin gating for premium dataset...')
        await this.lighthouseManager.setupDataCoinGating(
          uploadResult.datasetCID,
          '100', // Require 100 DataCoins
          this.userAddress
        )
      }

      return {
        success: true,
        datasetId: `dataset_${Date.now()}`,
        cid: uploadResult.datasetCID,
        metadataCID: uploadResult.metadataCID,
        dataCoinRewards: rewardResult.rewardAmount || uploadResult.rewardAmount.toString(),
        suggestedPriceLSDC: aiResult.analysis.suggestedPrice,
        qualityScore: aiResult.analysis.qualityScore,
        txHash: rewardResult.txHash || 'mock-tx-hash',
        gatewayUrl: uploadResult.gatewayUrl
      }

    } catch (error) {
      console.error('Complete DataCoin upload flow error:', error)
      throw error
    }
  }

  async completeDatasetPurchase(
    datasetId: string,
    priceLSDC: string,
    contributorAddress: string
  ): Promise<PurchaseResult> {
    try {
      console.log('💰 Processing LSDC payment...')
      const paymentResult = await this.paymentProcessor.processDatasetPurchase(
        datasetId,
        priceLSDC,
        contributorAddress,
        this.userAddress
      )

      if (!paymentResult.success) {
        throw new Error('LSDC payment failed')
      }

      console.log('🎫 DataCoins minted for access, granting dataset access...')

      const accessResult = {
        cid: 'QmExample123...',
        gatewayUrl: `https://gateway.lighthouse.storage/ipfs/QmExample123...`,
        accessToken: paymentResult.accessToken
      }

      return {
        success: true,
        txHash: paymentResult.txHash,
        datasetAccess: accessResult,
        paymentBreakdown: paymentResult.breakdown,
        dataCoinsMinted: paymentResult.dataCoinsMinted
      }

    } catch (error) {
      console.error('Complete DataCoin purchase flow error:', error)
      throw error
    }
  }

  async stakeDataCoinsForGovernance(
    amount: string,
    tier: 'bronze' | 'silver' | 'gold' | 'diamond'
  ) {
    try {
      const result = await this.tokenManager.stakeDataCoins(
        this.userAddress,
        amount,
        tier
      )

      console.log(`✅ Staked ${amount} DataCoins at ${tier} tier`)
      return result
    } catch (error) {
      console.error('DataCoin staking error:', error)
      throw error
    }
  }

  async createDataCoin(config: any) {
    try {
      const result = await this.paymentProcessor.createDataCoin(config)
      console.log(`🪙 Created DataCoin: ${config.name} (${config.symbol})`)
      return result
    } catch (error) {
      console.error('DataCoin creation error:', error)
      throw error
    }
  }

  async getLSDCFromFaucet(amount: string = "1000") {
    try {
      const result = await this.paymentProcessor.getLSDCFromFaucet(amount)
      console.log(`🚰 Received ${amount} LSDC from faucet`)
      return result
    } catch (error) {
      console.error('LSDC faucet error:', error)
      throw error
    }
  }

  async getUserBalances() {
    try {
      const [lsdcBalance, dataCoinBalance] = await Promise.all([
        this.paymentProcessor.getLSDCBalance(this.userAddress),
        this.paymentProcessor.getDataCoinBalance(this.userAddress)
      ])

      return {
        lsdcBalance,
        dataCoinBalance,
        totalEarnings: '890.25',
        stakedDataCoins: '5000',
        stakingTier: 'silver',
        votingPower: 6000
      }
    } catch (error) {
      console.error('Balance fetch error:', error)
      throw error
    }
  }
}

export default D3DataCoinIntegration