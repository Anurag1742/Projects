import os
import hashlib
import shutil
import datetime
import json

RECOVERY_FOLDER = "recovery_logs"
DUPLICATE_FOLDER = "duplicates"
TRASH_FOLDER = "trash_bin"
DELETED_LOGS_FOLDER = "deleted_file_logs"  # New folder for storing log files

# Generate hash for a file
def get_file_hash(filepath):
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as file:
            while chunk := file.read(4096):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"[Error] Unable to read file: {filepath}. Skipped. ({e})")
        return None

# Recursively find duplicates in a folder
def find_duplicates(folder_path):
    print(f"\n🔍 Scanning folder: {folder_path}\n")
    hash_map = {}
    duplicates = []

    for root, _, files in os.walk(folder_path):
        for file in sorted(files):
            full_path = os.path.join(root, file)
            file_hash = get_file_hash(full_path)
            if file_hash:
                if file_hash in hash_map:
                    duplicates.append((full_path, hash_map[file_hash]))
                else:
                    hash_map[file_hash] = full_path
    return duplicates

# Take action on duplicates
def handle_duplicates(duplicates, action):
    log_entries = []
    recovery_data = {}
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"duplicate_log_{timestamp}.txt"
    recovery_file = os.path.join(RECOVERY_FOLDER, f"recovery_{timestamp}.json")

    os.makedirs(RECOVERY_FOLDER, exist_ok=True)
    os.makedirs(DELETED_LOGS_FOLDER, exist_ok=True)  # Ensure log folder exists
    
    if action == "move":
        os.makedirs(DUPLICATE_FOLDER, exist_ok=True)
    if action == "safe_delete":
        os.makedirs(TRASH_FOLDER, exist_ok=True)

    for dup, original in duplicates:
        try:
            if action == "move":
                dest = os.path.join(DUPLICATE_FOLDER, os.path.basename(dup))
                if os.path.exists(dest):
                    base, ext = os.path.splitext(dest)
                    dest = f"{base}_{datetime.datetime.now().timestamp():.0f}{ext}"
                shutil.move(dup, dest)
                log_entries.append(f"Moved: {dup} → {dest}")
                recovery_data[dup] = {"action": "move", "from": dest, "to": dup}

            elif action == "safe_delete":
                dest = os.path.join(TRASH_FOLDER, os.path.basename(dup))
                if os.path.exists(dest):
                    base, ext = os.path.splitext(dest)
                    dest = f"{base}_{datetime.datetime.now().timestamp():.0f}{ext}"
                shutil.move(dup, dest)
                log_entries.append(f"Safely Deleted (moved to trash): {dup} → {dest}")
                recovery_data[dup] = {"action": "safe_delete", "from": dest, "to": dup}

            elif action == "permanent_delete":
                os.remove(dup)
                log_entries.append(f"Permanently Deleted: {dup}")
                recovery_data[dup] = {"action": "permanent_delete"}

            else:
                log_entries.append(f"Duplicate found: {dup} (Original: {original})")

        except Exception as e:
            log_entries.append(f"[Error] Failed to process {dup}: {e}")

    # Write the duplicate log file with utf-8 encoding
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("\n".join(log_entries))

    # Move the log file into the deleted_file_logs folder
    shutil.move(log_file, os.path.join(DELETED_LOGS_FOLDER, log_file))

    # Write the recovery JSON log
    with open(recovery_file, "w", encoding="utf-8") as f:
        json.dump(recovery_data, f, indent=4)

    print(f"\n✅ Action completed. Log saved to `{os.path.join(DELETED_LOGS_FOLDER, log_file)}`.")
    print(f"♻️ Recovery log saved to `{recovery_file}`.")

# Print summary
def preview_duplicates(duplicates):
    if not duplicates:
        print("\n✅ No duplicates found.")
        return
    print(f"\n📁 Found {len(duplicates)} duplicate files:\n")
    for dup, original in duplicates:
        print(f"- {dup}\n  ↪ Original: {original}\n")

# Recover from recovery log
def recover_files():
    os.makedirs(RECOVERY_FOLDER, exist_ok=True)
    logs = sorted([f for f in os.listdir(RECOVERY_FOLDER) if f.endswith(".json")])

    if not logs:
        print("❌ No recovery logs found in 'recovery_logs'.")
        return

    print(f"\n📝 Found {len(logs)} recovery log(s) in '{RECOVERY_FOLDER}':")
    for idx, log in enumerate(logs, 1):
        print(f"{idx}. {log}")

    try:
        choice = input("\n🔢 Enter the log number to restore [1-{}] or 0 to cancel: ".format(len(logs))).strip()
        if not choice.isdigit() or int(choice) == 0:
            print("🔙 Recovery cancelled.")
            return

        log_index = int(choice) - 1
        if log_index < 0 or log_index >= len(logs):
            print("❌ Invalid choice.")
            return

        recovery_file = os.path.join(RECOVERY_FOLDER, logs[log_index])
        with open(recovery_file, "r", encoding="utf-8") as f:
            recovery_data = json.load(f)

        for original, action_info in recovery_data.items():
            if action_info["action"] == "move" or action_info["action"] == "safe_delete":
                try:
                    shutil.move(action_info["from"], action_info["to"])
                    print(f"✅ Restored: {action_info['from']} → {action_info['to']}")
                except Exception as e:
                    print(f"❌ Failed to restore {action_info['from']}: {e}")
            elif action_info["action"] == "permanent_delete":
                print(f"⚠️ Cannot recover permanently deleted file: {original} → Reason: File was permanently deleted.")

        print("\n♻️ Recovery attempt completed.")

    except Exception as e:
        print(f"❌ Error during recovery: {e}")

# Main Menu
def main():
    print("=== 🔁 Duplicate File Remover ===\n")
    print("1. Scan folder and manage duplicates")
    print("2. Recover from last action")
    print("3. Exit")

    main_choice = input("\nEnter your choice [1-3]: ").strip()

    if main_choice == "1":
        folder = input("📂 Enter folder path to scan: ").strip()
        if not os.path.isdir(folder):
            print("\n❌ Invalid folder path.")
            return

        duplicates = find_duplicates(folder)
        if not duplicates:
            print("\n✅ No duplicates found.")
            return

        print("\nChoose an action:")
        print("1. Preview only")
        print("2. Move duplicates to `duplicates/` folder")
        print("3. Safe delete (recoverable)")
        print("4. Permanent delete (NOT recoverable)")
        print("5. Exit")

        choice = input("\nEnter your choice [1-5]: ").strip()

        if choice == "1":
            preview_duplicates(duplicates)
        elif choice == "2":
            handle_duplicates(duplicates, "move")
        elif choice == "3":
            handle_duplicates(duplicates, "safe_delete")
        elif choice == "4":
            confirm = input("⚠️ Are you sure you want to permanently delete duplicates? [yes/no]: ").lower()
            if confirm == "yes":
                handle_duplicates(duplicates, "permanent_delete")
            else:
                print("❌ Permanent deletion cancelled.")
        else:
            print("👋 Exiting. No action taken.")

    elif main_choice == "2":
        recover_files()
    else:
        print("👋 Goodbye!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user. Exiting...")
