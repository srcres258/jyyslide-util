import sys
import argparse
from jyyslide_util.converter import converter


def main() -> int:
  print("Welcome to use jyyslide util!")

  parser = argparse.ArgumentParser()
  parser.add_argument('filepath', type=str, help='select a Markdown file to convert')
  args = parser.parse_args()

  converter(args.filepath)

  return 0


def run() -> None:
  sys.exit(main())
