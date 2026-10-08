# TP 01: SHA-256 hashing, block chaining, and Proof of Work

This laboratory explores the core foundations of blockchain systems:
cryptographic hashing, immutable ledger data structures, Proof of Work (PoW)
consensus, and the mechanics of tamper-evident history.

## Laboratory contents

- Specification: [TP01.pdf](./TP01.pdf) containing the laboratory assignment
  and theoretical guidelines.
- Implementation: [main.ipynb](./main.ipynb) containing executable Python
  implementations, test scenarios, and performance evaluations.

## Covered concepts

### 1. SHA-256 cryptographic hashing
- Output uniformity: generation of 256-bit (64 hexadecimal characters) digests
  regardless of input size.
- Avalanche effect: quantifying bit-level and character-level divergence
  caused by single-character modifications in payload strings.

### 2. Block modeling and chaining
- Internal block anatomy: key-value structure storing `index`, `donnees`,
  `nonce`, `hash_precedent`, and `hash`.
- Genesis block: initialization with a designated zero-hash predecessor string.
- Ledger linking: cryptographic references ensuring each block commits to the
  complete history preceding it.
- Transaction accounting: parsing transactional payloads and computing
  participant balances over sequential blocks.

### 3. Proof of work mining
- Target difficulty: enforcing hash prefixes with $k$ hexadecimal zeros.
- Nonce iteration: brute-force search space requiring an average of $16^k$
  computational attempts per block.

### 4. Integrity verification and visualization
- Chain validation pipeline: sequential checks confirming hash recalculation,
  difficulty target adherence, and predecessor hash integrity.
- ASCII pipeline visualization: visual representation of block sequences and
  cryptographic linkages.

### 5. Difficulty scaling and computational complexity
- Exponential scaling: quantitative comparison between target difficulty 4 and
  difficulty 5.
- Mining throughput: calculating hash processing rates (hashes per second) and
  extrapolating wall-clock time requirements for higher difficulties.

### 6. Tampering and re-mining cost
- Attack simulation: altering committed historical payload data to demonstrate
  instantaneous downstream chain invalidation.
- Cascading re-mining overhead: empirical comparison proving that altering an
  older block requires re-mining every subsequent block, making historical
  tampering computationally prohibitive compared to modifying recent head blocks.

## Tech stack

- Language: Python 3
- Environment: Jupyter Notebook
- Standard modules: `hashlib`, `time`

Authored by Youssef Fellah.
Developed for the Engineering Cycle at Mundiapolis University.
