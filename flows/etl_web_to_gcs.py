import kaggle
import pandas as pd
from pathlib import Path
from typing import Generator, Tuple
from prefect import flow, task
from prefect.filesystems import GCS


gcs_block = GCS.load("spotify-gcs")


@task(log_prints=True)
def fetch_spotify_dataset(dataset: str, dir_path: str, dataset_path: str) -> Path:
    """Fetch spotify dataset and return Path object"""
    kaggle.api.dataset_download_files(
        dataset=dataset,
        path=dir_path,
        quiet=False,
        force=True,
    )
    return Path(dataset_path)


@task(log_prints=True)
def write_gcs(df: pd.DataFrame, chunk_file_path: Path) -> None:
    """Upload local csv chunk file to GCS"""
    gcs_block.write_path(path=chunk_file_path.as_posix(), content=df.to_csv().encode("utf-8"))
    print(f"Chunk {chunk_file_path.as_posix()} is uploaded to GCS.")


def get_large_file_by_chunks(source_path: Path, chunksize: int = 1000000) -> Generator[Tuple[int, pd.DataFrame]]:
    Path(f"./data/chunks").mkdir(parents=True, exist_ok=True)
    for i, chunk in enumerate(pd.read_csv(source_path, chunksize=chunksize)):
        yield i, chunk


@task(log_prints=True)
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Fix dtype issues"""
    df["streams"] = df["streams"].astype('Int64')
    df["date"] = pd.to_datetime(df["date"])
    return df


@flow(log_prints=True, name="Subflow - Web to GCS step")
def etl_web_to_gcs() -> None:
    """The main ETL function"""
    dataset, dir_path, dataset_path = "dhruvildave/spotify-charts", "./data", "./data/spotify-charts.zip"
    path = fetch_spotify_dataset(dataset, dir_path, dataset_path)
    for i, chunk_df in get_large_file_by_chunks(path):
        cleaned_chunk = clean(chunk_df)
        chunk_file_path = Path(f"./data/chunks/charts_{i}.csv")
        write_gcs(cleaned_chunk, chunk_file_path)


if __name__ == "__main__":
    etl_web_to_gcs()
