import re
from typing import List, Union, Tuple, Callable
from markdown import markdown, Extension
from markdown.blockprocessors import BlockProcessor
import xml.etree.ElementTree as ET


def process_image(
  content: str,
  func: Callable[[str], Tuple[str, bool]]
) -> str:
  """
  处理 Markdown 类型字符串中的图片链接, 返回处理过图片链接部分的
  Markdown 字符串.

  Args:
    content: Markdown类型字符串
    func: 处理图片链接的函数, 该函数接受图片链接字符串,
  """

  def modify(match):
    # --- 下面是黑盒魔法 ---
    tar = match.group()
    pre, mid, suf = str(), str(), str()
    
    if tar[-1] == ')':
      pre = tar[: tar.index('(') + 1]
      mid = tar[tar.index('(') + 1 : -1]
      suf = tar[-1]
    else:
      mid = re.search(r'src="([^"]*)"', tar).group(1)
      pre, suf = tar.split(mid)
    
    link = mid
    # --- 黑盒魔法结束 ---

    new_name, err = func(link)

    return pre + (new_name if not err else link) + suf
  
  pat = r"!\[.*?\]\((.*?)\)|<img.*?src=[\'\"](.*?)[\'\"].*?>"

  return re.sub(pat, modify, content)


class BoxBlockProcessor(BlockProcessor):
  first = True

  def run(
    self,
    parent: ET.Element,
    blocks: list[str]
  ) -> bool | None:
    if self.first:
      self.first = False
      e = ET.SubElement(parent, 'div')
      self.parser.parseBlocks(e, blocks)
      for _ in range(0, len(blocks)):
        blocks.pop(0)
      return True
    return False


class BoxExtension(Extension):
  def extendMarkdown(self, md: markdown) -> None:
    md.parser.blockprocessors.register(
      BoxBlockProcessor(md.parser),
      'box_block',
      175
    )


def md_to_html(content: str) -> str:
  """将 Markdown 类型字符串转换成 HTML 类型字符串."""
  
  extensions: List[Union[str, Extension]] = [
    BoxExtension(),
    'meta',
    'fenced_code',
    'codehilite',
    'extra',
    'attr_list',
    'tables',
    'toc'
  ]

  return markdown(content, extensions=extensions)
