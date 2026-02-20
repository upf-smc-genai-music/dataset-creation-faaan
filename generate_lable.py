import os
import shutil
import wave
import json
import math

# Configuration
SOURCE_DIR = "wav"
TARGET_DIR = "raw"
FRAME_RATE_CSV = 75  # Lines per second of audio


def prepare_dataset():
    # Ensure target directory exists
    os.makedirs(TARGET_DIR, exist_ok=True)

    # 1. Generate parameters.json
    params_data = {
        "parameter_1": {
            "name": "fan_speed",
            "type": "continuous",
            "unit": "level",
            "min": 0,
            "max": 100
        }
    }
    params_path = os.path.join(TARGET_DIR, "parameters.json")
    with open(params_path, "w", encoding="utf-8") as f:
        json.dump(params_data, f, indent=4)
    print(f"📄 Successfully generated: {params_path}")

    # 2. Define file mapping (Source -> Target Name & Value)
    file_mapping = {"roomenoise.wav": {"target_name": "fan_0", "speed_value": 0}}
    for i in range(1, 101):
        file_mapping[f"{i}.wav"] = {"target_name": f"fan_{i}", "speed_value": i}

    # 3. Processing loop
    success_count = 0

    for src_filename, info in file_mapping.items():
        src_path = os.path.join(SOURCE_DIR, src_filename)

        if not os.path.exists(src_path):
            continue  # Silently skip missing files or add a print if debugging

        target_name = info["target_name"]
        speed_value = info["speed_value"]

        target_wav_path = os.path.join(TARGET_DIR, f"{target_name}.wav")
        target_csv_path = os.path.join(TARGET_DIR, f"{target_name}.csv")

        # Copy WAV file
        shutil.copy2(src_path, target_wav_path)

        # Calculate duration and row count
        try:
            with wave.open(target_wav_path, 'r') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)

                # Using math.ceil or round to ensure CSV length matches audio frame chunks
                num_rows = int(round(duration * FRAME_RATE_CSV))
        except Exception as e:
            print(f"❌ Error processing {src_filename}: {e}")
            continue

        # Write CSV with column headers
        with open(target_csv_path, 'w', encoding='utf-8') as csv_file:
            csv_file.write("fan_speed\n")
            # Efficiently write multiple rows
            content = f"{speed_value}\n" * num_rows
            csv_file.write(content)

        print(f"✅ Processed: {src_filename} -> {target_name} ({duration:.2f}s, {num_rows} rows)")
        success_count += 1

    print(f"\n🎉 Task Complete! Successfully processed {success_count} files.")
    print(f"📁 Dataset location: {os.path.abspath(TARGET_DIR)}")


if __name__ == "__main__":
    prepare_dataset()