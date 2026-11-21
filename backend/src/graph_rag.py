import os
import re
import json
import time
from pathlib import Path
from typing import Any
import networkx as nx
import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI

_graph: nx.DiGraph | None = None
_collection: Any | None = None
_embedding_model: SentenceTransformer | None = None
_wiki_data: list[dict] | None = None
_demagog_data: list[dict] | None = None
_llm_unavailable_until: float = 0.0

VULGARITY_REGEX = re.compile(
    r"\b(złodziej\w*|oszust\w*|zdrajc\w*|bandyt\w*|kłamc\w*|kłam\w*|śmieci?\w*|szmat\w*|idiot\w*|debil\w*|"
    r"skurw\w*|jeb\w*|chuj\w*|pierd\w*|wypierdal\w*|szkodnik\w*|patologi\w*|bezczel\w*)\b",
    re.IGNORECASE,
)


def get_data_paths() -> tuple[Path, Path]:
    root_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = root_dir / "data"
    return data_dir / "wiki_knowledge.json", data_dir / "demagog_facts.json"


def load_raw_data() -> tuple[list[dict], list[dict]]:
    wiki_path, demagog_path = get_data_paths()
    with open(wiki_path, "r", encoding="utf-8") as file_handle:
        wiki_items = json.load(file_handle)
    with open(demagog_path, "r", encoding="utf-8") as file_handle:
        demagog_items = json.load(file_handle)
    return wiki_items, demagog_items


def extract_fact_topic(fact: dict, index: int) -> str:
    summary = fact.get("summary", "").strip()
    if not summary:
        return f"Temat_{index}"
    first_sentence = summary.split(".")[0].strip()
    cleaned = re.sub(
        r"^(Sprawdzamy wypowiedź|Wiceminister stwierdził, że|Według|Policja dementuje doniesienia, według których)\s*",
        "",
        first_sentence,
        flags=re.IGNORECASE,
    ).strip()
    if len(cleaned) > 50:
        cleaned = cleaned[:50].rsplit(" ", 1)[0]
    return cleaned if cleaned else f"Temat_{index}"


def build_knowledge_graph(wiki_items: list[dict], demagog_items: list[dict]) -> nx.DiGraph:
    graph = nx.DiGraph()
    wiki_titles = {item["title"] for item in wiki_items if "title" in item}

    for item in wiki_items:
        title = item["title"]
        graph.add_node(title, node_type="wiki", summary=item.get("summary", ""), url=item.get("url", ""))

    for item in wiki_items:
        src = item["title"]
        for target in item.get("links", []):
            if target in wiki_titles and target != src:
                graph.add_edge(src, target, relation="POWIĄZANY_Z")

    for idx, item in enumerate(demagog_items):
        author = item.get("author", "").strip()
        verdict = item.get("verdict", "").strip()
        quote = item.get("quote", "").strip()
        summary = item.get("summary", "").strip()
        combined_text = f"{quote} {summary}".lower()

        if author:
            graph.add_node(author, node_type="author")

        matched_wiki = [
            title for title in wiki_titles
            if title.lower() in combined_text or any(token.lower() in combined_text for token in title.split() if len(token) > 4)
        ]

        if matched_wiki:
            for entity in matched_wiki:
                if author and author != entity:
                    graph.add_edge(author, entity, relation="WYPOWIEDZIAŁ_SIĘ_O", verdict=verdict)
        else:
            topic = extract_fact_topic(item, idx)
            graph.add_node(topic, node_type="topic")
            if author:
                graph.add_edge(author, topic, relation="WYPOWIEDZIAŁ_SIĘ_O", verdict=verdict)
            graph.add_edge(topic, verdict, relation="WERDYKT_FAKTU")

        if author and verdict:
            graph.add_edge(author, verdict, relation="OCENA_WYPOWIEDZI")

    return graph


