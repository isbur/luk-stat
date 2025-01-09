from pathlib import Path

workdir = Path("./projects/luk-osc")
number = len(list((workdir / Path("src")).glob("*.png"))) # Hopefully you didn't put anything unnecessary there

sol_img_ext = "png"

