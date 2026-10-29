# Video structured-data investigation — October 29, 2026

**Draft only. Do not merge, deploy, change DNS, or request Search Console validation yet.** Existing publication approvals and freezes remain in force. This is a partial, evidence-backed repair: 5 video dates verified, 8 still unresolved.

## Verified production cause

The October 29 Search Console notification reports the critical missing `uploadDate` field. The email does not enumerate URLs. The authenticated issue report could not be read: the available browser session is signed out. Therefore Google's exact affected-URL count, sample URLs, last crawl dates, and validation status are unknown.

Repository `main` was `d56d0956e1d77e8369e665e0ee41bedf21a0af51`. PR #6 merged October 28 at 02:42:24 UTC, followed by #7 at 02:47:13 UTC. No open PR or issue existed in this repository at inspection. No AGENTS.md or local freeze document was present; a ruleset read returned none, while branch-protection inspection was denied by the GitHub integration. No approval is inferred from those absences.

Direct HTTP checks around 17:21 UTC October 29 found the homepage, all 13 canonical episode pages, sitemap and robots file returning HTTP 200 and matching `main` byte-for-byte. Every episode page contained one `VideoObject` without `uploadDate`; the homepage contained no `VideoObject`. This establishes 13 live instances of the defect, independently of which subset Google has crawled. The old PR description saying production episode pages returned 404 is now stale.

The generator explicitly omitted unknown dates. The original site check validated JSON syntax, name, description, and thumbnail, but did not require `uploadDate`, so it passed the affected site. GitHub's Vercel status reports deployment completion for `d56d095`; the Vercel connector could not read the project/deployments (404/403), and no local authenticated Vercel CLI was available. Production content identity is verified by HTTP bytes, not a claimed Vercel deployment inspection.

## Authoritative video evidence

For episodes 1, 2, 3, 5 and 9, the original public YouTube watch-page response identifies the expected exact video ID, episode number, and Mission One Eleven channel `UCpp2TgO-EiiiPnXgAFa4J5g`. Its `playerMicroformatRenderer.publishDate`, `uploadDate`, and HTML `meta[itemprop=datePublished]` agree, including seconds and timezone. These are publication timestamps of the linked YouTube uploads, **not a claim about the original television broadcast date**. Their descriptions match the existing episode synopses.

The remaining requests did not provide usable publication metadata. An inspected response for episode 4 explicitly returned `LOGIN_REQUIRED` / a bot-confirmation sign-in request. Further direct YouTube requests were stopped. Public search and the publisher's episode page supplied no authoritative dates for the eight unresolved videos. No YouTube account was connected through the available Zapier integration.

