from pathlib import Path
from typing import List
import json


def get_uploaded_file_names(
    directory: str | Path, extension: str | None = None
) -> List[str]:
    """
    Fetch all file names (without extensions) from the specified upload directory.

    Args:
        directory (str | Path): Path to the upload directory.
        extension (str | None): Optional extension filter (e.g. '.json').

    Returns:
        List[str]: List of file names without extensions.
    """
    upload_dir = Path(directory)
    if not upload_dir.exists():
        raise FileNotFoundError(f"Upload directory not found: {upload_dir}")

    # Get files (filtered if extension provided)
    if extension:
        files = upload_dir.glob(f"*{extension}")
    else:
        files = upload_dir.iterdir()

    # Return names without extension
    return [f.stem for f in files if f.is_file()]


def load_json_from_file(directory: str | Path, filename: str) -> dict:
    """
    Load JSON data from a file in the given directory.

    Args:
        directory (str | Path): Directory where the JSON file is stored.
        filename (str): Name of the file (with or without '.json' extension).

    Returns:
        dict: Parsed JSON content.
    """
    upload_dir = Path(directory)
    if not upload_dir.exists():
        raise FileNotFoundError(f"Upload directory not found: {upload_dir}")

    # Ensure file has .json extension
    file_path = upload_dir / (
        filename if filename.endswith(".json") else f"{filename}.json"
    )

    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    # Read and parse JSON
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data
