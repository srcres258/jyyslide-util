import os
from argparse import ArgumentParser

from jinja2 import Template
from simple_toml_configurator import Configurator


settings_abspath = os.path.split(os.path.realpath(__file__))[0]
projects_abspath = os.path.abspath(os.path.join(settings_abspath, ".."))

static_path = os.path.join(projects_abspath, "src", "static")
backup_path = os.path.join(projects_abspath, "src", "backup")
template_from = os.path.join(backup_path, "template", "basetemp.html")
authortemp_from = os.path.join(backup_path, "template", "authortemp.html")

op_first_section = "\n---\n"
op_second_section = "\n----\n"
op_animate_section = "\n++++\n"
op_index_fragment = "\n--\n"
op_front_matter = "\n+++++\n"

# file information
filename = str()
filepath = str()
output_foldname = "dist"
output_filename = "index.html"
output_foldpath = str()
output_filepath = str()
static_foldpath = str()
images_foldname = "img"
images_foldpath = str()

content = str() # Markdown content

template: str | Template = str() # HTML content
title = str()
body = str()

img_center = True

# author information
author_template: str | Template = str()


def init(target_filepath: str) -> None:
  global filename, filepath, output_foldname, output_filename, output_foldpath, output_filepath, static_foldpath, images_foldpath

  filename = os.path.basename(target_filepath)
  filepath = os.path.abspath(target_filepath)
  output_foldpath = os.path.join(filepath.split(filename)[0], output_foldname)
  output_filepath = os.path.join(output_foldpath, output_filename)

  static_foldpath = os.path.join(output_foldpath, "static")
  images_foldpath = os.path.join(static_foldpath, images_foldname)