| Episode URL | Original video/source | Verified uploadDate |
| --- | --- | --- |
| [1](https://www.theassignmentshow.tv/episode-1/) | [Kv2HmDKY9Jk](https://www.youtube.com/watch?v=Kv2HmDKY9Jk) | 2021-07-02T09:24:37-07:00 |
| [2](https://www.theassignmentshow.tv/episode-2/) | [MqkBidv5LRU](https://www.youtube.com/watch?v=MqkBidv5LRU) | 2021-07-02T09:42:26-07:00 |
| [3](https://www.theassignmentshow.tv/episode-3/) | [pM91XLRN2CY](https://www.youtube.com/watch?v=pM91XLRN2CY) | 2021-07-02T10:02:39-07:00 |
| [4](https://www.theassignmentshow.tv/episode-4/) | [_curg73S194](https://www.youtube.com/watch?v=_curg73S194) | Unresolved — no authoritative date obtained |
| [5](https://www.theassignmentshow.tv/episode-5/) | [VRdMOGj4HDI](https://www.youtube.com/watch?v=VRdMOGj4HDI) | 2021-07-07T12:24:03-07:00 |
| [6](https://www.theassignmentshow.tv/episode-6/) | [5a5uiTjnZLA](https://www.youtube.com/watch?v=5a5uiTjnZLA) | Unresolved — no authoritative date obtained |
| [7](https://www.theassignmentshow.tv/episode-7/) | [2ZElpIsYFDE](https://www.youtube.com/watch?v=2ZElpIsYFDE) | Unresolved — no authoritative date obtained |
| [8](https://www.theassignmentshow.tv/episode-8/) | [P2lYvwMZeDM](https://www.youtube.com/watch?v=P2lYvwMZeDM) | Unresolved — no authoritative date obtained |
| [9](https://www.theassignmentshow.tv/episode-9/) | [kPEKNLH4UhU](https://www.youtube.com/watch?v=kPEKNLH4UhU) | 2021-07-07T12:27:19-07:00 |
| [10](https://www.theassignmentshow.tv/episode-10/) | [0Ae8sbsl-ws](https://www.youtube.com/watch?v=0Ae8sbsl-ws) | Unresolved — no authoritative date obtained |
| [11](https://www.theassignmentshow.tv/episode-11/) | [Qqhjk7dfmLM](https://www.youtube.com/watch?v=Qqhjk7dfmLM) | Unresolved — no authoritative date obtained |
| [12](https://www.theassignmentshow.tv/episode-12/) | [zoDEP70enGM](https://www.youtube.com/watch?v=zoDEP70enGM) | Unresolved — no authoritative date obtained |
| [13](https://www.theassignmentshow.tv/episode-13/) | [3Jg2wFGJ-y4](https://www.youtube.com/watch?v=3Jg2wFGJ-y4) | Unresolved — no authoritative date obtained |

Source evidence, retrieval timestamps, response hashes and unresolved reasons are in [`../data/video-metadata.json`](../data/video-metadata.json). Never extrapolate the other episode dates from these five. The publisher webpage's 2025 `datePublished`, its image `/2020/11/` paths, the new site dates, and today's date are not video upload evidence.

## Proposed implementation

- Bind metadata to each exact video ID and episode number. Fail on mismatched provenance, invalid dates, future dates, missing source corroboration or catalog drift. Build without network access and without fallback dates.
- Emit `uploadDate` only for the five verified records. Retain the eight unresolved `VideoObject` records without invented dates, making the remaining issue explicit.
- Use the unique episode images linked to each exact video on [the publisher's Assignment page](https://missiononeeleven.com/the-assignment/) for `VideoObject.thumbnailUrl`, replacing the shared stock landscape thumbnail. All 13 source images returned HTTP 200, image/png, 1920×1080. These metadata images depend on the existing publisher's host.
- Preserve all visible HTML, episode descriptions, outgoing links, navigation, canonical URLs, branding, existing image assets, Open Graph images, homepage, CSS, robots and sitemap byte-for-byte. Only episode JSON-LD changes. No TV air dates added.
- Require complete verified date coverage in CI. Diagnostic site checks can show unresolved dates as warnings; the release/CI command fails on each unresolved date. A failing draft is intentional, not a completed fix.
- Disable automatic Vercel deployment for the exact repair branch `codex/verified-video-upload-dates` in its `vercel.json`. Other branches are unchanged. Do not remove this guard or merge without publication authorization.

## Validation

- `python3 .github/scripts/build_episodes.py --check`: PASS, 16 generated files reproduce exactly.
- `python3 -m unittest discover -s .github/scripts -p 'test_*.py'`: PASS, 7 tests for provenance, source identity, invalid/future dates, unknown-date omission, release reporting and reproducibility.
- `python3 .github/scripts/site_check.py --host www.theassignmentshow.tv --max-page-kb 1024`: PASS, 14 pages, 0 errors, **8 explicit unresolved-date warnings**. This includes JSON-LD syntax, titles, canonical links, internal links/assets, robots and all 14 sitemap URLs.
- Same command with `--require-video-dates`: **FAIL, exactly 8 missing uploadDate errors**, for episodes 4, 6, 7, 8, 10, 11, 12 and 13. The workflow uses this stricter command.
- Google Rich Results Test, **CODE mode**: **5 valid Video items** for the exact corrected `VideoObject` payloads for episodes 1, 2, 3, 5 and 9, submitted together in a test HTML wrapper. [Google result](https://search.google.com/test/rich-results/result?id=CYiFbm4yPX-MInfRpBG9Mg). This is schema validation of proposed code, not validation of deployed URLs or indexing.
- [Validation screenshot](google-video-validation-2026-10-29.jpg).
- [Production response audit](production-audit-2026-10-29.json).
- All 13 page bodies and all head markup outside JSON-LD are identical to the inspected production baseline. No visual redesign or new player; no claim of a fresh Lighthouse/browser-accessibility audit.

## Remaining work and approval sequence

1. Obtain authoritative original publishing records for the eight unresolved video IDs, ideally authenticated YouTube metadata/Studio records; preserve the supplied precision and timezone. Add evidence to the manifest and regenerate. If no trustworthy date can be established, retain unresolved status and decide the correct markup treatment explicitly rather than fabricating a value.
2. Sign in to Search Console for the existing `theassignmentshow.tv` property and read the exact missing-uploadDate issue samples, count and crawl dates. Compare these with the complete live URL audit above.
3. Separately review video-search eligibility: current episode pages only link to YouTube and contain no player. A valid VideoObject alone does not make these dedicated watch pages. Approve a suitable on-page video experience if video indexing on this domain is intended; this draft preserves the existing design.
4. Rerun the strict CI check, Google code tests and review. Resolve all publication approvals/freezes. Update sitemap lastmod only for actual page changes at the approved release; it is not a video upload date.
5. Only after explicit release authorization, merge and deploy through the existing owner/team workflow. Re-fetch the live canonical URLs and verify their actual served markup and thumbnail reachability, then run Google's URL-mode Rich Results Test and Search Console URL Inspection.
6. In the specific Search Console issue, start **Validate fix** only after every affected live instance is corrected. Request recrawl where appropriate and monitor Google's validation results. A local/code test or PR does not clear the warning; Google must recrawl and reprocess. Correct markup does not guarantee a search feature.

## Reference documentation

- [Google VideoObject requirements](https://developers.google.com/search/docs/appearance/structured-data/video): uploadDate is the first publication timestamp, in ISO 8601.
- [Google video SEO requirements](https://developers.google.com/search/docs/appearance/video): dedicated watch pages and discoverable playable video.
- [Google rich-result report validation](https://support.google.com/webmasters/answer/7552505): fix all instances and validate after the live change.
- [Vercel per-branch deployment guard](https://vercel.com/docs/project-configuration/git-configuration).
