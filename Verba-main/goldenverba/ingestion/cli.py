import click
from goldenverba.ingestion.init_schema import init_schema
from goldenverba.ingestion.init_cache import init_cache
from goldenverba.ingestion.init_suggestion import init_suggestion
from goldenverba.ingestion.import_data import import_data
from goldenverba.ingestion.import_weaviate import import_weaviate


@click.group()
def cli():
    """Main command group for verba."""
    pass


@cli.command()
@click.option(
    "--model",
    default="gpt-3.5-turbo",
    help="OpenAI Model name to initialize. (default gpt-3.5-turbo)",
)
def init(model):
    """
    Initialize schemas
    """
    init_schema(model=model)
    init_cache()
    init_suggestion()


@cli.command()
def clear_cache_command():
    init_cache()


@cli.command()
@click.option(
    "--model",
    default="gpt-3.5-turbo",
    help="OpenAI Model name to initialize. (default gpt-3.5-turbo)",
)
def clear_all_command(model):
    init_schema(model=model)
    init_cache()
    init_suggestion()


@cli.command()
@click.option(
    "--path",
    default="./data",
    help="Path to data directory",
)
@click.option(
    "--model",
    default="gpt-3.5-turbo",
    help="OpenAI Model name to initialize. (default gpt-3.5-turbo)",
)
@click.option(
    "--clear",
    default=False,
    help="Remove all existing data before ingestion",
)
def import_data_command(path, model, clear):
    if clear:
        init_schema(model=model)
        init_cache()
        init_suggestion()
    import_data(path, model)


@cli.command()
def import_weaviate_command():
    init_schema(model="gpt-4")
    init_cache()
    init_suggestion()
    import_weaviate()
