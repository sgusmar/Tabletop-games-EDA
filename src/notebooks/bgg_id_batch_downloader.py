"""Descargador por lotes de datos de BGG usando `boardgames_ranks.csv`.

Características:
- Lee la primera columna del CSV con IDs (por defecto `data/boardgames_ranks.csv`).
- Procesa en lotes ajustables (por defecto 2000) y guarda cada lote en `data/batch_{i}.json`.
- Mantiene `data/processed_ids.txt` con los IDs ya descargados para reanudar.
- Respeta `delay` entre peticiones y `batch_pause` entre lotes para evitar bloqueos.
- Maneja errores 429 con backoff exponencial y reintentos.

Uso:
    python bgg_id_batch_downloader.py --input data/boardgames_ranks.csv --batch-size 2000 --delay 2.0 --batch-pause 60 --outdir data/batches

Notas:
- Este script intenta parsear la respuesta XML y extraer muchos campos básicos.
- Ajusta `--delay` y `--batch-pause` a valores conservadores para no sobrecargar la API.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, List

import requests


DEFAULT_TOKEN = os.getenv("BGG_TOKEN")
BGG_THING_URL = "https://boardgamegeek.com/xmlapi2/thing"


def read_ids_from_csv(path: Path) -> List[str]:
    ids: List[str] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            first = row[0].strip()
            if first and first.isdigit():
                ids.append(first)
    return ids


def chunks(iterable: List[str], size: int) -> Generator[List[str], None, None]:
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


def load_processed(path: Path) -> set:
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def append_processed(path: Path, ids: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for _id in ids:
            f.write(f"{_id}\n")


def _parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalized_numplayers_result(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower().replace(" ", "").replace("-", "")
    if normalized == "best":
        return "Best"
    if normalized == "recommended":
        return "Recommended"
    if normalized in {"notrecommended", "notrecomended"}:
        return "Not Recommended"
    return None


def parse_suggested_numplayers(item: ET.Element) -> Dict[str, Any]:
    poll = None
    for candidate in item.findall("poll"):
        if candidate.get("name") == "suggested_numplayers":
            poll = candidate
            break

    if poll is None:
        return {}

    by_result: Dict[str, Dict[str, int | None]] = {
        "Best": {},
        "Recommended": {},
        "Not Recommended": {},
    }
    columns: set[str] = set()

    for results in poll.findall("results"):
        numplayers = results.get("numplayers")
        if not numplayers:
            continue
        columns.add(numplayers)

        for result in results.findall("result"):
            row_name = _normalized_numplayers_result(result.get("value") or result.get("name"))
            if row_name is None:
                continue

            count = _parse_int(
                result.get("numvotes")
                or result.get("num")
                or result.get("count")
                or result.get("value")
            )
            by_result[row_name][numplayers] = count

    sorted_columns = sorted(
        columns,
        key=lambda value: (not value.isdigit(), int(value) if value.isdigit() else value),
    )
    result: Dict[str, Any] = {}
    for row_name in ("Best", "Recommended", "Not Recommended"):
        row_counts = by_result[row_name]
        values = [count for count in row_counts.values() if count is not None]
        max_count = max(values) if values else None
        max_numplayers = None
        if max_count is not None:
            for numplayers in sorted_columns:
                if row_counts.get(numplayers) == max_count:
                    max_numplayers = numplayers
                    break

        result[row_name] = max_numplayers

    return result


def parse_language_dependence(item: ET.Element) -> Dict[str, Any]:
    poll = None
    for candidate in item.findall("poll"):
        if candidate.get("name") == "language_dependence":
            poll = candidate
            break

    if poll is None:
        return {}

    best_result: Dict[str, Any] | None = None
    best_numvotes: int | None = None

    for results in poll.findall("results"):
        for result in results.findall("result"):
            numvotes = _parse_int(result.get("numvotes") or result.get("num") or result.get("count"))
            if numvotes is None:
                continue

            if best_numvotes is None or numvotes > best_numvotes:
                best_numvotes = numvotes
                best_result = f"{result.get('level')}: {result.get('value')}"

    return best_result or {}


def parse_collection(ratings: ET.Element) -> List[Dict[str, Any]]:
    collection: List[Dict[str, Any]] = []
    for category in ("owned", "trading", "wanting", "wishing"):
        elem = ratings.find(category)
        if elem is None:
            continue
        collection.append(
            {
                "category": category,
                "value": elem.get("value") if elem.get("value") is not None else elem.text,
            }
        )
    return collection


def parse_thing_xml_item(item: ET.Element) -> Dict[str, Any]:
    """Parse a single `<item>` XML element into an entry dict.
    
    Compatible with `boardgamegeek_to_excel._flatten_entry`.
    """
    if item is None:
        return {}

    def get_text(elem: ET.Element) -> str | None:
        if elem is None:
            return None
        # prefer attribute 'value' if present
        val = elem.get("value")
        return val if val is not None else (elem.text.strip() if elem.text and elem.text.strip() else None)

    entry: Dict[str, Any] = {}
    entry["row_id"] = item.get("id")
    entry["type"] = item.get("type")
    
    if not entry["row_id"]:
        return {}

    # primary name
    primary_names = [n.get("value") or n.text for n in item.findall("name") if n.get("type") == "primary"]
    entry["boardgame"] = primary_names[0] if primary_names else None

    # description and url
    desc = item.find("description")
    entry["description"] = desc.text if desc is not None and desc.text else None


    # player counts

    for tag in ("minplayers", "maxplayers"):
        elem = item.find(tag)
        entry[elem.tag] = get_text(elem)

    # playtime
    for tag, key in (("minplaytime", "min_playtime"), ("maxplaytime", "max_playtime"), ("playingtime", "playingtime")):
        entry[key] = get_text(item.find(tag))


    # minimum age
    entry["minimum_age"] = get_text(item.find("minage"))


    # game_info: yearpublished, categories, mechanisms, family
    entry["release_year"] = get_text(item.find("yearpublished"))
    # categories/mechanics/family: from link elements (type attributes vary)
    cats = []
    mechanisms = []
    families = []
    for l in item.findall("link"):
        ltype = l.get("type")
        name = l.get("value") or l.text
        if not name:
            continue
        if ltype == "boardgamecategory":
            cats.append(name)
        elif ltype == "boardgamemechanic":
            mechanisms.append(name)
        elif ltype == "boardgamefamily":
            families.append(name)
    entry["categories"] = cats
    entry["mechanisms"] = mechanisms
    entry["family"] = families

    # credits
    designers = []
    artists = []
    publishers = []
    for l in item.findall("link"):
        ltype = l.get("type")
        name = l.get("value") or l.text
        if not name:
            continue
        if ltype == "boardgamedesigner":
            designers.append(name)
        elif ltype == "boardgameartist":
            artists.append(name)
        elif ltype == "boardgamepublisher":
            publishers.append(name)
    entry["designers"] = designers
    entry["artists"] = artists
    entry["publishers"] = publishers

    # statistics
    ranks: Dict[str, Any] = {}
    collection: List[Dict[str, Any]] = []
    suggested_numplayers: Dict[str, Any] = parse_suggested_numplayers(item)
    language_dependence = parse_language_dependence(item)

    stats = item.find("statistics")
    if stats is not None:
        ratings = stats.find("ratings")
        if ratings is not None:
            entry["average_rating"] = get_text(ratings.find("average"))
            entry["num_of_ratings"] = get_text(ratings.find("usersrated"))
            entry["weight"] = get_text(ratings.find("averageweight"))
            entry["num_of_weights"] = get_text(ratings.find("numweights"))
            entry["bayes_average"] = get_text(ratings.find("bayesaverage"))
            entry["std_deviation"] = get_text(ratings.find("stddev"))

            # ranks
            ranks_elem = ratings.find("ranks")
            if ranks_elem is not None:
                for r in ranks_elem.findall("rank"):
                    rname = r.get("name") or r.get("type") or "rank"
                    ranks[rname] = r.get("value")

            collection = parse_collection(ratings)

    # Rebuild key order for stable JSON output.
    ordered_entry: Dict[str, Any] = {
        "row_id": entry.get("row_id"),
        "type": entry.get("type"),
        "boardgame": entry.get("boardgame"),
        "description": entry.get("description"),
        "min_players": entry.get("minplayers"),
        "max_players": entry.get("maxplayers"),
        "suggested_numplayers": suggested_numplayers,
        "min_playtime": entry.get("min_playtime"),
        "max_playtime": entry.get("max_playtime"),
        "playingtime": entry.get("playingtime"),
        "minimum_age": entry.get("minimum_age"),
        "release_year": entry.get("release_year"),
        "average_rating": entry.get("average_rating"),
        "num_of_ratings": entry.get("num_of_ratings"),
        "weight": entry.get("weight"),
        "num_of_weights": entry.get("num_of_weights"),
        "bayes_average": entry.get("bayes_average"),
        "std_deviation": entry.get("std_deviation"),
        "ranks": ranks,
        "language_dependency": language_dependence,
        "categories": entry.get("categories"),
        "mechanisms": entry.get("mechanisms"),
        "family": entry.get("family"),
        "designers": entry.get("designers"),
        "artists": entry.get("artists"),
        "publishers": entry.get("publishers"),
    }

    for c in collection:
        ordered_entry[c["category"]] = c["value"]


    # ensure all expected keys exist
    ordered_entry.setdefault("row_id", None)
    ordered_entry.setdefault("boardgame", None)
    ordered_entry.setdefault("description", None)

    return ordered_entry


def parse_thing_xml(xml_text: str) -> List[Dict[str, Any]]:
    """Parse `/thing` XML (single or multiple items) into a list of entry dicts.
    
    When multiple IDs are requested via comma-separated params, the response
    contains multiple `<item>` elements. Each is parsed into an entry.
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return [{"raw_xml": xml_text}]

    items = root.findall("item")
    if not items:
        return [{"raw_xml": xml_text}]
    
    return [parse_thing_xml_item(item) for item in items]


