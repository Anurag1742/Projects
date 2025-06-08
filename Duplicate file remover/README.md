

# 🗂️ Duplicate File Remover

## 🔍 Overview

The **Duplicate File Remover** is a Python-based utility designed to efficiently scan directories for duplicate files and provide flexible options to manage them. Duplicate files waste valuable disk space, slow down file searches, and clutter your system. This tool helps maintain a clean and organized storage by detecting duplicates using SHA-256 hashing and allowing users to preview, move, safely delete (recoverable), or permanently delete files.

## ✨ Features

* 🔄 **Recursive folder scanning** for duplicate files.
* 🔐 Uses **SHA-256 hash** to reliably identify duplicates regardless of filename.
* ⚙️ Multiple management options:

  * 👀 Preview duplicates without any changes.
  * 📂 Move duplicates to a designated `duplicates/` folder.
  * 🗑️ Safe delete duplicates by moving them to a `trash_bin/` folder (recoverable).
  * ❌ Permanent delete duplicates with no recovery.
* 📝 **Automatic logging** of all operations with timestamps.
* ♻️ **Recovery system** to restore safely deleted or moved files using saved logs.
* ⚠️ Handles errors gracefully and provides informative messages.
* 📁 Organized folder structure for duplicates, trash, and recovery logs.

## 🛠️ Installation

1. Ensure you have **Python 3.6+** installed.
2. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/duplicate-file-remover.git
   ```
3. Navigate to the project directory:

   ```bash
   cd duplicate-file-remover
   ```
4. No external libraries are required as only Python standard libraries are used.

## ▶️ Usage

Run the script using Python in your terminal or command prompt:

```bash
python duplicate_file_remover.py
```

Follow the interactive prompts to:

* 📂 Enter the folder path to scan.
* ⚙️ Choose how you want to handle duplicates.
* 🔄 Optionally recover files from previous safe deletions.

## 📂 Folder Structure Created

* `duplicates/` — Contains files moved as duplicates.
* `trash_bin/` — Contains files that are safely deleted (recoverable).
* `recovery_logs/` — JSON logs storing details for file recovery.
* `deleted_file_logs/` — Stores log text files for previous actions.

## ⚙️ How It Works

* The program calculates SHA-256 hashes for all files in the target directory and subdirectories.
* Files with matching hashes are identified as duplicates.
* Based on user input, duplicates can be previewed, moved, safely deleted, or permanently deleted.
* Operations are logged with timestamps for traceability and recovery.
* Recovery feature uses saved logs to restore files moved or safely deleted.

## ⚠️ Limitations

* Permanent deletion is irreversible; use with caution.
* Recovery only applies to files moved to `duplicates/` or `trash_bin/`.
* Large directories with many files may take time due to hashing.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to open a pull request or issue.

## 📄 License

This project is licensed under the MIT License.


