# GoProMerger

GoProMerger is a Python tool designed to **merge GoPro chaptered video files** while **preserving metadata**. It uses **FFmpeg** and **ExifTool** to concatenate video parts and retain metadata .  
It is a fast solution that works by combining file parts rather than reencoding the entire video .

## 🚀 Features
- Automatically detects GoPro video parts.
- Merges them into a single video file.
- Retains metadata from the original parts.
- Optionally includes global metadata.
- Allows listing of available videos and their parts.
- Supports extracting metadata separately.

---

## 🛠️ Requirements

Ensure you have the following installed:

- **Python 3**
- **FFmpeg** (for video processing)
- **ExifTool** (for metadata handling)

You can install FFmpeg and ExifTool using:

```bash
sudo apt install ffmpeg exiftool  # For Debian/Ubuntu
brew install ffmpeg exiftool      # For macOS
```

---

## 📌 Usage

Run the script with the appropriate flags:

```bash
python gopro_merger.py -b /path/to/videos [OPTIONS]
```

### **Available Options**

| Option                  | Description |
|-------------------------|-------------|
| `-b, --base_path`       | **(Required)** Path to the directory containing GoPro video parts. |
| `--list_videos`         | Lists detected videos and their parts. |
| `--merge`               | Merges video parts into a single video while preserving metadata. |
| `--dump_metadata`       | Extracts metadata from each video part. |
| `--add_global_metadata` | Injects global metadata into the final video (may rewrite the file). |
| `--video_number`        | Processes only the specified video number. |

---

## 🔥 Examples

### **1️⃣ List available videos and their parts**
```bash
python gopro_merger.py -b /path/to/videos --list_videos
```

### **2️⃣ Merge GoPro video parts into a single file**
```bash
python gopro_merger.py -b /path/to/videos --merge
```

### **3️⃣ Merge a specific video **
```bash
python gopro_merger.py -b /path/to/videos --merge --video_number 238
```
---

## 📌 How It Works
1. **Detects GoPro video parts** based on filename patterns.
2. **Extracts metadata** using FFmpeg.
3. **Groups related parts** based on video id.
4. **Concatenates them without reeconding** while preserving metadata.
5. **(Optional)** Injects global metadata into the final video.

---

## ❗ Notes
- **Global metadata injection** (`--add_global_metadata`) rewrites the file for a second time, which may cause stress on the hard drive.
- Make sure FFmpeg and ExifTool are installed and accessible from the command line.
