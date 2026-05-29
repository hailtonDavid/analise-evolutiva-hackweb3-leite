require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config({ path: "../.env" });

const PRIVATE_KEY = process.env.PRIVATE_KEY || "";
const SEPOLIA_RPC_URL = process.env.SEPOLIA_RPC_URL || process.env.RPC_URL || "";
const AMOY_RPC_URL = process.env.AMOY_RPC_URL || "";

function accounts() {
  return PRIVATE_KEY ? [PRIVATE_KEY] : [];
}

module.exports = {
  solidity: "0.8.24",
  paths: {
    sources: "../contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  },
  networks: {
    localhost: { url: "http://127.0.0.1:8545" },
    sepolia: { url: SEPOLIA_RPC_URL || "http://127.0.0.1:8545", accounts: accounts() },
    amoy: { url: AMOY_RPC_URL || "http://127.0.0.1:8545", accounts: accounts() }
  }
};
