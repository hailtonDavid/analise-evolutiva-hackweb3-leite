// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title AnaliseEvolutivaLeiteTrace
/// @notice Smart contract demonstrativo para registrar evidencias da cadeia produtiva do leite.
/// @dev O arquivo bruto do laudo nao entra na blockchain. Registra-se apenas o hash e metadados minimos.
contract AnaliseEvolutivaLeiteTrace {
    enum EvidenceStatus { Pendente, Registrado, Validado, Reprovado }

    struct Evidence {
        string sampleId;
        string lotId;
        string evidenceHash;
        string classification;
        string metadataURI;
        address submitter;
        uint256 createdAt;
        EvidenceStatus status;
    }

    mapping(string => Evidence) private evidences;
    string[] private evidenceHashes;

    event EvidenceRegistered(
        string indexed evidenceHash,
        string sampleId,
        string lotId,
        string classification,
        address indexed submitter,
        uint256 createdAt
    );

    event EvidenceStatusChanged(string indexed evidenceHash, EvidenceStatus status, uint256 updatedAt);

    function registerEvidence(
        string calldata sampleId,
        string calldata lotId,
        string calldata evidenceHash,
        string calldata classification,
        string calldata metadataURI
    ) external {
        require(bytes(evidenceHash).length > 0, "hash obrigatorio");
        require(evidences[evidenceHash].createdAt == 0, "evidencia ja registrada");

        evidences[evidenceHash] = Evidence({
            sampleId: sampleId,
            lotId: lotId,
            evidenceHash: evidenceHash,
            classification: classification,
            metadataURI: metadataURI,
            submitter: msg.sender,
            createdAt: block.timestamp,
            status: EvidenceStatus.Registrado
        });

        evidenceHashes.push(evidenceHash);
        emit EvidenceRegistered(evidenceHash, sampleId, lotId, classification, msg.sender, block.timestamp);
    }

    function updateStatus(string calldata evidenceHash, EvidenceStatus status) external {
        require(evidences[evidenceHash].createdAt != 0, "evidencia inexistente");
        require(evidences[evidenceHash].submitter == msg.sender, "somente o registrante pode atualizar no MVP");
        evidences[evidenceHash].status = status;
        emit EvidenceStatusChanged(evidenceHash, status, block.timestamp);
    }

    function getEvidence(string calldata evidenceHash) external view returns (Evidence memory) {
        require(evidences[evidenceHash].createdAt != 0, "evidencia inexistente");
        return evidences[evidenceHash];
    }

    function totalEvidences() external view returns (uint256) {
        return evidenceHashes.length;
    }
}
