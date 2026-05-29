// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.24;

/// @title AnaliseEvolutivaLeiteTrace
/// @notice Registro Web3 de evidências da cadeia produtiva do leite.
/// @dev O contrato registra apenas o hash da evidência e metadados mínimos.
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

    error EvidenceAlreadyRegistered(bytes32 evidenceHash);
    error EvidenceNotFound(bytes32 evidenceHash);
    error EmptyHash();

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
            exists: true
        });

        emit EvidenceRegistered(evidenceHash, batchId, producerId, status, msg.sender, block.timestamp);
    }

    function exists(bytes32 evidenceHash) external view returns (bool) {
        return evidences[evidenceHash].exists;
    }

    function getEvidence(bytes32 evidenceHash) external view returns (Evidence memory) {
        if (!evidences[evidenceHash].exists) {
            revert EvidenceNotFound(evidenceHash);
        }
        return evidences[evidenceHash];
    }
}
