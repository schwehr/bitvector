import sys
content = open("BitVector/BitVectorNumPy.py").read()
import re
content = re.sub(r'mask = np\.uint64\(~0\) >> np\.uint64\(64 - \(self\.size % 64\)\)',
r'''mask = np.uint64(0xFFFFFFFFFFFFFFFF) >> np.uint64(64 - (self.size % 64))''', content)
content = re.sub(r'~0x8000000000000000', r'0x7FFFFFFFFFFFFFFF', content)
open("BitVector/BitVectorNumPy.py", "w").write(content)
