import requests
import os
from pathlib import Path
from langchain_core.tools import tool

# Define the base directory for all projects
BASE = (Path.cwd() / "Generated Projects").resolve()


def resolve_path(project_name: str, path: str) -> Path:
    """
    Safely resolve a project-relative path.
    Prevents directory traversal attacks (e.g., "../secrets").
    """
    project_root = (BASE / project_name).resolve()
    full_path = (project_root / path).resolve()

    # Security Check: Ensure the resolved path is within the project root
    if project_root not in full_path.parents and project_root != full_path:
        raise ValueError(f"Security Error: Path '{path}' is outside project '{project_name}'")

    return full_path


@tool
def create_project_folder(project_name: str) -> str:
    """Create the root folder for a project."""
    project_path = BASE / project_name
    project_path.mkdir(parents=True, exist_ok=True)
    return f"Project folder ready at: {project_path}"


@tool
def create_file(project_name: str, path: str) -> str:
    """Create an empty file at the given relative path."""
    file_path = resolve_path(project_name, path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.touch(exist_ok=True)
    return f"Created file: {file_path}"


@tool
def write_file(project_name: str, path: str, content: str) -> str:
    """
    Write (or create if missing) a file with the given content.
    More reliable than strict 'file must exist' behavior.
    """
    file_path = resolve_path(project_name, path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"Written: {file_path}"


@tool
def update_file(project_name: str, path: str, content: str) -> str:
    """Update an existing file. Raises error if missing."""
    file_path = resolve_path(project_name, path)

    if not file_path.exists():
        raise FileNotFoundError(f"Error: '{path}' does not exist in project '{project_name}'")

    file_path.write_text(content, encoding="utf-8")
    return f"Updated: {file_path}"


@tool
def read_file(project_name: str, path: str) -> str:
    """Read a file and return its content."""
    file_path = resolve_path(project_name, path)

    if not file_path.exists():
        raise FileNotFoundError(f"Error: '{path}' does not exist in project '{project_name}'")

    return file_path.read_text(encoding="utf-8")


@tool
def list_project_files(project_name: str) -> str:
    """List all files in the project."""
    project_path = (BASE / project_name).resolve()

    if not project_path.exists():
        raise FileNotFoundError(f"Project '{project_name}' does not exist")

    # Use rglob("*") to list all files recursively
    files = [
        str(p.relative_to(project_path))
        for p in project_path.rglob("*")
        if p.is_file()
    ]
    return "\n".join(files) if files else "No files found."

@tool
def get_relevant_image(query: str, orientation: str = "landscape"):
    """Searches Pexels for a relevant image based on the query."""
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")  # Store in your .env file
    headers = {"Authorization": PEXELS_API_KEY}

    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1&orientation={orientation}"

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if data['photos']:
            # Returns the medium sized image URL
            return data['photos'][0]['src']['medium']
        else:
            return "https://via.placeholder.com/800x400?text=No+Image+Found"
    except Exception as e:
        return "https://via.placeholder.com/800x400?text=Error"