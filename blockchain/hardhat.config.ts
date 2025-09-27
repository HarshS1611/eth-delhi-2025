import "dotenv/config";
import "hardhat-deploy";
import "@nomicfoundation/hardhat-toolbox";

const { SEPOLIA_RPC_URL, PRIVATE_KEY, ETHERSCAN_API_KEY } = process.env;

export default {
  solidity: "0.8.20",
  namedAccounts: {
    deployer: { default: 0 },
  },
  networks: {
    sepolia: {
      url: SEPOLIA_RPC_URL ?? "",
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      chainId: 11155111,
    },
  },
  etherscan: {
    apiKey: ETHERSCAN_API_KEY ?? "",
  },
};