def build_vector_index(
    wiki_items: list[dict],
    demagog_items: list[dict],
    embedding_model: SentenceTransformer,
) -> Any:
    client = chromadb.EphemeralClient()
    collection = client.create_collection(name="hybrid_graphrag_facts")

    documents: list[str] = []
    metadatas: list[dict] = []
    ids: list[str] = []

    for idx, item in enumerate(wiki_items):
        title = item.get("title", "")
        summary = item.get("summary", "")
        doc_text = f"{title}. {summary}"
        documents.append(doc_text)
        metadatas.append({
            "source": "wiki",
            "title": title,
            "author": title,
            "verdict": "",
            "summary": summary,
            "url": item.get("url", ""),
            "quote": "",
        })
        ids.append(f"wiki_{idx}")

    for idx, item in enumerate(demagog_items):
        author = item.get("author", "")
        quote = item.get("quote", "")
        summary = item.get("summary", "")
        verdict = item.get("verdict", "")
        doc_text = f"Wypowiedź ({author}): {quote}\nFakt: {summary}\nOcena: {verdict}"
        documents.append(doc_text)
        metadatas.append({
            "source": "demagog",
            "title": author,
            "author": author,
            "verdict": verdict,
            "summary": summary,
            "url": item.get("url", ""),
            "quote": quote,
        })
        ids.append(f"demagog_{idx}")

    embeddings = embedding_model.encode(documents, show_progress_bar=False).tolist()
    collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
    return collection


def get_knowledge_base() -> tuple[nx.DiGraph, Any, SentenceTransformer, list[dict], list[dict]]:
    global _graph, _collection, _embedding_model, _wiki_data, _demagog_data
    if _graph is not None and _collection is not None and _embedding_model is not None:
        return _graph, _collection, _embedding_model, _wiki_data or [], _demagog_data or []

    _wiki_data, _demagog_data = load_raw_data()
    _graph = build_knowledge_graph(_wiki_data, _demagog_data)
    _embedding_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    _collection = build_vector_index(_wiki_data, _demagog_data, _embedding_model)
    return _graph, _collection, _embedding_model, _wiki_data, _demagog_data


def extract_subgraph(
    graph: nx.DiGraph,
    query_text: str,
    top_metas: list[dict],
) -> list[tuple[str, str, str]]:
    relevant_nodes = set()
    query_lower = query_text.lower()

    for node in graph.nodes():
        node_str = str(node)
        if node_str.lower() in query_lower:
            relevant_nodes.add(node_str)
        elif any(token.lower() in query_lower for token in node_str.split() if len(token) > 4):
            relevant_nodes.add(node_str)

    for meta in top_metas:
        author = meta.get("author")
        title = meta.get("title")
        if author and author in graph:
            relevant_nodes.add(author)
        if title and title in graph:
            relevant_nodes.add(title)

    edges: list[tuple[str, str, str]] = []
    seen = set()

    for u, v, data in graph.edges(data=True):
        if u in relevant_nodes and v in relevant_nodes:
            rel = str(data.get("relation", "POWIĄZANY_Z"))
            edge = (str(u), rel, str(v))
            if edge not in seen:
                edges.append(edge)
                seen.add(edge)

    if len(edges) < 6:
        for node in list(relevant_nodes):
            for u, v, data in graph.out_edges(node, data=True):
                rel = str(data.get("relation", "POWIĄZANY_Z"))
                edge = (str(u), rel, str(v))
                if edge not in seen:
                    edges.append(edge)
                    seen.add(edge)
                if len(edges) >= 6:
                    break
            if len(edges) >= 6:
                break

    if len(edges) < 6:
        for node in list(relevant_nodes):
            for u, v, data in graph.in_edges(node, data=True):
                rel = str(data.get("relation", "POWIĄZANY_Z"))
                edge = (str(u), rel, str(v))
                if edge not in seen:
                    edges.append(edge)
                    seen.add(edge)
                if len(edges) >= 6:
                    break
            if len(edges) >= 6:
                break

    if not edges and top_metas:
        first_meta = top_metas[0]
        entity = first_meta.get("author") or first_meta.get("title") or "Wpis_Publiczny"
        verdict = first_meta.get("verdict") or "Brak danych"
        edges.append(("Wpis_Analizowany", "odnosi_się_do", str(entity)))
        edges.append((str(entity), "status_faktu", str(verdict)))
        edges.append((str(entity), "baza_weryfikacyjna", "Demagog / Wikipedia"))

    return edges[:8]


