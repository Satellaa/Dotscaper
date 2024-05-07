from bs4 import BeautifulSoup


def parse_and_expand_ruby(string: str) -> str:

    if "<ruby>" not in string:
        return string

    ruby_less = ""
    soup = BeautifulSoup(string, "html.parser")

    for element in soup.children:
        if element.name is None:
            ruby_less += element.string
        elif element.name == "ruby":
            if len(element.contents) == 2:
                rb, rt = element.contents
                if rb.name is None and rt.name == "rt" and len(
                        rt.contents) == 1 and rt.contents[0].name is None:
                    ruby_less += rb.string

    return ruby_less


HALF2FULL = dict((i, i + 0xFEE0) for i in range(0x21, 0x7F))
HALF2FULL[0x20] = 0x20


def half_to_full(string: str) -> str:
    return str(string).translate(HALF2FULL)
