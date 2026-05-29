const fs = require("fs");
const path = require("path");
const hre = require("hardhat");

async function main() {
  const Registry = await hre.ethers.getContractFactory("AnaliseEvolutivaLeiteTrace");
  const registry = await Registry.deploy();
  await registry.waitForDeployment();
  const address = await registry.getAddress();
  const network = hre.network.name;
  const chainId = (await hre.ethers.provider.getNetwork()).chainId.toString();

  const deployment = {
    contract: "AnaliseEvolutivaLeiteTrace",
    address,
    network,
    chainId,
    deployedAt: new Date().toISOString()
  };

  const outDir = path.join(__dirname, "..", "deployments");
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, `${network}.json`), JSON.stringify(deployment, null, 2));

  console.log(`AnaliseEvolutivaLeiteTrace deployed to: ${address}`);
  console.log(`Network: ${network} | Chain ID: ${chainId}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
