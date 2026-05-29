const hre = require("hardhat");

async function main() {
  const Registry = await hre.ethers.getContractFactory("AnaliseEvolutivaLeiteTrace");
  const registry = await Registry.deploy();
  await registry.waitForDeployment();
  const address = await registry.getAddress();
  console.log(`AnaliseEvolutivaLeiteTrace deployed to: ${address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
