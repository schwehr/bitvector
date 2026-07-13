# BitVector

The `BitVector` module provides a memory-efficient packed representation of bit
vectors and methods for the processing of such vectors.

This is a modern Python fork from Avi Kak's BitVector 3.5.0.

## Installation

You can install it if available from your preferred package manager (or see
`Development` section for local setup): This project uses `uv` for dependency
management.

```bash
# Clone the repository
git clone https://github.com/schwehr/bitvector-modern
cd bitvector-modern

# Set up the virtual environment and install
uv sync
```

## Quick Start

You can execute the code in `BitVector.py` directly in the project directory.

To see a working example of the `BitVector` module, see the file:
[`examples/demo.py`](https://github.com/schwehr/bitvector-modern/blob/main/examples/demo.py)

```python
from BitVector import BitVector

# Create a BitVector
bv = BitVector(intVal=42, size=8)
print(bv)
```
