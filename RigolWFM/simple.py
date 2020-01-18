import wfm1102e
from pprint import pprint
# Instantiate DS1000E object
target = wfm1102e.Wfm1102e.from_file("../wfm/DS1102E.wfm")

# Print bootloader section info
print("Header")
print("----------")
print(hex(target.header.magic[0]), hex(target.header.magic[1]))

print("Header")
pprint(vars(target.header))
print()
print("time header")
pprint(vars(target.header.time1))
print()
print("trigger header")
pprint(vars(target.header.trigger1))
