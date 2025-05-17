import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

def find_icon_file(folder):
    for ext in ['png', 'ico', 'jpg', 'jpeg', 'bmp']:
        icon = Path(folder) / f'icon.{ext}'
        if icon.exists():
            return icon
    return None

def build_windows(source_dir, output_base, icon_file, architectures, version, name):
    pyinstaller = shutil.which("pyinstaller")
    if not pyinstaller:
        print("[!] pyinstaller not found. Ensure it's installed and in PATH.")
        return

    for arch in architectures:
        print(f"[*] Building for Windows ({arch})...")
        output_dir = output_base / f"windows-{arch}"
        output_dir.mkdir(parents=True, exist_ok=True)

        for pyfile in Path(source_dir).rglob("*.py"):
            command = [
                pyinstaller,
                "--onefile",
                "--distpath", str(output_dir),
                "--workpath", str(output_dir / "build"),
                "--specpath", str(output_dir / "spec")
            ]
            if icon_file:
                command += ["--icon", str(icon_file)]
                print(f"[*] Found icon argument: {icon_file}")
            command.append(str(pyfile))
            env = os.environ.copy()
            if arch == "x86":
                env["PYINSTALLER_PLATFORM"] = "win32"
            elif arch == "x64":
                env["PYINSTALLER_PLATFORM"] = "win_amd64"
                print(f"Running command: {command}")
            subprocess.run(command, env=env)

def build_linux(source_dir, output_base, icon_file, architectures, name, build_name, version=0):
    app_name = Path(source_dir)
    for arch in architectures:
        print(f"[*] Building for Linux ({arch})...")
        output_dir = output_base / f"{arch}"
        bin_dir = output_dir / "package" / "usr" / "local" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        build_root = os.path.join("Builds", "code", build_name, "executables")
        print(f"[*] Build root: {build_root}")
        build_path = os.path.join(build_root, arch)
        print(f"[*] Build path: {build_path}")
        
        if version == 0:
            version = 1.0
        
        shutil.copytree(source_dir, bin_dir, dirs_exist_ok=True)

        name = ''.join(c.lower() if c.isalpha() else c for c in name)
        fpm_cmd = [
            "fpm",
            "-s", "dir",
            "-t", "deb",
            "-n", name,
            "-v", str(version),
            "-a", arch,
            "package/=/"
        ]
        print(f"[*] Running command: {fpm_cmd}")
        subprocess.run(fpm_cmd, cwd=build_path, check=True)

def main():
    parser = argparse.ArgumentParser(description="Cross-platform and multi-arch build script")
    parser.add_argument("source", help="Path to the folder containing your code")
    parser.add_argument("--linux", action="store_true", help="Build for Linux")
    parser.add_argument("--windows", action="store_true", help="Build for Windows")
    parser.add_argument("--both", action="store_true", help="Build for both Linux and Windows")
    parser.add_argument("--arch", nargs='+', default=[], help="Architectures: x86, x64, arm64")
    parser.add_argument("--version", type=str, default=1.0, help="Version number for the package/executable")
    parser.add_argument("--name", type=str, default="Unnamed", help="Name for the package/executable")
    parser.add_argument("--clean", action="store_true", help="Clean/Remove build dir")
    parser.add_argument("--extrahelp", action="store_true", help="Some extra help with flags")
    args = parser.parse_args()
    
    if args.clean:
        BuildDir = os.path.join(os.getcwd(), "Builds")
        
        if os.path.exists(BuildDir):
            try:
                shutil.rmtree(BuildDir)
                exit(0)
            except error as e:
                print(f"[*] An error occurred when cleaning: {e}")
                exit(0)
        else:
            print(f"[*] Couldn't find: {BuildDir}")
            exit(0)
                
    if args.extrahelp:
        print("[*] Flags: source (Path to project dir), --linux (flag to build for linux), --windows (flag to build for windows), --both (flag to build for both) --arch (Architectures x86 x64 and arm64) --version(String) --name(String) --clean(flag), --help(flag)")
        exit(0)
    
    source_dir = Path(args.source).resolve()
    if not source_dir.exists():
        print(f"[!] Source directory {source_dir} does not exist.")
        return

    target_platforms = []
    if args.both or (not args.linux and not args.windows):
        target_platforms = ['linux', 'windows']
    else:
        if args.linux:
            target_platforms.append('linux')
        if args.windows:
            target_platforms.append('windows')

    build_name = source_dir.name
    output_base = Path("Builds") / "code" / build_name / "executables"
    if output_base.exists():
        shutil.rmtree(output_base)

    icon = find_icon_file(source_dir)

    linux_archs = [arch for arch in args.arch if arch in ['x86', 'x64', 'arm64']]
    windows_archs = [arch for arch in args.arch if arch in ['x86', 'x64']]

    if not linux_archs:
        linux_archs = ['x64']
    if not windows_archs:
        windows_archs = ['x64']
    
    name = args.name
    version = args.version
    
    if 'linux' in target_platforms:
        build_linux(source_dir, output_base, icon, linux_archs, name, build_name, version)
    if 'windows' in target_platforms:
        build_windows(source_dir, output_base, icon, windows_archs)

    print(f"[*] Build completed. Output at: {output_base}")

if __name__ == "__main__":
    main()
