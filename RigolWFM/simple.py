import wfm1102e

# Instantiate DS4000 object
target = wfm1102e.Wfm1102e.from_file("../wfm/DS1102E.wfm")

# Print bootloader section info
print("Header")
print("----------")
print(hex(target.header.magic[0]),hex(target.header.magic[1]))
print(target)
