import wfm4

# Instantiate DS4000 object
target = wfm4.Wfm4.from_file("DS4022-B.wfm")

# Print bootloader section info
print("Header")
print("----------")
print(hex(target.header.magic[0]),hex(target.header.magic[1]))
print(f"Scope: {target.header.scope_info}")
