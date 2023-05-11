
def deserializeRecord(record):
	return {
	  "capsule": Capsule.from_bytes(deserializeFrom(record["capsule"])),
	  "ciphertext": deserializeFrom(record["content"])
	}