def censor_text(text: str) -> str:
    return VULGARITY_REGEX.sub("[TREŚĆ MODEROWANA]", text)


def normalize_verdict_string(raw_verdict: str) -> str:
    cleaned = raw_verdict.strip().upper()
    if "FAŁ" in cleaned or "FAL" in cleaned:
        return "FAŁSZ"
    if "MANIP" in cleaned:
        return "MANIPULACJA"
    if "PRAW" in cleaned:
        return "PRAWDA"
    return "NIEZWERYFIKOWANE"


def call_slm(
    text: str,
    context_docs: list[str],
    subgraph_edges: list[tuple[str, str, str]],
) -> dict | None:
    global _llm_unavailable_until
    if time.time() < _llm_unavailable_until:
        return None

    base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
    api_key = os.getenv("LLM_API_KEY", "ollama")
    model_name = os.getenv("LLM_MODEL", "llama3.2:3b")

    edges_representation = "\n".join([f"- ({s}) --[{r}]--> ({t})" for s, r, t in subgraph_edges])
    docs_representation = "\n\n".join(context_docs[:3])

    system_instruction = (
        "Jesteś modułem weryfikacji faktów i neutralizacji dezinformacji. "
        "Na podstawie podanego kontekstu i powiązań grafu wiedzy oceniasz prawdziwość wypowiedzi, "
        "cenzurujesz mowę nienawiści lub wulgaryzmy oraz przygotowujesz neutralną wersję.\n"
        "Zwróć WYŁĄCZNIE obiekt JSON o polach:\n"
        '{"verdict": "PRAWDA"|"FAŁSZ"|"MANIPULACJA"|"NIEZWERYFIKOWANE", '
        '"explanation": "zwięzłe uzasadnienie po polsku", '
        '"censored_text": "tekst z wulgaryzmami zastąpionymi [TREŚĆ MODEROWANA]", '
        '"neutralized_text": "obiektywna, spokojna wersja bez manipulacji"}'
    )

    user_prompt = (
        f"Wypowiedź do weryfikacji: {text}\n\n"
        f"Kontekst wektorowy:\n{docs_representation}\n\n"
        f"Krawędzie grafu wiedzy:\n{edges_representation}\n\n"
        "Odpowiedź w czystym formacie JSON:"
    )

    try:
        client = OpenAI(base_url=base_url, api_key=api_key, timeout=3.0, max_retries=0)
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=500,
        )
        raw_content = completion.choices[0].message.content or ""
        cleaned = raw_content.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
        parsed = json.loads(cleaned)
        verdict = normalize_verdict_string(str(parsed.get("verdict", "")))
        return {
            "verdict": verdict,
            "explanation": str(parsed.get("explanation", "")).strip(),
            "censored_text": str(parsed.get("censored_text", "")).strip() or text,
            "neutralized_text": str(parsed.get("neutralized_text", "")).strip() or text,
        }
    except Exception:
        _llm_unavailable_until = time.time() + 10.0
        return None


