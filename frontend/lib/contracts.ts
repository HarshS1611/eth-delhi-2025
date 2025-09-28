import type { Abi } from "viem"

/** Deployed addresses */
export const ADDR = {
  LSDC:    "0x2EA104BCdF3A448409F2dc626e606FdCf969a5aE",
  DIP:     "0x4E6c6e92902ACfAF4E1022896460781634C86D50",
  NFT:     "0xccfDc0c1F350C40C1fA92f892AA7d50fc1b83802",
  DATA_DAO:"0xcE1f1A61c9e9cebB350620C66485fC89dA018dF1",
  STAKE:   "0x97C20982dd35A5fBDA7da57A72b6ABB168Af8B7C",
} as const

/** Minimal ERC20 for reads/approve */
export const ERC20_ABI = [
  { type:"function", name:"decimals",  stateMutability:"view", inputs:[], outputs:[{type:"uint8"}]},
  { type:"function", name:"symbol",    stateMutability:"view", inputs:[], outputs:[{type:"string"}]},
  { type:"function", name:"balanceOf", stateMutability:"view", inputs:[{name:"a",type:"address"}], outputs:[{type:"uint256"}]},
  { type:"function", name:"allowance", stateMutability:"view", inputs:[{type:"address"},{type:"address"}], outputs:[{type:"uint256"}]},
  { type:"function", name:"approve",   stateMutability:"nonpayable", inputs:[{type:"address"},{type:"uint256"}], outputs:[{type:"bool"}]},
] as const satisfies Abi

/** DATA DAO */
export const DATA_DAO_ABI = [
  { type:"function", name:"nextDatasetId", stateMutability:"view", inputs:[], outputs:[{type:"uint256"}]},
  { type:"function", name:"datasets", stateMutability:"view",
    inputs:[{type:"uint256"}],
    outputs:[
      {name:"cid",type:"string"},
      {name:"title",type:"string"},
      {name:"tokenUri",type:"string"},
      {name:"creator",type:"address"},
      {name:"price",type:"uint256"},
      {name:"qualityScore",type:"uint8"},
      {name:"status",type:"uint8"},
      {name:"votes",type:"uint256"},
      {name:"tokenGated",type:"bool"},
      {name:"minTokenForBuy",type:"uint256"},
      {name:"minStakeForBuy",type:"uint256"},
    ],
  },
  { type:"function", name:"submitDataset", stateMutability:"nonpayable",
    inputs:[
      {name:"cid",type:"string"},
      {name:"title",type:"string"},
      {name:"tokenUri",type:"string"},
      {name:"price",type:"uint256"},
      {name:"qualityScore",type:"uint8"},
      {name:"tokenGated",type:"bool"},
      {name:"minTokenForBuy",type:"uint256"},
      {name:"minStakeForBuy",type:"uint256"},
    ],
    outputs:[]
  },
  { type:"function", name:"purchase", stateMutability:"nonpayable",
    inputs:[{name:"datasetId",type:"uint256"}], outputs:[] },
  { type:"function", name:"paymentToken", stateMutability:"view", inputs:[], outputs:[{type:"address"}] },
  { type: "function", name: "vote", stateMutability: "nonpayable",
  inputs: [{ name: "id", type: "uint256" }, { name: "approve", type: "bool" }],
  outputs: []
},
{ type: "function", name: "approvalVotes", stateMutability: "view",
  inputs: [], outputs: [{ type: "uint256" }]
},
{ type: "function", name: "hasVoted", stateMutability: "view",
  inputs: [{ type: "uint256" }, { type: "address" }],
  outputs: [{ type: "bool" }]
},
] as const satisfies Abi

/** STAKING */
export const STAKE_ABI = [
  // reads
  { type:"function", name:"stakeToken",   stateMutability:"view", inputs:[], outputs:[{type:"address"}]},
  { type:"function", name:"rewardsToken", stateMutability:"view", inputs:[], outputs:[{type:"address"}]},
  { type:"function", name:"stakedBalance",stateMutability:"view", inputs:[{name:"user",type:"address"}], outputs:[{type:"uint256"}]},
  { type:"function", name:"pendingRewards",stateMutability:"view", inputs:[{type:"address"}], outputs:[{type:"uint256"}]},
  { type:"function", name:"users", stateMutability:"view", inputs:[{type:"address"}], outputs:[
    {type:"uint256", name:"amount"},
    {type:"uint256", name:"tierIndex"},
    {type:"uint256", name:"stakedAt"},
    {type:"uint256", name:"lastRPT"},
    {type:"uint256", name:"boostUntil"},
    {type:"uint256", name:"boostBps"},
  ]},
  { type:"function", name:"tiers", stateMutability:"view", inputs:[{type:"uint256"}], outputs:[
    {type:"string",  name:"name"},
    {type:"uint256", name:"minStake"},
    {type:"uint256", name:"rewardsMultiplier"}, // percent (100 = 1.0x)
  ]},
  // writes
  { type:"function", name:"stake",   stateMutability:"nonpayable", inputs:[{type:"uint256"},{type:"uint256"}], outputs:[]},
  { type:"function", name:"unstake", stateMutability:"nonpayable", inputs:[{type:"uint256"}], outputs:[]},

  { type:"function", name:"pendingRewards", stateMutability:"view", inputs:[{name:"user",type:"address"}], outputs:[{type:"uint256"}]},
  { type:"function", name:"totalRewardsDistributed", stateMutability:"view", inputs:[], outputs:[{type:"uint256"}]},
  { type:"function", name:"claimRewards", stateMutability:"nonpayable", inputs:[], outputs:[]},
] as const

/** NFT minimal */
export const NFT_ABI = [
  { type:"function", name:"tokenURI", stateMutability:"view", inputs:[{type:"uint256"}], outputs:[{type:"string"}]},
  { type:"function", name:"ownerOf", stateMutability:"view", inputs:[{type:"uint256"}], outputs:[{type:"address"}]},
  { type:"function", name:"setApprovalForAll", stateMutability:"nonpayable", inputs:[{type:"address"},{type:"bool"}], outputs:[]},
] as const
