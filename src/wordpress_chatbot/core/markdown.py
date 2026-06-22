from markdownify import MarkdownConverter


def md_soup(soup, **options):
    return MarkdownConverter(**options).convert_soup(soup)