def deterministic_fallback(
    text: str,
    top_metas: list[dict],
    top_distances: list[float],
) -> dict:
    censored = censor_text(text)
    if not top_metas:
        return {
            "verdict": "NIEZWERYFIKOWANE",
            "explanation": "Brak pasujących dokumentów w bazie wiedzy do przeprowadzenia rzetelnej weryfikacji.",
            "censored_text": censored,
            "neutralized_text": censored,
        }

    best_meta = top_metas[0]
    best_dist = top_distances[0] if top_distances else 999.0
    source_type = best_meta.get("source", "")

    if source_type == "demagog" and best_dist <= 12.0:
        raw_verdict = best_meta.get("verdict", "")
        verdict = normalize_verdict_string(raw_verdict)
        explanation = best_meta.get("summary", "") or "Fakt zweryfikowany w bazie portalu Demagog."
        if verdict == "PRAWDA":
            neutralized = censored
        else:
            neutralized = f"Według oficjalnych ustaleń i weryfikacji fact-checkingowej: {explanation}"
        return {
            "verdict": verdict,
            "explanation": explanation,
            "censored_text": censored,
            "neutralized_text": neutralized,
        }

    if source_type == "wiki" and best_dist <= 10.0:
        title = best_meta.get("title", "")
        summary = best_meta.get("summary", "")
        explanation = f"Zweryfikowano z encyklopedią wiedzy ({title}): {summary[:240]}..."
        return {
            "verdict": "PRAWDA",
            "explanation": explanation,
            "censored_text": censored,
            "neutralized_text": f"Zgodnie z danymi encyklopedycznymi dotyczącymi hasła {title}: {summary[:200]}...",
        }

    if best_dist <= 15.0 and best_meta.get("verdict"):
        raw_verdict = best_meta.get("verdict", "")
        verdict = normalize_verdict_string(raw_verdict)
        explanation = best_meta.get("summary", "")
        return {
            "verdict": verdict,
            "explanation": f"Częściowa zgodność kontekstowa z bazą faktów: {explanation}",
            "censored_text": censored,
            "neutralized_text": f"W odniesieniu do analizowanej tezy, oficjalne źródła wskazują: {explanation}",
        }

    return {
        "verdict": "NIEZWERYFIKOWANE",
        "explanation": "Brak bezpośredniego potwierdzenia przedstawionej tezy w zweryfikowanej bazie faktów Demagog i encyklopedii.",
        "censored_text": censored,
        "neutralized_text": censored if censored != text else f"Pojawiły się niepotwierdzone doniesienia: {text.strip()}, które wymagają dodatkowej weryfikacji u źródeł.",
    }


def verify_and_rewrite(text: str) -> dict:
    cleaned_input = text.strip()
    if not cleaned_input:
        return {
            "verdict": "NIEZWERYFIKOWANE",
            "explanation": "Tekst do weryfikacji jest pusty.",
            "censored_text": "",
            "neutralized_text": "",
            "subgraph_edges": [],
        }

    graph, collection, embedding_model, _, _ = get_knowledge_base()

    query_embedding = embedding_model.encode([cleaned_input], show_progress_bar=False).tolist()
    query_result = collection.query(query_embeddings=query_embedding, n_results=4)

    retrieved_docs: list[str] = query_result["documents"][0] if query_result["documents"] else []
    retrieved_metas: list[dict] = query_result["metadatas"][0] if query_result["metadatas"] else []
    retrieved_dists: list[float] = query_result["distances"][0] if query_result["distances"] else []

    subgraph_edges = extract_subgraph(graph, cleaned_input, retrieved_metas)

    slm_result = call_slm(cleaned_input, retrieved_docs, subgraph_edges)
    if slm_result is not None:
        return {
            "verdict": slm_result["verdict"],
            "explanation": slm_result["explanation"],
            "censored_text": slm_result["censored_text"],
            "neutralized_text": slm_result["neutralized_text"],
            "subgraph_edges": subgraph_edges,
        }

    fallback_result = deterministic_fallback(cleaned_input, retrieved_metas, retrieved_dists)
    return {
        "verdict": fallback_result["verdict"],
        "explanation": fallback_result["explanation"],
        "censored_text": fallback_result["censored_text"],
        "neutralized_text": fallback_result["neutralized_text"],
        "subgraph_edges": subgraph_edges,
    }
