import os
import shutil

here = os.path.dirname(os.path.abspath(__file__))
out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
os.makedirs(out_dir, exist_ok=True)
shutil.copyfile(
    os.path.join(here, "entry.png"),
    os.path.join(out_dir, "entry.png"),
)
