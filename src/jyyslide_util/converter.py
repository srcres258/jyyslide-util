import json
import os
from importlib.resources import as_file

import shutil
import yaml
from jinja2 import Template
from pyquery import PyQuery

from jyyslide_util.util import *
from . import settings as st


def process_html_elements(before_html: str) -> str:
  """
  Process HTML elements in the given HTML content.

  Args:
      before_html (str): The HTML content to be processed.
  Returns:
      str: The processed HTML content.
  """

  temp_html = '<html><body>' + before_html + '</body></html>'
  page = PyQuery(temp_html)
  e = page
  for item in e('h1').parent():
    t = PyQuery(item)
    t.wrap("<div style='width:100%'>")
    t.wrap("<div class='center middle'>")
  class_data = {
    'ul': 'list-disc font-serif',
    'li': 'ml-8',
    'h2': 'text-xl mt-2 pb-2 font-sans',
    'h1': 'text-2xl mt-2 font-sans',
    'p': 'font-serif my-1',
    'pre': 'bg-gray-100 overflow-x-auto rounded p-2 mb-2 mt-2'
  }
  if st.img_center:
    class_data['img'] = 'center'
  for k, v in class_data.items():
    for item in e(k):
      t = PyQuery(item)
      t.add_class(v)
  page = e
  items = page('body').children()
  return ''.join([str(PyQuery(e)) for e in items])


def process_terminal(semi_html: str) -> str:
  """
  Process terminal-like blocks in the given HTML content.

  Args:
      semi_html (str): The HTML content to be processed.
  Returns:
      str: The processed HTML content.
  """

  semi_html += st.author_template
  st.author_template = ''
  temp = '<div>' + semi_html + '</div>'
  semi_html = process_html_elements(temp)
  return semi_html


def vertical_to_fragment(vertical: str) -> str:
  """
  Convert vertical separators to fragment separators in the given content.

  Args:
      vertical (str): The content with vertical separators.
  Returns:
      str: The content with fragment separators.
  """

  fragments = vertical.split(st.op_index_fragment)

  fragment_list = [md_util.md_to_html(fragments[0])]
  template = "<div class='fragment' data-fragment-index='{}'>{}</div>"

  for i in range(1, len(fragments)):
    fragment_list.append(template.format(i, md_util.md_to_html(fragments[i])))

  return ''.join(fragment_list)


def vertical_to_animate(vertical: str) -> str:
  """
  Convert vertical separators to animated sections in the given content.

  Args:
      vertical (str): The content with vertical separators.
  Returns:
      str: The content with animated sections.
  """

  animates = vertical.split(st.op_animate_section)

  animate_list = list()
  template = "{}"

  for i in range(len(animates)):
    animate_list.append(template.format(md_util.md_to_html(animates[i])))

  return ''.join(animate_list)


def horizontal_to_vertical(horizontal: str) -> str:
  verts_div_by_sec = horizontal.split(st.op_second_section)

  sections = list()
  template = "<section>{}</section>"

  cont_cond = lambda v: len(v) == 0 or v == '' or v.isspace()
  for vert_div_by_sec in verts_div_by_sec:
    if cont_cond(vert_div_by_sec):
      continue
    if st.op_animate_section in vert_div_by_sec:
      verts_div_by_anim = vert_div_by_sec.split(st.op_animate_section)
      template_anim = "<section data-auto-animate>{}</section>"
      for vert_div_by_anim in verts_div_by_anim:
        if cont_cond(vert_div_by_anim):
          continue
        sections.append(template_anim.format(
          process_terminal(vertical_to_animate(vert_div_by_anim))
        ))
    elif st.op_index_fragment in vert_div_by_sec:
      sections.append(template.format(
        process_terminal(vertical_to_fragment(vert_div_by_sec))
      ))
    else:
      sections.append(template.format(
        process_terminal(md_util.md_to_html(vert_div_by_sec))
      ))
  
  return ''.join(sections)


def md_devide_to_horizontal(content: str) -> str:
  """
  Divide the given Markdown content into horizontal sections.

  Args:
      content (str): The Markdown content to be divided.
  Returns:
      str: The HTML content with horizontal sections.
  """

  horizontals = content.split(st.op_first_section)

  sections = list()
  template = "<section>{}</section>"

  cont_cond = lambda v: len(v) == 0 or v == '' or v.isspace()
  for horizontal in horizontals:
    if cont_cond(horizontal):
      continue
    html_sec_sections = horizontal_to_vertical(horizontal)

    html = template.format(html_sec_sections)
    sections.append(html)
  
  return ''.join(sections)


def get_body(content: str) -> str:
  """
  Convert the given Markdown content to HTML body content.

  Args:
      content (str): The Markdown content to be converted.
  Returns:
      str: The HTML body content.
  """

  html_first_sections = md_devide_to_horizontal(content)
  return html_first_sections


def process_image_link() -> None:
  """
  Process image links in the global content variable.
  """

  def handler(link: str) -> str:
    new_name, err = file_util.get_image_to_target(
      link, st.filepath, st.images_foldpath
    )

    return (
      os.path.join('.', 'static', st.images_foldname, new_name)
      if err is False
      else ''
    ), err
  
  st.content = md_util.process_images(st.content, handler)


def process_front_matter() -> None:
  """
  Process front matter in the global content variable.
  Sets the author_template in the settings module.
  """

  if st.op_front_matter not in st.content:
    st.author_template = ''
    return
  
  parts = st.content.split(st.op_front_matter)

  front_matter = parts[0]
  st.content = ''.join(parts[1:])

  try:
    data = json.loads(front_matter)
  except Exception:
    data = yaml.load(front_matter, Loader=yaml.SafeLoader)
  
  for dept in data['departments']:
    new_name, err = file_util.get_image_to_target(
      dept['img'], st.filepath, st.images_foldpath
    )
    if err is False:
      dept['img'] = os.path.join(
        '.', 'static', st.images_foldname, new_name
      )
    dept['name'] = dept['name'].replace(' ', '&#12288;')
  
  st.author_template = st.author_template.render(
    author=data['author'],
    departments=data['departments']
  )


def process_static() -> None:
  """
  Process static files by copying them to the output directory.
  """

  if os.path.exists(st.output_foldpath):
    shutil.rmtree(st.output_foldpath)
  os.mkdir(st.output_foldpath)
  with as_file(st.static_path) as st_p:
    shutil.copytree(str(st_p), st.static_foldpath)


def converter(md_filepath: str) -> None:
  """
  Convert the given Markdown file to an HTML slide presentation.
  """

  st.init(md_filepath)
  process_static()

  st.template = Template(file_util.read(st.template_from))
  st.author_template = Template(file_util.read(st.authortemp_from))

  st.content = file_util.read(st.filepath)
  process_front_matter()
  process_image_link()

  st.title = ''.join(st.filename.split('.')[:-1])
  st.body = get_body(st.content)

  st.template = st.template.render(title=st.title, body=st.body)

  file_util.write(st.output_filepath, st.template)

