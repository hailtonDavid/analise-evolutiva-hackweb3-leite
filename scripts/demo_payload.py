from backend.core import create_sample

sample = create_sample(seed=123, adulterated=True)
print("Amostra:", sample["sample_id"])
print("Classificacao:", sample["analysis"]["classificacao"])
print("Hash:", sample["evidence_hash"])
print("Tx simulada:", sample["blockchain"]["tx_hash"])
