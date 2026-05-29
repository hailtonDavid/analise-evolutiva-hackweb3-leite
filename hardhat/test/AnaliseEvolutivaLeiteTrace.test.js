const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AnaliseEvolutivaLeiteTrace", function () {
  async function deployRegistry() {
    const Registry = await ethers.getContractFactory("AnaliseEvolutivaLeiteTrace");
    const registry = await Registry.deploy();
    await registry.waitForDeployment();
    return registry;
  }

  it("registra uma evidencia da cadeia do leite", async function () {
    const registry = await deployRegistry();
    const evidenceHash = ethers.keccak256(ethers.toUtf8Bytes("evidencia-demo-leite"));

    await expect(
      registry.registerEvidence(evidenceHash, "LEITE-20260529-0001", "PROD-001", "ipfs://demo", "APROVADO")
    ).to.emit(registry, "EvidenceRegistered");

    expect(await registry.exists(evidenceHash)).to.equal(true);
    const evidence = await registry.getEvidence(evidenceHash);
    expect(evidence.batchId).to.equal("LEITE-20260529-0001");
    expect(evidence.status).to.equal("APROVADO");
    expect(evidence.certified).to.equal(false);
  });

  it("emite certificacao digital para evidencia registrada", async function () {
    const registry = await deployRegistry();
    const evidenceHash = ethers.keccak256(ethers.toUtf8Bytes("evidencia-certificada"));

    await registry.registerEvidence(evidenceHash, "LOTE-A2A2-1", "PROD-A", "ipfs://laudo", "APROVADO");
    await expect(registry.certifyEvidence(evidenceHash, "ipfs://certificado-a2a2"))
      .to.emit(registry, "EvidenceCertified");

    expect(await registry.isCertified(evidenceHash)).to.equal(true);
    const evidence = await registry.getEvidence(evidenceHash);
    expect(evidence.certificateURI).to.equal("ipfs://certificado-a2a2");
  });

  it("bloqueia duplicidade de hash", async function () {
    const registry = await deployRegistry();
    const evidenceHash = ethers.keccak256(ethers.toUtf8Bytes("hash-repetido"));

    await registry.registerEvidence(evidenceHash, "LOTE-1", "PROD-1", "uri", "APROVADO");
    await expect(
      registry.registerEvidence(evidenceHash, "LOTE-1", "PROD-1", "uri", "APROVADO")
    ).to.be.revertedWithCustomError(registry, "EvidenceAlreadyRegistered");
  });
});
