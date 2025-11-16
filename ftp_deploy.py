#!/usr/bin/env python3
import ftplib
import os
import argparse
from datetime import datetime
import fnmatch
import json
import hashlib
import shutil
import subprocess
import sys

def read_config():
    """Reads configuration from .ftprules file"""
    config = {}
    current_section = None
    
    with open('.ftprules', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                config[current_section] = []
            elif current_section:
                config[current_section].append(line)
    
    return {
        'host': config.get('remote', [''])[0] if config.get('remote') else '',
        'user': config.get('user', [''])[0] if config.get('user') else '',
        'password': config.get('password', [''])[0] if config.get('password') else '',
        'remote_folder': config.get('remote-folder', [''])[0] if config.get('remote-folder') else '',
        'origin': config.get('origin', [''])[0] if config.get('origin') else '',
        'exclude': config.get('ignore', [])
    }

def should_exclude(filepath, exclude_patterns):
    """Checks if file should be excluded"""
    # Normaliza o caminho para usar barras
    filepath_normalized = filepath.replace('\\', '/')
    
    for pattern in exclude_patterns:
        if pattern.endswith('/'):
            # It's a folder - check if path contains exactly this folder
            folder_name = pattern.rstrip('/')
            # Check if it's exactly the folder (with separators)
            if f'/{folder_name}/' in f'/{filepath_normalized}/' or filepath_normalized.startswith(f'{folder_name}/'):
                return True
        else:
            # It's a file or pattern - use fnmatch
            if fnmatch.fnmatch(filepath_normalized, pattern):
                return True
    return False

def create_remote_dirs(ftp, remote_path):
    """Creates remote directories if they don't exist (supports nested paths)"""
    # Go back to root directory
    try:
        ftp.cwd('/')
    except:
        pass
    
    # Split path into parts
    dirs = [d for d in remote_path.split('/') if d]
    
    for i, dir_name in enumerate(dirs):
        try:
            # Try to navigate to directory
            ftp.cwd(dir_name)
        except ftplib.error_perm:
            # If it doesn't exist, try to create it
            try:
                ftp.mkd(dir_name)
                ftp.cwd(dir_name)
            except ftplib.error_perm as e:
                print(f"Error creating {dir_name}: {e}")
                return False
    
    return True

def load_cache():
    """Loads cache of uploaded files"""
    try:
        with open('.ftp_cache.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_cache(cache):
    """Saves cache of uploaded files"""
    with open('.ftp_cache.json', 'w') as f:
        json.dump(cache, f, indent=2)

def get_file_hash(filepath):
    """Calculates MD5 hash of file"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def should_upload_file(filepath, local_time, force=False):
    """Checks if file should be uploaded based on local cache"""
    if force:
        return True
    
    cache = load_cache()
    file_key = os.path.normpath(filepath)
    
    # If file is not in cache, should upload
    if file_key not in cache:
        return True
    
    cached_info = cache[file_key]
    
    # Compare modification timestamp
    cached_mtime = datetime.fromisoformat(cached_info.get('mtime', '1970-01-01'))
    if local_time > cached_mtime:
        return True
    
    # Compare file hash (more reliable)
    try:
        current_hash = get_file_hash(filepath)
        if current_hash != cached_info.get('hash'):
            return True
    except:
        return True  # If can't calculate hash, upload for safety
    
    return False

def update_cache(filepath, local_time):
    """Updates cache after successful upload"""
    cache = load_cache()
    file_key = os.path.normpath(filepath)
    
    try:
        file_hash = get_file_hash(filepath)
        cache[file_key] = {
            'mtime': local_time.isoformat(),
            'hash': file_hash,
            'uploaded_at': datetime.now().isoformat()
        }
        save_cache(cache)
    except Exception as e:
        print(f"Warning: Could not update cache for {filepath}: {e}")

def clean_cache():
    """Removes cache entries for files that no longer exist locally"""
    cache = load_cache()
    files_to_remove = []
    
    for cached_file in cache.keys():
        if not os.path.exists(cached_file):
            files_to_remove.append(cached_file)
    
    if files_to_remove:
        for file_path in files_to_remove:
            del cache[file_path]
        save_cache(cache)
        print(f"Cache cleanup: {len(files_to_remove)} entries removed")

def get_remote_file_time(ftp, filepath):
    """Gets remote file timestamp"""
    try:
        response = ftp.sendcmd(f'MDTM {filepath}')
        if response.startswith('213'):
            time_str = response[4:].strip()
            return datetime.strptime(time_str, '%Y%m%d%H%M%S')
    except:
        pass
    return None

def upload_file(ftp, local_path, remote_path, dry_run=False):
    """Uploads a file"""
    if dry_run:
        print(f"[DRY-RUN] Would upload: {local_path} -> {remote_path}")
        return
    
    try:
        with open(local_path, 'rb') as file:
            ftp.storbinary(f'STOR {remote_path}', file)
        print(f"Uploaded: {local_path} -> {remote_path}")
    except Exception as e:
        print(f"Error uploading {local_path}: {e}")

def get_script_dir():
    """Returns the directory where the script is located"""
    return os.path.dirname(os.path.abspath(__file__))

def create_example_config():
    """Creates default .ftprules.example file in script folder"""
    example_content = """[remote]
ftp.yourserver.com

[user]
yourusername

[password]
yourpassword

[remote-folder]
www/remotefoldername

[origin]
dist

[ignore]
TEMP/
"""
    
    script_dir = get_script_dir()
    example_file = os.path.join(script_dir, '.ftprules.example')
    
    with open(example_file, 'w', encoding='utf-8') as f:
        f.write(example_content)
    
    print(f"Default template created at: {example_file}")
    print("You can edit this file to customize your template.")
    
    return example_file

def init_config():
    """Initializes configuration by copying .ftprules.example from script folder"""
    script_dir = get_script_dir()
    example_file = os.path.join(script_dir, '.ftprules.example')
    target_file = '.ftprules'
    
    # Check if .ftprules already exists in current folder
    if os.path.exists(target_file):
        print(f"File {target_file} already exists in current folder.")
        return
    
    # If .ftprules.example doesn't exist in script folder, create default template
    if not os.path.exists(example_file):
        print("Template .ftprules.example not found in script folder.")
        example_file = create_example_config()
    else:
        print(f"Using custom template: {example_file}")
    
    # Copy template to current folder
    try:
        shutil.copy2(example_file, target_file)
        print(f"File {target_file} created successfully!")
        print("Edit the .ftprules file with your specific FTP settings.")
    except Exception as e:
        print(f"Error creating {target_file}: {e}")

def open_config_folder():
    """Opens script folder in explorer"""
    script_dir = get_script_dir()
    try:
        if os.name == 'nt':  # Windows
            os.startfile(script_dir)
        elif os.name == 'posix':  # Linux/Mac
            subprocess.run(['xdg-open', script_dir])
        print(f"Script folder opened: {script_dir}")
    except Exception as e:
        print(f"Error opening folder: {e}")
        print(f"Script folder: {script_dir}")

def main():
    parser = argparse.ArgumentParser(
        description='Automated FTP deployment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Usage examples:
  ftp_deploy                      # Normal deploy
  ftp_deploy --dry-run            # Shows what would be uploaded
  ftp_deploy --force              # Forces upload of all files
  ftp_deploy --init               # Creates .ftprules using template
  ftp_deploy --open-config-folder # Opens script folder to edit template"""
    )
    
    parser.add_argument('--dry-run', action='store_true', help='Shows what would be uploaded without uploading')
    parser.add_argument('--force', action='store_true', help='Forces upload of all files')
    parser.add_argument('--init', action='store_true', help='Creates .ftprules file using template')
    parser.add_argument('--open-config-folder', action='store_true', help='Opens script folder to edit template')
    
    args = parser.parse_args()
    
    # Special commands
    if args.init:
        init_config()
        return
    
    if args.open_config_folder:
        open_config_folder()
        return
    
    # Check if .ftprules exists
    if not os.path.exists('.ftprules'):
        print("Error: .ftprules file not found in current folder.")
        print("Use 'ftp_deploy --init' to create a configuration file.")
        return
    
    # Read configuration
    try:
        config = read_config()
    except FileNotFoundError:
        print("Error: .ftprules file not found.")
        print("Use 'ftp_deploy --init' to create a configuration file.")
        return
    except Exception as e:
        print(f"Error reading .ftprules: {e}")
        return
    
    if not config['host']:
        print("Error: Host not found in .ftprules")
        print("Check if .ftprules file is configured correctly.")
        return
    
    print(f"Connecting to {config['host']}...")
    
    try:
        # Connect to FTP
        ftp = ftplib.FTP(config['host'])
        ftp.login(config['user'], config['password'])
        
        # Create and access remote folder
        if not create_remote_dirs(ftp, config['remote_folder']):
            print(f"Error: Could not create/access folder {config['remote_folder']}")
            return
        
        files_to_upload = []
        files_to_delete = []
        files_to_rename = []
        
        # Check if origin folder exists
        origin_folder = config['origin']
        if not origin_folder:
            print("Error: Origin folder not specified in .ftprules")
            return
        
        if not os.path.isdir(origin_folder):
            print(f"Error: Origin folder '{origin_folder}' does not exist")
            return
        
        # Process origin folder
        if True:
            # Walk through origin folder recursively
            for root, dirs, files in os.walk(origin_folder):
                for file in files:
                    local_path = os.path.join(root, file)
                    
                    # Check if should exclude
                    if should_exclude(local_path, config['exclude']):
                        continue
                    
                    # Relative path for FTP
                    rel_path = os.path.relpath(local_path, origin_folder)
                    remote_path = rel_path.replace('\\', '/')
                    
                    # Check if needs update
                    local_time = datetime.fromtimestamp(os.path.getmtime(local_path))
                    
                    # Check if needs to upload based on local cache
                    should_upload = should_upload_file(local_path, local_time, args.force)
                    
                    if should_upload:
                        files_to_upload.append((local_path, remote_path))
        
        # Check files to delete (that were in cache but no longer exist locally)
        cache = load_cache()
        current_files = set()
        
        # Collect all current files from origin folder
        for root, dirs, files in os.walk(origin_folder):
            for file in files:
                local_path = os.path.join(root, file)
                if not should_exclude(local_path, config['exclude']):
                    current_files.add(os.path.normpath(local_path))
        
        # Detect renames and removed files
        deleted_files = {}
        
        # Collect removed files (were in cache but no longer exist)
        for cached_file in cache.keys():
            if cached_file not in current_files and not os.path.exists(cached_file):
                cached_hash = cache[cached_file].get('hash')
                if cached_hash:
                    deleted_files[cached_hash] = cached_file
        
        # Collect new files and check if they are renames
        for local_path, remote_path in files_to_upload[:]:
            try:
                file_hash = get_file_hash(local_path)
                if file_hash in deleted_files:
                    # It's a rename!
                    old_file = deleted_files[file_hash]
                    # Calculate old remote path
                    if old_file.startswith(os.path.normpath(origin_folder)):
                        old_remote_path = os.path.relpath(old_file, origin_folder).replace('\\', '/')
                        files_to_rename.append((old_remote_path, remote_path, local_path))
                        # Remove from upload and delete lists
                        files_to_upload.remove((local_path, remote_path))
                        del deleted_files[file_hash]
            except:
                pass  # If can't calculate hash, keep as normal upload
        
        # Files remaining in deleted_files are actually removed
        for cached_file in deleted_files.values():
            if cached_file.startswith(os.path.normpath(origin_folder)):
                rel_path = os.path.relpath(cached_file, origin_folder)
                remote_path = rel_path.replace('\\', '/')
                files_to_delete.append((cached_file, remote_path))
        
        if not files_to_upload and not files_to_delete and not files_to_rename:
            print("No files need to be updated.")
            return
        
        if files_to_upload:
            print(f"\nFiles to be uploaded: {len(files_to_upload)}")
            for local_path, remote_path in files_to_upload:
                print(f"  {local_path} -> {remote_path}")
        
        if files_to_delete:
            print(f"\nFiles to be removed: {len(files_to_delete)}")
            for local_path, remote_path in files_to_delete:
                print(f"  {remote_path} (removed locally)")
        
        if files_to_rename:
            print(f"\nFiles to be renamed: {len(files_to_rename)}")
            for old_remote, new_remote, local_path in files_to_rename:
                print(f"  {old_remote} -> {new_remote}")
        
        if not args.dry_run:
            # Upload files
            if files_to_upload:
                print("\nStarting upload...")
                for local_path, remote_path in files_to_upload:
                    # Create remote directories if necessary
                    remote_dir = '/'.join(remote_path.split('/')[:-1])
                    if remote_dir:
                        create_remote_dirs(ftp, config['remote_folder'] + '/' + remote_dir)
                        create_remote_dirs(ftp, config['remote_folder'])
                    
                    upload_file(ftp, local_path, remote_path)
                    # Update cache after successful upload
                    local_time = datetime.fromtimestamp(os.path.getmtime(local_path))
                    update_cache(local_path, local_time)
            
            # Rename files
            if files_to_rename:
                print("\nRenaming files...")
                create_remote_dirs(ftp, config['remote_folder'])
                
                for old_remote, new_remote, local_path in files_to_rename:
                    try:
                        # Create destination directory if necessary
                        new_dir = '/'.join(new_remote.split('/')[:-1])
                        if new_dir:
                            create_remote_dirs(ftp, config['remote_folder'] + '/' + new_dir)
                            create_remote_dirs(ftp, config['remote_folder'])
                        
                        # Rename on FTP server
                        ftp.rename(old_remote, new_remote)
                        print(f"Renamed: {old_remote} -> {new_remote}")
                        
                        # Update cache
                        cache = load_cache()
                        # Remove old entry
                        old_cache_key = None
                        for key, value in cache.items():
                            if value.get('hash') == get_file_hash(local_path):
                                old_cache_key = key
                                break
                        if old_cache_key:
                            del cache[old_cache_key]
                        
                        # Add new entry
                        local_time = datetime.fromtimestamp(os.path.getmtime(local_path))
                        update_cache(local_path, local_time)
                        
                    except Exception as e:
                        print(f"Error renaming {old_remote}: {e}")
            
            # Remove files
            if files_to_delete:
                print("\nRemoving files...")
                create_remote_dirs(ftp, config['remote_folder'])
                
                for local_path, remote_path in files_to_delete:
                    try:
                        ftp.delete(remote_path)
                        print(f"Removed: {remote_path}")
                        # Remove from cache
                        cache = load_cache()
                        if local_path in cache:
                            del cache[local_path]
                            save_cache(cache)
                    except Exception as e:
                        print(f"Error removing {remote_path}: {e}")
        
        # Clean orphaned cache entries
        clean_cache()
        
        ftp.quit()
        print(f"\nDeploy completed to {config['host']}/{config['remote_folder']}!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()