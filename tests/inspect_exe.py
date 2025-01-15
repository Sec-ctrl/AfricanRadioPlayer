import pefile

# Path to the executable
exe_path = "C:\\Users\\Bruger\\Music\\Python\\African Radio Shuffle App\\dist\\SmoothAfricanRadioPlayer.exe"

# Load the executable with pefile
pe = pefile.PE(exe_path)

# Print general information
print("Executable Info:")
print(f"  Entry Point: 0x{pe.OPTIONAL_HEADER.AddressOfEntryPoint:X}")
print(f"  Image Base: 0x{pe.OPTIONAL_HEADER.ImageBase:X}")

# List all imported DLLs
print("\nImported DLLs:")
for entry in pe.DIRECTORY_ENTRY_IMPORT:
    print(f"  {entry.dll.decode()}")

# List all sections
print("\nSections:")
for section in pe.sections:
    print(f"  Name: {section.Name.decode().strip()}")
    print(f"    Virtual Address: 0x{section.VirtualAddress:X}")
    print(f"    Raw Size: {section.SizeOfRawData}")
    print(f"    Characteristics: 0x{section.Characteristics:X}")
    print()

# Close the PE object
pe.close()
