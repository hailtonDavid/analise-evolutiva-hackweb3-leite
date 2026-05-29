// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.24;

/// @title AnaliseEvolutivaLeiteTrace
/// @notice Registro Web3 de evidências da cadeia produtiva do leite.
/// @dev O contrato mantém dados mínimos on-chain e preserva o laudo completo off-chain.
contract AnaliseEvolutivaLeiteTrace {
    struct Evidence {
        bytes32 evidenceHash;
        string batchId;
        string producerId;
        string analysisURI;
        string status;
        address registrar;
        uint256 registeredAt;
        bool exists;
        bool certified;
        string certificateURI;
        address certifier;
        uint256 certifiedAt;
    }

    mapping(bytes32 => Evidence) private evidences;

    event EvidenceRegistered(
        bytes32 indexed evidenceHash,
        string batchId,
        string producerId,
        string status,
        address indexed registrar,
        uint256 registeredAt
    );

    event EvidenceCertified(
        bytes32 indexed evidenceHash,
        string certificateURI,
        address indexed certifier,
        uint256 certifiedAt
    );

    error EvidenceAlreadyRegistered(bytes32 evidenceHash);
    error EvidenceAlreadyCertified(bytes32 evidenceHash);
    error EvidenceNotFound(bytes32 evidenceHash);
    error EmptyHash();
    error EmptyCertificateURI();

    /// @notice Registra a prova de integridade de uma análise da cadeia do leite.
    /// @dev O analysisURI pode apontar para IPFS, storage público ou referência controlada pela aplicação.
    function registerEvidence(
        bytes32 evidenceHash,
        string calldata batchId,
        string calldata producerId,
        string calldata analysisURI,
        string calldata status
    ) external {
        if (evidenceHash == bytes32(0)) {
            revert EmptyHash();
        }
        if (evidences[evidenceHash].exists) {
            revert EvidenceAlreadyRegistered(evidenceHash);
        }

        evidences[evidenceHash] = Evidence({
            evidenceHash: evidenceHash,
            batchId: batchId,
            producerId: producerId,
            analysisURI: analysisURI,
            status: status,
            registrar: msg.sender,
            registeredAt: block.timestamp,
            exists: true,
            certified: false,
            certificateURI: "",
            certifier: address(0),
            certifiedAt: 0
        });

        emit EvidenceRegistered(evidenceHash, batchId, producerId, status, msg.sender, block.timestamp);
    }

    /// @notice Emite uma certificação digital para uma evidência previamente registrada.
    /// @dev No MVP, representa certificação de lote aprovado, auditoria ou selo de rastreabilidade.
    function certifyEvidence(bytes32 evidenceHash, string calldata certificateURI) external {
        if (!evidences[evidenceHash].exists) {
            revert EvidenceNotFound(evidenceHash);
        }
        if (evidences[evidenceHash].certified) {
            revert EvidenceAlreadyCertified(evidenceHash);
        }
        if (bytes(certificateURI).length == 0) {
            revert EmptyCertificateURI();
        }

        Evidence storage evidence = evidences[evidenceHash];
        evidence.certified = true;
        evidence.certificateURI = certificateURI;
        evidence.certifier = msg.sender;
        evidence.certifiedAt = block.timestamp;

        emit EvidenceCertified(evidenceHash, certificateURI, msg.sender, block.timestamp);
    }

    function exists(bytes32 evidenceHash) external view returns (bool) {
        return evidences[evidenceHash].exists;
    }

    function isCertified(bytes32 evidenceHash) external view returns (bool) {
        if (!evidences[evidenceHash].exists) {
            revert EvidenceNotFound(evidenceHash);
        }
        return evidences[evidenceHash].certified;
    }

    function getEvidence(bytes32 evidenceHash) external view returns (Evidence memory) {
        if (!evidences[evidenceHash].exists) {
            revert EvidenceNotFound(evidenceHash);
        }
        return evidences[evidenceHash];
    }
}
