import requests


def download_image(
  img_url: str,
  save_path: str
) -> None:
  """下载图片到指定路径."""

  resp = requests.get(img_url)
  with open(save_path, 'wb') as f:
    f.write(resp.content)
