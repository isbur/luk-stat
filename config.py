from pathlib import Path
import tomli_w as tomliw

workdir = Path("./projects/luk-electro")
number = len(list((workdir / Path("src")).glob("*.png"))) # Hopefully you didn't put anything unnecessary there

sol_img_ext = "png"
# atan
# problem_number_re_str = r'^\d{3}\S?$'
# luk-stat
# doc = {"problem_number_re_str": r'^\d{3}\.?\S?$'}
# luk-electro
doc = {"problem_number_re_str": r'^\d{4}\.?\S?$'}
with open(Path("./luk/config.toml"), "wb") as f:
    tomliw.dump(doc, f)
