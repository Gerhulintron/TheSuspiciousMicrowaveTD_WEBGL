# Suspicious Microwave WebGL deployment

This repository contains the generated WebGL player. Unity source and the
Seeker build remain in the separate source repository.

## Git LFS

The large `Build/*.data*` and `Build/*.wasm*` files use Git LFS. Install Git LFS
on any machine working with this repository, then run:

```powershell
git lfs install --local
git lfs pull
```

The original `Build/WebGL.*` files are preserved locally but ignored and removed
from Git tracking. The current `index.html` references the
`TheSuspiciousMicrowaveTD_WEBGL.*` build instead. No build files were deleted.

Git LFS is storage, not a game CDN. New binary versions use additional LFS
storage, and CI downloads count against the owner's LFS bandwidth allowance.

## GitHub Pages

Use **GitHub Actions** as the Pages source. Direct branch publishing cannot
serve Git LFS pointer files. The workflow checks out the real LFS content,
verifies it, and publishes a separate static-site artifact. The packaging
script rejects LFS pointers and includes only files referenced by `index.html`
plus `StreamingAssets`; it excludes obsolete builds and repository internals.

After pushing `main`:

1. Open the repository's **Settings > Pages**.
2. Set **Source** to **GitHub Actions**.
3. Set **Custom domain** to `suspiciousmicrowavetd.thesimulacrum.xyz`.
4. In DNS, add this record:

   | Type | Name | Target |
   |---|---|---|
   | CNAME | suspiciousmicrowavetd | gerhulintron.github.io |

5. Run/re-run **Deploy WebGL to GitHub Pages** in the Actions tab.
6. Enable **Enforce HTTPS** when the certificate becomes available.

GitHub Actions deployments use the domain saved in Pages settings. A repository
`CNAME` file does not configure that setting and is not required for this workflow.

## Build and test

The current player is a development build, not a fully validated public release.
Live wallet login and SOL/USDC/SKR/ORE purchase recovery still require testing.
For a release, enable Unity compression with **Decompression Fallback** so the
loader uses `.unityweb` files. Pages does not provide configurable Unity
`Content-Encoding` headers. Keep the existing Low managed stripping and caught
exception support until wallet and UGS behavior is validated.

Verify the site without writing a staging copy:

```powershell
python scripts/prepare_pages.py --source .
```

The custom-domain site will be `https://suspiciousmicrowavetd.thesimulacrum.xyz/`.
DNS, repository Pages settings, and public deployment must be configured
separately from preparing the local repository.

References:
- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://github.com/actions/checkout#usage
- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- https://docs.github.com/en/billing/concepts/product-billing/git-lfs
- https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
