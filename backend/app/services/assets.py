from pathlib import Path


def _cv_stem(cv_file_path: str) -> str:
    return Path(cv_file_path.replace("\\", "/")).stem


def pdf_path_for_cv(cv_file_path: str) -> str:
    if not cv_file_path:
        return ""
    base = _cv_stem(cv_file_path)
    return str(Path("_batch_pdf") / f"{base}.pdf")


def png_preview_path_for_cv(cv_file_path: str) -> str:
    if not cv_file_path:
        return ""
    base = _cv_stem(cv_file_path)
    return str(Path("_batch_png") / base / "page-1.png")


def asset_exists(package_root: Path, relative_path: str) -> bool:
    return bool(relative_path) and (package_root / relative_path).exists()
