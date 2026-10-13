"""Warm grade + soft vignette for the raw renders."""
import sys
import numpy as np
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert("RGB")).astype(np.float32) / 255
h, w, _ = im.shape
# warm: lift reds, cool down blues a touch in the shadows
im = im * np.array([1.03, 1.0, 0.93])
im = np.clip(im, 0, 1) ** np.array([0.97, 1.0, 1.04])
# vignette
y, x = np.mgrid[0:h, 0:w]
r = np.sqrt(((x - w * 0.47) / w) ** 2 + ((y - h * 0.4) / h) ** 2)
v = 1 - 0.38 * np.clip((r - 0.28) / 0.45, 0, 1) ** 1.6
im = im * v[..., None]
Image.fromarray((np.clip(im, 0, 1) * 255).astype(np.uint8)).save(dst, quality=93)
print("graded", dst)
