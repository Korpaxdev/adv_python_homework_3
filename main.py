from classes.parser_hh import ParserHH
from utils.config import MAIN_URL, KEYWORDS


def run():
    parser = ParserHH(url=MAIN_URL, keywords=KEYWORDS, match_all_keywords=False, salary_type='USD')
    parser.parse_all_pages()


if __name__ == '__main__':
    run()
