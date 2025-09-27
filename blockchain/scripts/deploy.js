import "@nomicfoundation/hardhat-toolbox";

export default async function ({ getNamedAccounts, deployments, ethers }) {
  const { deploy, log } = deployments;
  const { deployer } = await getNamedAccounts();

  log("Deploying DIPDataNFT...");
  const nft = await deploy("DIPDataNFT", {
    from: deployer,
    args: [deployer],
    log: true,
  });

  log("Deploying DIPStaking...");
  const staking = await deploy("DIPStaking", {
    from: deployer,
    args: [
      "0x4E6c6e92902ACfAF4E1022896460781634C86D50", // DIP DataCoin
      "0x2EA104BCdF3A448409F2dc626e606FdCf969a5aE", // LSDC
      deployer,
    ],
    log: true,
  });

  log("Deploying DIPDataDAO...");
  const dao = await deploy("DIPDataDAO", {
    from: deployer,
    args: [
      "0x2EA104BCdF3A448409F2dc626e606FdCf969a5aE", // LSDC
      "0x4E6c6e92902ACfAF4E1022896460781634C86D50", // DIP DataCoin
      nft.address,
      process.env.DAO_TREASURY,
      process.env.OPS_TREASURY,
    ],
    log: true,
  });

  // --- wiring ---
  const nftContract = await ethers.getContract("DIPDataNFT", deployer);
  const daoContract = await ethers.getContract("DIPDataDAO", deployer);
  const stakingContract = await ethers.getContract("DIPStaking", deployer);

  const MINTER_ROLE = ethers.id("MINTER_ROLE");
  await (await nftContract.grantRole(MINTER_ROLE, dao.address)).wait();
  log("NFT: MINTER_ROLE granted to DAO");

  await (await daoContract.setSplit(8000, 1500, 300, 200)).wait();
  await (await daoContract.setRewardsSink(staking.address)).wait();
  log("DAO: split + rewards sink configured");

  await (await stakingContract.setDAO(dao.address)).wait();
  log("Staking: DAO set");

  log("✅ Deployments complete");
  log(`- DIPDataNFT: ${nft.address}`);
  log(`- DIPStaking: ${staking.address}`);
  log(`- DIPDataDAO: ${dao.address}`);
}

export const tags = ["all", "dip"];
