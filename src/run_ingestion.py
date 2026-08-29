from ingestion.pipeline import ingest_directory
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        data_dir = "data"  # default
    ingest_directory(data_dir)