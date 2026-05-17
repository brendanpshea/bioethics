from pathlib import Path
import urllib.request


HEADERS = {
    "User-Agent": "BioethicsCourseBot/1.0 (https://github.com/brendanpshea/bioethics)"
}

IMAGES = [
    ("hippocrates.jpg", "https://commons.wikimedia.org/wiki/Special:Redirect/file/Hippocrates_rubens.jpg"),
    ("nuremberg_trial.jpg", "https://commons.wikimedia.org/wiki/Special:Redirect/file/Doctors_Trial.jpg"),
    ("tuskegee.jpg", "https://commons.wikimedia.org/wiki/Special:Redirect/file/Tuskegee-syphilis-study_doctor-injecting-subject.jpg"),
    ("willowbrook.jpg", "https://commons.wikimedia.org/wiki/Special:Redirect/file/Willowbrook_State_School_(NYPL_b15279351-105038)_-_cropped.jpg"),
    ("the_doctor_fildes.jpg", "https://upload.wikimedia.org/wikipedia/commons/8/84/The_Doctor_Luke_Fildes_crop.jpg"),
    ("doctor_patient_jan_steen.jpg", "https://upload.wikimedia.org/wikipedia/commons/8/81/Steen_Doctor_and_His_Patient.jpg"),
]


def is_valid_jpeg(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 3:
        return False
    with path.open("rb") as file_obj:
        return file_obj.read(3) == b"\xff\xd8\xff"


def main() -> None:
    repo_root = Path(__file__).resolve().parent
    images_dir = repo_root / "images"
    images_dir.mkdir(exist_ok=True)

    for name, url in IMAGES:
        destination = images_dir / name
        if is_valid_jpeg(destination):
            print(f"Skipped {name} (already present)")
            continue
        if destination.exists():
            print(f"Re-downloading {name} (existing file is not a valid JPEG)")
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req) as response, destination.open("wb") as out_file:
                out_file.write(response.read())
            print(f"Downloaded {name}")
        except Exception as exc:
            print(f"Error downloading {name}: {exc}")


if __name__ == "__main__":
    main()
