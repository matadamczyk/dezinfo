import json
import random
from collections import Counter
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from datasets import load_dataset


def fetch_wikipedia_knowledge(output_path: Path) -> list[dict]:
    titles = [
        "Sejm Rzeczypospolitej Polskiej",
        "Senat Rzeczypospolitej Polskiej",
        "Platforma Obywatelska",
        "Prawo i Sprawiedliwość",
        "Konfederacja Wolność i Niepodległość",
        "Nowa Lewica",
        "Polska 2050",
        "Polskie Stronnictwo Ludowe",
        "Partia Razem",
        "Donald Tusk",
        "Jarosław Kaczyński",
        "Szymon Hołownia",
        "Sławomir Mentzen",
        "Rafał Trzaskowski",
        "Karol Nawrocki",
        "Andrzej Duda",
        "Władysław Kosiniak-Kamysz",
        "Krzysztof Bosak",
        "Centralny Port Komunikacyjny",
        "Krajowy Plan Odbudowy",
        "Rodzina 800 plus",
        "Zakład Ubezpieczeń Społecznych",
        "Narodowy Bank Polski",
        "Trybunał Konstytucyjny (Polska)",
    ]

    headers = {
        "User-Agent": "DezinfoFactCheckerBot/1.0 (academic NLP research; contact: student@wsei.edu.pl)"
    }
    articles = []

    for title in titles:
        params = {
            "action": "query",
            "titles": title,
            "prop": "extracts|links|info",
            "inprop": "url",
            "explaintext": 1,
            "exintro": 1,
            "plnamespace": 0,
            "pllimit": 50,
            "format": "json",
        }
        response = requests.get(
            "https://pl.wikipedia.org/w/api.php", params=params, headers=headers, timeout=15
        )
        if response.status_code != 200:
            continue

        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id == "-1":
                continue
            article_title = page_data.get("title", title)
            article_url = page_data.get(
                "fullurl", f"https://pl.wikipedia.org/wiki/{title.replace(' ', '_')}"
            )
            article_summary = page_data.get("extract", "").strip()
            article_links = [
                link_obj.get("title", "")
                for link_obj in page_data.get("links", [])
                if link_obj.get("title")
            ]
            articles.append(
                {
                    "title": article_title,
                    "url": article_url,
                    "summary": article_summary,
                    "links": article_links,
                }
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    return articles


def fetch_demagog_facts(output_path: Path, max_items: int = 28) -> list[dict]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    source_urls = [
        "https://demagog.org.pl/wypowiedzi/",
        "https://demagog.org.pl/tematy/polityka-krajowa/",
        "https://demagog.org.pl/osoba/donald-tusk/",
        "https://demagog.org.pl/osoba/slawomir-mentzen/",
        "https://demagog.org.pl/osoba/mateusz-morawiecki/",
        "https://demagog.org.pl/osoba/szymon-holownia/",
        "https://demagog.org.pl/osoba/rafal-trzaskowski/",
    ]

    facts = []
    seen_urls = set()

    for list_url in source_urls:
        if len(facts) >= max_items:
            break
        response = requests.get(list_url, headers=headers, timeout=15)
        if response.status_code != 200:
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select(".dg-item--desktop")
        if not items:
            items = soup.select(".dg-item")

        for item in items:
            if len(facts) >= max_items:
                break

            title_link = item.select_one(".dg-item__title a")
            if not title_link or not title_link.has_attr("href"):
                continue

            article_url = title_link["href"]
            if not article_url.startswith("http"):
                article_url = "https://demagog.org.pl" + article_url

            if "/wypowiedzi/" not in article_url or article_url in seen_urls:
                continue
            seen_urls.add(article_url)

            title_text = title_link.get_text(strip=True)

            author_tag = item.select_one(".dg-item__person a, .dg-item__person")
            author_text = author_tag.get_text(strip=True) if author_tag else "Nieznany"

            verdict_tag = item.select_one(".dg-item__evaluation p, .dg-item__evaluation")
            raw_verdict = verdict_tag.get_text(strip=True) if verdict_tag else "Nieweryfikowalne"
            normalized_verdict = "Nieweryfikowalne"
            for candidate in ["Fałsz", "Prawda", "Manipulacja", "Nieweryfikowalne"]:
                if candidate.lower() in raw_verdict.lower():
                    normalized_verdict = candidate
                    break

            quote_tag = item.select_one(".dg-item__description")
            quote_text = quote_tag.get_text(" ", strip=True) if quote_tag else ""

            summary_text = title_text
            try:
                detail_resp = requests.get(article_url, headers=headers, timeout=10)
                if detail_resp.status_code == 200:
                    detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
                    meta_desc = detail_soup.find("meta", attrs={"name": "description"}) or detail_soup.find(
                        "meta", attrs={"property": "og:description"}
                    )
                    if meta_desc and meta_desc.get("content"):
                        summary_text = meta_desc["content"].strip()
            except Exception:
                pass

            facts.append(
                {
                    "quote": quote_text,
                    "author": author_text,
                    "verdict": normalized_verdict,
                    "url": article_url,
                    "summary": summary_text,
                }
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=2)

    return facts


def fetch_poleval_tweets(
    output_path: Path, train_count: int = 500, test_count: int = 100
) -> list[dict]:
    dataset = load_dataset("ptaszynski/PolishCyberbullyingDataset")
    rng = random.Random(42)

    train_raw = list(dataset["train"])
    test_raw = list(dataset["test"])

    selected_train = rng.sample(train_raw, min(train_count, len(train_raw)))
    selected_test = rng.sample(test_raw, min(test_count, len(test_raw)))

    processed = []

    for row in selected_train:
        text = str(row.get("TEXT", "")).strip()
        is_toxic = bool(row.get("GENERAL TAG") == 1 or row.get("GENERAL TAG") == "1")
        processed.append({"text": text, "is_toxic": is_toxic, "split": "train"})

    for row in selected_test:
        text = str(row.get("TEXT", "")).strip()
        is_toxic = bool(row.get("GENERAL TAG") == 1 or row.get("GENERAL TAG") == "1")
        processed.append({"text": text, "is_toxic": is_toxic, "split": "test"})

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

    return processed


def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = base_dir / "data"

    wiki_path = data_dir / "wiki_knowledge.json"
    demagog_path = data_dir / "demagog_facts.json"
    poleval_path = data_dir / "poleval_tweets.json"

    print("Rozpoczynanie pobierania danych...")

    wiki_data = fetch_wikipedia_knowledge(wiki_path)
    print(f"\n[1] Wikipedia: pobrano {len(wiki_data)} artykułów -> {wiki_path}")

    demagog_data = fetch_demagog_facts(demagog_path, max_items=28)
    verdict_counter = Counter(item["verdict"] for item in demagog_data)
    print(f"\n[2] Demagog: pobrano {len(demagog_data)} wypowiedzi -> {demagog_path}")
    print("    Rozkład werdyktów:", dict(verdict_counter))

    poleval_data = fetch_poleval_tweets(poleval_path, train_count=500, test_count=100)
    toxic_overall = Counter(item["is_toxic"] for item in poleval_data)
    toxic_train = Counter(item["is_toxic"] for item in poleval_data if item["split"] == "train")
    toxic_test = Counter(item["is_toxic"] for item in poleval_data if item["split"] == "test")
    print(f"\n[3] PolEval Tweets: pobrano {len(poleval_data)} tweetów -> {poleval_path}")
    print("    Łączny rozkład is_toxic:", dict(toxic_overall))
    print("    Train split (is_toxic):", dict(toxic_train))
    print("    Test split (is_toxic):", dict(toxic_test))


if __name__ == "__main__":
    main()
