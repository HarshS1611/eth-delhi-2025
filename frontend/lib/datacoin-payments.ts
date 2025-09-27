import { ethers } from 'ethers'
import lighthouse from '@lighthouse-web3/sdk'
import axios from 'axios'

export const DATACOIN_ADDRESSES = {
  base: process.env.NEXT_PUBLIC_DATACOIN_BASE || '',
  polygon: process.env.NEXT_PUBLIC_DATACOIN_POLYGON || '',
  sepolia: process.env.NEXT_PUBLIC_DATACOIN_SEPOLIA || '',
  worldchain: process.env.NEXT_PUBLIC_DATACOIN_WORLDCHAIN || ''
} as const

export const LSDC_ADDRESSES = {
  base: '0x' + '0'.repeat(40), // Mock LSDC Base
  polygon: '0x' + '1'.repeat(40), // Mock LSDC Polygon  
  sepolia: '0x' + '2'.repeat(40), // Mock LSDC Sepolia
  worldchain: '0x' + '3'.repeat(40) // Mock LSDC Worldchain
} as const

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

export interface PaymentBreakdown {
  total: string
  contributor: string
  dao: string
  ai: string
  lighthouse: string
  operations: string
}

export interface DataCoinPaymentResult {
  success: boolean
  txHash: string
  breakdown: PaymentBreakdown
  datasetId: string
  dataCoinsMinted: string
  accessToken: string
}

export class DataCoinPaymentProcessor {
  private provider: ethers.BrowserProvider
  private signer: ethers.Signer | null = null
  private dataCoinContract: ethers.Contract | null = null
  private lsdcContract: ethers.Contract | null = null
  private network: keyof typeof DATACOIN_ADDRESSES
  private lighthouseApiKey: string

  constructor(
    provider: ethers.BrowserProvider, 
    network: keyof typeof DATACOIN_ADDRESSES = 'base',
    lighthouseApiKey: string
  ) {
    this.provider = provider
    this.network = network
    this.lighthouseApiKey = lighthouseApiKey
  }

  async initialize() {
    try {
      this.signer = await this.provider.getSigner()

      // DataCoin ERC20 ABI
      const dataCoinABI = [
        'function balanceOf(address owner) view returns (uint256)',
        'function allowance(address owner, address spender) view returns (uint256)', 
        'function approve(address spender, uint256 amount) returns (bool)',
        'function transfer(address to, uint256 amount) returns (bool)',
        'function transferFrom(address from, address to, uint256 amount) returns (bool)',
        'function decimals() view returns (uint8)',
        'function mint(address to, uint256 amount) returns (bool)',
        'function totalSupply() view returns (uint256)',
        'function name() view returns (string)',
        'function symbol() view returns (string)'
      ]

      // LSDC Mock USDC ABI
      const lsdcABI = [
        'function balanceOf(address owner) view returns (uint256)',
        'function approve(address spender, uint256 amount) returns (bool)',
        'function transfer(address to, uint256 amount) returns (bool)',
        'function decimals() view returns (uint8)',
        'function faucet(uint256 amount) returns (bool)' // Mock faucet function
      ]

      if (DATACOIN_ADDRESSES[this.network]) {
        this.dataCoinContract = new ethers.Contract(
          DATACOIN_ADDRESSES[this.network],
          dataCoinABI,
          this.signer
        )
      }

      if (LSDC_ADDRESSES[this.network]) {
        this.lsdcContract = new ethers.Contract(
          LSDC_ADDRESSES[this.network],
          lsdcABI,
          this.signer
        )
      }

      console.log(`✅ DataCoin processor initialized on ${this.network}`)

    } catch (error) {
      console.error('DataCoin initialization failed:', error)
      throw error
    }
  }

  async createDataCoin(config: DataCoinConfig): Promise<any> {
    try {
      console.log('🪙 Creating DataCoin with config:', config)

      // Mock DataCoin creation for demo - integrate with 1MB.io API
      const createPayload = {
        name: config.name,
        symbol: config.symbol,
        totalSupply: config.totalSupply,
        network: config.network,
        allocations: {
          creator: config.creatorAllocation,
          liquidity: config.liquidityAllocation,
          contributor: config.contributorAllocation,
          treasury: 100 - (config.creatorAllocation + config.liquidityAllocation + config.contributorAllocation)
        },
        lockingToken: config.lockingToken,
        lockAmount: config.lockAmount,
        website: config.website,
        description: config.description,
        socialLinks: config.socialLinks
      }

      // In production, this would call 1MB.io API
      const mockResponse = {
        success: true,
        tokenAddress: '0x' + Math.random().toString(16).substring(2, 42).padStart(40, '0'),
        txHash: '0x' + Math.random().toString(16).substring(2, 66).padStart(64, '0'),
        initialPrice: this.calculateInitialPrice(config.lockAmount, config.liquidityAllocation),
        liquidityPoolAddress: '0x' + Math.random().toString(16).substring(2, 42).padStart(40, '0'),
        minterRole: await this.signer?.getAddress() || ''
      }

      console.log('✅ DataCoin created successfully:', mockResponse)
      return mockResponse

    } catch (error) {
      console.error('DataCoin creation failed:', error)
      throw error
    }
  }

