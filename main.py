from classes.parser_hh import ParserHH
from utils.config import MAIN_URL, KEYWORDS


def run():
    parser = ParserHH(url=MAIN_URL, keywords=KEYWORDS)
    parser.parse_first_page()


if __name__ == '__main__':
    run()
