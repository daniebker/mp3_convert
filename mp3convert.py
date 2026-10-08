#!/usr/bin/env python3
import argparse
import csv
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Recursively convert FLAC and WAV files to MP3."
    )
    parser.add_argument("input_dir", type=Path, help="Directory to scan")
    parser.add_argument("output_dir", type=Path, help="Base directory for MP3 output")
    parser.add_argument("--bitrate", default="320k", help="MP3 bitrate (default: 320k)")
    parser.add_argument(
        "--errors-csv",
        type=Path,
        help="CSV path for conversion failures "
             "(default: OUTPUT_DIR/conversion_errors.csv)",
    )
    args = parser.parse_args()

    source = args.input_dir.resolve()
    destination = args.output_dir.resolve()
    errors_csv = args.errors_csv or destination / "conversion_errors.csv"

    if not source.is_dir():
        parser.error(f"Input directory does not exist: {source}")

    destination.mkdir(parents=True, exist_ok=True)
    errors_csv.parent.mkdir(parents=True, exist_ok=True)

    with errors_csv.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["file", "error"])

        for audio_file in source.rglob("*"):
            if not audio_file.is_file():
                continue
            if audio_file.suffix.lower() not in {".flac", ".wav"}:
                continue

            # macOS metadata sidecars are not audio files.
            if audio_file.name.startswith("._"):
                writer.writerow([str(audio_file), "Skipped macOS metadata sidecar"])
                print(f"Skipping metadata sidecar: {audio_file}")
                continue

            relative_path = audio_file.relative_to(source)
            mp3 = (destination / relative_path).with_suffix(".mp3")

            if mp3.exists():
                print(f"Skipping existing MP3: {mp3}")
                continue

            mp3.parent.mkdir(parents=True, exist_ok=True)

            command = [
                "ffmpeg", "-hide_banner", "-nostdin", "-y",
                "-i", str(audio_file),
            ]

            cover = audio_file.parent / "cover.jpg"
            if cover.is_file():
                command += [
                    "-i", str(cover),
                    "-map", "0:a",
                    "-map", "1:v",
                    "-c:v", "mjpeg",
                    "-id3v2_version", "3",
                    "-metadata:s:v", "title=Album cover",
                    "-metadata:s:v", "comment=Cover (front)",
                ]
            else:
                command += ["-map", "0:a"]

            command += [
                "-map_metadata", "0",
                "-c:a", "libmp3lame",
                "-b:a", args.bitrate,
                str(mp3),
            ]

            print(f"Converting: {audio_file} -> {mp3}")
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:
                error = result.stderr.strip() or (
                    f"FFmpeg exited with code {result.returncode}"
                )
                writer.writerow([str(audio_file), error])
                csv_file.flush()
                print(f"Failed; logged to {errors_csv}")
                if result.stderr:
                    print(result.stderr.strip())
            else:
                print(f"Converted: {mp3}")

    print(f"Finished. Failed/skipped files are listed in: {errors_csv}")


if __name__ == "__main__":
    main()