def fetch_with_retries(session: requests.Session, url: str, params: Dict[str, Any], max_retries: int = 6) -> str:
    for attempt in range(max_retries):
        try:
            resp = session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            if status == 429:
                wait = (2 ** attempt) * 5
                print(f"  ⚠ 429 received. Waiting {wait}s before retry (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
                continue
            else:
                raise
        except requests.exceptions.RequestException as e:
            wait = (2 ** attempt) * 5
            print(f"  Request error: {e}. Waiting {wait}s and retrying (attempt {attempt+1}/{max_retries})")
            time.sleep(wait)
            continue
    raise RuntimeError("Max retries exceeded for request")


def process_batch(
    ids: List[str],
    session: requests.Session,
    out_path: Path,
    processed_path: Path,
    delay: float,
    max_retries: int,
    ids_per_request: int = 20,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    results: List[Dict[str, Any]] = []
    processed_now: List[str] = []
    
    # Group IDs into sub-batches (e.g., 20 at a time)
    sub_batches = list(chunks(ids, ids_per_request))

    for batch_idx, sub_batch in enumerate(sub_batches, start=1):
        ids_str = ",".join(sub_batch)
        print(f"  [Batch {batch_idx}/{len(sub_batches)}] Fetching {len(sub_batch)} IDs: {ids_str[:50]}...")
        try:
            xml = fetch_with_retries(session, BGG_THING_URL, params={"id": ids_str, "stats": "1"}, max_retries=max_retries)
            parsed_items = parse_thing_xml(xml)
            results.extend(parsed_items)
            processed_now.extend(sub_batch)
            print(f"    ✓ Retrieved {len(parsed_items)} items")
        except Exception as e:
            print(f"    Error fetching batch: {e}")
            for _id in sub_batch:
                results.append({"id": _id, "error": str(e)})

        print(f"    Sleeping {delay}s...")
        time.sleep(delay)

    # Save batch
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Append processed IDs to log
    append_processed(processed_path, processed_now)


def main() -> None:
    parser = argparse.ArgumentParser(description="Descargar datos de BGG por IDs en lotes y registrar progreso")
    parser.add_argument("--input", default="../data/boardgames_ranks.csv", help="CSV con IDs en primera columna")
    parser.add_argument("--id", dest="single_id", help="ID único a descargar (omite --input)")
    parser.add_argument("--batch-size", type=int, default=2000, help="Tamaño del lote (p.ej. 2000 o 3000)")
    parser.add_argument("--ids-per-request", type=int, default=20, help="Cuántos IDs agrupar por petición (p.ej. 20)")
    parser.add_argument("--outdir", default="../data/batches", help="Directorio de salida para los lotes")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay entre peticiones (segundos)")
    parser.add_argument("--batch-pause", type=float, default=60.0, help="Pausa entre lotes (segundos)")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="Bearer token (no necesario para xmlapi2)")
    parser.add_argument("--max-retries", type=int, default=6, help="Reintentos por petición en caso de error")
    parser.add_argument("--start-batch", type=int, default=0, help="Índice de lote para reanudar (0-based)")
    args = parser.parse_args()

    input_path = Path(args.input)
    outdir = Path(args.outdir)
    processed_log = outdir / "processed_ids.txt"

    # If a single ID is provided, use it and ignore the CSV to avoid processing the whole file.
    if args.single_id:
        ids = [str(args.single_id).strip()]
        print(f"Single ID mode: {ids[0]}")
    else:
        ids = read_ids_from_csv(input_path)
        print(f"Total IDs found in CSV: {len(ids)}")

    # Build batches
    if args.single_id:
        all_batches = [ids]
    else:
        all_batches = list(chunks(ids, args.batch_size))
    print(f"Total batches: {len(all_batches)} (batch size: {args.batch_size})")

    # Load processed IDs to skip already-done ones
    processed = load_processed(processed_log)
    session = requests.Session()
    headers = {"Accept": "application/xml"}
    # add a friendly User-Agent to reduce chance of simple blocking
    headers.setdefault("User-Agent", "BGGBatchDownloader/1.0 (+https://github.com/)")
    if args.token:
        headers["Authorization"] = f"Bearer {args.token}"
    session.headers.update(headers)

    for batch_index, batch_ids in enumerate(all_batches):
        if batch_index < args.start_batch:
            print(f"Skipping batch {batch_index} (before start-batch)")
            continue

        # Filter IDs in batch that are not yet processed
        to_process = [i for i in batch_ids if i not in processed]
        if not to_process:
            print(f"Batch {batch_index} already processed. Skipping.")
            continue

        print(f"Processing batch {batch_index}: {len(to_process)} IDs (range approx. {batch_index*args.batch_size}..)")
        out_path = outdir / f"bgg_batch_{batch_index:04d}.json"

        try:
            process_batch(to_process, session, out_path, processed_log, args.delay, args.max_retries, args.ids_per_request)
        except Exception as e:
            print(f"Batch {batch_index} failed: {e}")
            # Do not abort; move to next batch after pause

        print(f"Batch {batch_index} finished. Pausing {args.batch_pause}s before next batch.")
        time.sleep(args.batch_pause)

    print("All batches processed.")


if __name__ == "__main__":
    main()
