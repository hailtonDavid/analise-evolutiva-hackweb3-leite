from __future__ import annotations

import hashlib
import os
from typing import Any, Dict, Mapping

try:
    from .core import canonical_json, utc_now
except ImportError:  # permite executar com: cd backend && python app.py
    from core import canonical_json, utc_now


def register_evidence(evidence: Mapping[str, Any]) -> Dict[str, Any]:
    """Registra a evidência na camada Web3.

    O MVP usa modo simulado por padrão para permitir avaliação sem carteira,
    RPC ou chaves privadas. O smart contract real está disponível em /contracts
    e o ambiente Hardhat está em /hardhat.
    """
    mode = os.getenv("WEB3_MODE", "simulated").lower()
    if mode != "simulated":
        # Segurança do MVP: não tenta usar chaves privadas nem RPC real sem implementação controlada.
        # Em produção, este ponto seria substituído por integração web3.py/ethers.
        raise RuntimeError("WEB3_MODE real ainda não está habilitado neste MVP. Use WEB3_MODE=simulated.")

    tx_source = {
        "evidence_hash": evidence["evidence_hash"],
        "batch_id": evidence["sample"]["batch_id"],
        "producer_id": evidence["sample"]["producer_id"],
        "status": evidence["analysis"]["status"],
        "registered_at": utc_now(),
        "mode": mode,
    }
    simulated_tx = "0x" + hashlib.sha256(canonical_json(tx_source).encode("utf-8")).hexdigest()
    return {
        "mode": mode,
        "chain_id": int(os.getenv("CHAIN_ID", "31337")),
        "contract_address": os.getenv("CONTRACT_ADDRESS", "simulated-contract"),
        "transaction_hash": simulated_tx,
        "registered_at": tx_source["registered_at"],
    }
