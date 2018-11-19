import spcid666
import os

dir = "test_SPCs"

print("get_total_size test: this should print X, 84, X, X, 228")
for filename in os.listdir(dir):
	if filename.endswith(".spc"):
		tag = spcid666.parse(os.path.join(dir, filename))
		if tag.extended is None:
			print("X")
		else:
			print(str(tag.extended.get_total_size()))
