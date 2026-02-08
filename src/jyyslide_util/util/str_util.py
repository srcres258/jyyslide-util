from urllib.parse import urlparse


def is_url(string: str) -> bool:
  """分辨URL和路径: 判断一个字符串是否为URL."""

  result = urlparse(string)
  return all([result.scheme, result.netloc])


def is_path(string: str) -> bool:
  """分辨URL和路径: 判断一个字符串是否为路径."""

  result = urlparse(string)
  return not all([result.scheme, result.netloc])
