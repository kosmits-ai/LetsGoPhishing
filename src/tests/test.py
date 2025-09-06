import json
from pathlib import Path
import click
from src.parser import parse_email_bytes
from src.inference import get_verdict
import sys


def read_eml_files():
    dataset_path = Path(__file__).parent / "dataset.json"
    try:
        return json.loads(dataset_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error reading the dataset {e}", file=sys.stderr)
        sys.exit(2)
    return data


def main(provider: str, model: str):

    data = read_eml_files()
    for item in data:
        raw = item["eml"].encode('utf-8')
        try:
            parsed = parse_email_bytes(raw) #ParsedEmail fixed structure
            parsed_dict = parsed.model_dump() #ParsedEmail to dict
            verdict = get_verdict(provider, model, parsed_dict) #dict
            result = json.dumps(verdict, indent=2) #dict to json string
            print(f"Label: {item['label']}\nResult: {result}\n")
            with open("score_qwen2.5.txt", "a") as f:
                f.write(f"{item['label']},\n Result: {verdict["classification"]}, {verdict["confidence"]}\n")
        except Exception as e:
            click.echo(f"Error parsing email: {e}", err=True)
            with open("score.txt", "a") as f:
                f.write(f"Error parsing {item['label']}: {e}\n")
if __name__ == "__main__":
    main("ollama", "qwen2.5:7b-instruct")  # Change model as needed