import json
import sys
from pathlib import Path
import click
from .parser import parse_email_bytes
from .inference import get_verdict

@click.command()
@click.argument("eml_path", type=click.Path(exists=True))
@click.option("--provider", type=click.Choice(["openai", "ollama"]), help="LLM provider to use", required=True)
@click.option("--model", type=str, help="Model name to use with the provider", required=True)
def main(provider: str, model: str, eml_path: str):
    try:
        raw = Path(eml_path).read_bytes()
    except Exception as e:
        click.echo(f"Error reading the file {e}", err=True)
        sys.exit(2)

    try:
        parsed = parse_email_bytes(raw) #ParsedEmail fixed structure
        parsed_dict = parsed.model_dump() #ParsedEmail to dict
        verdict = get_verdict(provider, model, parsed_dict)
        print(json.dumps(verdict, indent=2))
        sys.exit(0)

    except Exception as e:
        click.echo(f"Error parsing email: {e}", err=True)
        sys.exit(3)
    

if __name__ == "__main__":
    main()