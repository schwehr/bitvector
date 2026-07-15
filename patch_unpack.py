import sys
content = open("BitVector/BitVectorNumPy.py").read()
import re
content = re.sub(r'return int\(np\.unpackbits\(self\.vector\.view\(np\.uint8\)\)\.sum\(\)\) - \(64 - self\.size % 64 if self\.size % 64 else 0\) if len\(self\.vector\) > 0 else 0',
r'''if len(self.vector) == 0:
            return 0

        # Unpackbits works on uint8, but the bits in a uint64 might need to be masked properly depending on endianness or how bits are packed.
        # Alternatively, we can use a simpler approach summing bits directly or relying on population counts.
        # But wait, np.unpackbits unpacks bytes. Since our implementation treats the right-most bits of the last 64-bit int as padding (because size might not be a multiple of 64),
        # we can just zero out those padding bits and sum the popcount.
        # An easier way for np is to count bits properly:
        total_bits = 0
        for val in self.vector[:-1]:
            total_bits += int(val.bit_count())

        if len(self.vector) > 0:
            last_val = self.vector[-1]
            if self.size % 64 != 0:
                # Mask out unused bits in the last uint64
                mask = np.uint64(~0) >> np.uint64(64 - (self.size % 64))
                last_val = last_val & mask
            total_bits += int(last_val.bit_count())
        return total_bits''', content)
open("BitVector/BitVectorNumPy.py", "w").write(content)