  async processDatasetPurchase(
    datasetId: string,
    totalPriceLSDC: string,
    contributorAddress: string,
    buyerAddress: string
  ): Promise<DataCoinPaymentResult> {
    try {
      if (!this.lsdcContract || !this.dataCoinContract) {
        await this.initialize()
      }

      const priceInLSDC = ethers.parseUnits(totalPriceLSDC, 6) // LSDC has 6 decimals
      const breakdown = this.calculatePaymentBreakdown(totalPriceLSDC)

      // Check LSDC balance
      const balance = await this.lsdcContract!.balanceOf(buyerAddress)
      if (balance < priceInLSDC) {
        throw new Error(`Insufficient LSDC balance. Required: ${totalPriceLSDC}, Available: ${ethers.formatUnits(balance, 6)}`)
      }

      console.log('💰 Processing LSDC payment breakdown:', breakdown)

      // Execute LSDC transfers
      const transfers = [
        {
          to: contributorAddress,
          amount: ethers.parseUnits(breakdown.contributor, 6),
          label: 'Contributor payment'
        },
        {
          to: process.env.NEXT_PUBLIC_DAO_TREASURY || '',
          amount: ethers.parseUnits(breakdown.dao, 6), 
          label: 'DAO treasury'
        },
        {
          to: process.env.NEXT_PUBLIC_AI_TREASURY || '',
          amount: ethers.parseUnits(breakdown.ai, 6),
          label: 'AI infrastructure'
        },
        {
          to: process.env.NEXT_PUBLIC_LIGHTHOUSE_TREASURY || '',
          amount: ethers.parseUnits(breakdown.lighthouse, 6),
          label: 'Lighthouse storage'
        }
      ]

      let txHash = ''
      for (const transfer of transfers) {
        if (transfer.to && transfer.amount > 0n) {
          const tx = await this.lsdcContract!.transfer(transfer.to, transfer.amount)
          await tx.wait()
          if (!txHash) txHash = tx.hash
          console.log(`${transfer.label}: ${ethers.formatUnits(transfer.amount, 6)} LSDC to ${transfer.to}`)
        }
      }

      // Mint DataCoins to buyer as access token
      const dataCoinAmount = this.calculateDataCoinMintAmount(totalPriceLSDC)
      const mintTx = await this.dataCoinContract!.mint(buyerAddress, dataCoinAmount)
      await mintTx.wait()

      console.log(`🪙 Minted ${ethers.formatEther(dataCoinAmount)} DataCoins to buyer`)

      return {
        success: true,
        txHash,
        breakdown,
        datasetId,
        dataCoinsMinted: ethers.formatEther(dataCoinAmount),
        accessToken: `dc_${datasetId}_${Date.now()}`
      }

    } catch (error) {
      console.error('DataCoin payment processing error:', error)
      throw error
    }
  }

  async getLSDCFromFaucet(amount: string = "1000"): Promise<string> {
    try {
      if (!this.lsdcContract) {
        await this.initialize()
      }

      console.log(`🚰 Requesting ${amount} LSDC from faucet`)

      const amountWei = ethers.parseUnits(amount, 6)
      const tx = await this.lsdcContract!.faucet(amountWei)
      await tx.wait()

      console.log(`✅ Received ${amount} LSDC from faucet`)
      return tx.hash

    } catch (error) {
      console.error('LSDC faucet error:', error)
      throw error
    }
  }

  async getLSDCBalance(userAddress: string): Promise<string> {
    if (!this.lsdcContract) {
      await this.initialize()
    }

    const balance = await this.lsdcContract!.balanceOf(userAddress)
    return ethers.formatUnits(balance, 6)
  }

  async getDataCoinBalance(userAddress: string): Promise<string> {
    if (!this.dataCoinContract) {
      await this.initialize()
    }

    const balance = await this.dataCoinContract!.balanceOf(userAddress)
    return ethers.formatEther(balance)
  }

  private calculatePaymentBreakdown(totalLSDC: string): PaymentBreakdown {
    const total = parseFloat(totalLSDC)

    return {
      total: totalLSDC,
      contributor: (total * 0.70).toFixed(2), // 70% to contributor
      dao: (total * 0.15).toFixed(2),        // 15% to DAO
      ai: (total * 0.08).toFixed(2),         // 8% to AI
      lighthouse: (total * 0.05).toFixed(2), // 5% to Lighthouse
      operations: (total * 0.02).toFixed(2)  // 2% to operations
    }
  }

  private calculateDataCoinMintAmount(priceLSDC: string): bigint {
    // 1 LSDC = 10 DataCoins (configurable ratio)
    const ratio = 10n
    const priceWei = ethers.parseUnits(priceLSDC, 6)
    return (priceWei * ratio) / 1000000n // Convert from 6 decimals to 18 decimals
  }

  private calculateInitialPrice(lockAmount: string, liquidityAllocation: number): string {
    const lock = parseFloat(lockAmount)
    const liquidity = liquidityAllocation / 100
    const initialPrice = (lock * liquidity) / 1000000 // Basic calculation
    return initialPrice.toFixed(6)
  }
}