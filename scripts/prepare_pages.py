"""Package a built Unity player for Pages; never publish Git LFS pointers."""
import argparse
from pathlib import Path
import re
import shutil


LFS_POINTER = b'version https://git-lfs.github.com/spec/v1'
MAX_SITE_BYTES = 1_000_000_000


def collect_files(source):
    index = source / 'index.html'
    html = index.read_text(encoding='utf-8')
    build_paths = sorted(set(re.findall(r'''['"](Build/[^'"<>]+)['"]''', html)))
    if not build_paths or not any('.wasm' in name for name in build_paths):
        raise ValueError('index.html does not reference a complete Unity WebGL build.')
    files = [index]
    for name in build_paths:
        path = source / name
        if path.is_symlink() or not path.resolve().is_relative_to(source):
            raise ValueError(f'Build reference escapes the site directory: {name}')
        if path.suffix in ('.gz', '.br'):
            raise ValueError('Pages cannot set Unity Content-Encoding headers. '
                             'Use an uncompressed build or Unity decompression fallback (.unityweb).')
        files.append(path)
    streaming = source / 'StreamingAssets'
    if not streaming.is_dir():
        raise ValueError('StreamingAssets is missing.')
    for path in sorted(streaming.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Symbolic links are not supported: {path}')
        if path.is_file():
            files.append(path)
    total = 0
    for path in files:
        if not path.is_file():
            raise ValueError(f'Required game file is missing: {path}')
        with path.open('rb') as stream:
            if stream.read(len(LFS_POINTER)).startswith(LFS_POINTER):
                raise ValueError(f'Git LFS pointer found instead of game data: {path}. '
                                 'Download the LFS objects before deploying.')
        total += path.stat().st_size
    if total >= MAX_SITE_BYTES:
        raise ValueError('The site exceeds the supported GitHub Pages size limit. '
                         'Build a smaller release before deploying.')
    return files, total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    files, total = collect_files(source)
    if args.output is not None:
        output = args.output.resolve()
        if output == source or source.is_relative_to(output):
            raise ValueError('The output must be a separate staging directory.')
        # No cleanup: fail instead of overwriting an existing staging directory.
        output.mkdir(parents=True, exist_ok=False)
        for path in files:
            destination = output / path.relative_to(source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
        (output / '.nojekyll').write_text('', encoding='utf-8')
    print(f'Verified {len(files)} game files, {total / 1024 / 1024:.1f} MiB. '
          'No LFS pointers or obsolete build variants included.')


if __name__ == '__main__':
    main()
