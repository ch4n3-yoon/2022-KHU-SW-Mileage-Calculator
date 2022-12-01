#!/usr/bin/env python3
# coding: utf-8

import bs4
import pprint
import requests

PAGE = "page"


class Archive:
    def __init__(self, name: str, point: int) -> None:
        self.name = name.replace(" ", "")
        self.point = point

    def is_equal(self, name: str) -> bool:
        return name.lower().find(self.name.lower()) > -1


archives = [
    Archive("국내 학술회의 논문 발표", 100),
    Archive("국내 학술회의 발표", 100),
    Archive("국내 학술회의 논문 게재", 100),
    Archive("국내 학술지 논문 게재", 200),
    Archive("국내 학술지 논문 개제", 200),
    Archive("우수논문 수상", 50),
    Archive("오픈소스 코드기여", 200),
    Archive("오픈소스 기여", 200),
    Archive("교내 경진대회 및 공모전 수상", 100),
    Archive("교외 경진대회 및 공모전 수상", 200),
    Archive("교외 경진대회 공모전 및 수상", 200),
    Archive("국내 특허 출원", 150),
    Archive("SW중심대학 사업단 진행행사 참여", 50),
    Archive("재학생 코딩 역량평가 참가", 50),
    Archive("봄 경시대회 참가", 50),
    Archive("중심대학 사업단 진행행사", 50),
    Archive("khuthon 참가", 50),
    Archive("소프트웨어 등록", 75),
    Archive("국외 학술회의 논문 발표", 150),
    Archive("국외 학술지 논문 게제", 250),
    Archive("국외 학술지 논문 게재", 250),
    Archive("오픈소스 영어 기술 문서 번역", 80),
    Archive("영어 봉사활동 실적", 75),  # 해외 IT 봉사단은 별로 없을 것 같아서 일단 75로
    Archive("전공 관련 창업", 250),
    Archive("앱스토어 소프트웨어 등록", 250),
    Archive("창업 공모전 수상", 150),
    Archive("산업체 실무 경험을 위한 장/단기 인턴수료", 150),
    Archive("아너십", 50),
]


class Article:
    """
    This class is created to store article and calculate point efficiently
    """

    def __init__(self, name: str, title: str):
        self.name = name
        self.title = title.replace(" ", "")

    @property
    def point(self) -> int:
        for archive in archives:
            if self.title.lower().find(archive.name.lower()) > -1:
                return archive.point

        # raise ValueError(f"Cannot match the point to `{self.title}`")
        print(f"[ ERROR ] Cannot match the point to `{self.title}`")

        # return default point (not official)
        return 20

    def __str__(self) -> str:
        return f"<{self.name}:{self.point}>"

    def __repr__(self) -> str:
        return self.__str__()


class ArticleParser:
    """
    This class will request swedu.khu.ac.kr, and parse articles, rank
    """

    def __init__(self, page: int) -> None:
        self.page = page
        self.session = requests.Session()
        self.url = "http://swedu.khu.ac.kr/board5/bbs/board.php"
        self.params = {
            "bo_table": "02_07",
            "page": 0,
        }
        self.articles = []
        self.rank = {}

    def get_all(self) -> list:
        for page in range(1, self.page + 1):
            self.params[PAGE] = page

            response = self.session.get(
                self.url,
                params=self.params,
            )

            self.parse_page(response.text)

            return self.articles

    @staticmethod
    def is_valid_date(date: str) -> bool:
        date1, date2 = map(int, date.split("-"))

        if date1 < 9:
            return False

        return True

    def parse_page(self, html) -> None:
        soup = bs4.BeautifulSoup(html, "lxml")
        for tr in soup.find_all("tr"):
            if "bo_notice" in tr.get("class", ""):
                continue

            # 반려 여부 확인
            status = tr.find("span", attrs={"class": "status03"})
            if status:
                continue

            # 게시글 등록 날짜 확인
            try:
                created_at = tr.find("td", attrs={"class": "td_datetime"}).text
                if not self.is_valid_date(created_at):
                    continue
            except AttributeError:
                continue

            # 게시글 파싱
            try:
                name = tr.find("td", attrs={"class": ["td_name", "sv_use"]}).text.strip()
                title = tr.find("td", attrs={"class": "td_subject"}).find("a").text.strip()
            except AttributeError:
                continue

            article = Article(name, title)
            self.articles.append(article)

            # 랭킹 기록
            try:
                self.rank[article.name] += article.point
            except KeyError:
                self.rank[article.name] = article.point

    def get_rank(self) -> list:
        self.get_all()
        return sorted(self.rank.items(), key=lambda x: x[1], reverse=True)


if __name__ == "__main__":
    article_parser = ArticleParser(31)
    rank = article_parser.get_rank()
    pprint.pprint(rank)

