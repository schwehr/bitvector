import sys
content = open("BitVector/BitVectorNumPy.py").read()
import re
content = re.sub(r'total_bits \+= int\(val\.bit_count\(\)\)',
r'total_bits += int(int(val).bit_count())', content)
content = re.sub(r'total_bits \+= int\(last_val\.bit_count\(\)\)',
r'total_bits += int(int(last_val).bit_count())', content)
open("BitVector/BitVectorNumPy.py", "w").write(content)
