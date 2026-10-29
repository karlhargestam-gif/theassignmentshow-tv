# Video structured-data investigation — October 29, 2026

**Draft only. Do not merge, deploy, change DNS, or request Search Console validation yet.** Existing publication approvals and freezes remain in force. All 13 original video publication dates are verified and the proposed metadata passes Google’s code-mode test. Production remains unchanged until the approved release.

## Verified production cause

The October 29 Search Console notification reports the critical missing `uploadDate` field. After secure sign-in, the authenticated `sc-domain:theassignmentshow.tv` Videos report confirmed **5 invalid items, 0 valid items**, and validation **Not Started**. The specific issue lists exactly these five examples, all last crawled October 28, 2026:

| Affected URL | Item name |
| --- | --- |
| https://www.theassignmentshow.tv/episode-10/ | Are We There Yet? |
| https://www.theassignmentshow.tv/episode-9/ | The Road to Dida Guda |
| https://www.theassignmentshow.tv/episode-1/ | Mission One Eleven takes Ethiopia. |
| https://www.theassignmentshow.tv/episode-5/ | What's for Dinner? |
| https://www.theassignmentshow.tv/episode-6/ | We've Come in Peace |

The report displays “First detected: 10/28/26” and “Last update: 10/27/26”; both are recorded as displayed, without inferring a chronological explanation. The examples are not a complete independent crawl of this site's 13 episode pages. **Validate fix was not started.**

Repository `main` was `d56d0956e1d77e8369e665e0ee41bedf21a0af51`. PR #6 merged October 28 at 02:42:24 UTC, followed by #7 at 02:47:13 UTC. No open PR or issue existed in this repository at inspection. No AGENTS.md or local freeze document was present; a ruleset read returned none, while branch-protection inspection was denied by the GitHub integration. No approval is inferred from those absences.

Direct HTTP checks around 17:21 UTC October 29 found the homepage, all 13 canonical episode pages, sitemap and robots file returning HTTP 200 and matching `main` byte-for-byte. Every episode page contained one `VideoObject` without `uploadDate`; the homepage contained no `VideoObject`. This establishes 13 live instances of the defect, independently of which subset Google has crawled. The old PR description saying production episode pages returned 404 is now stale.

The generator explicitly omitted unknown dates. The original site check validated JSON syntax, name, description, and thumbnail, but did not require `uploadDate`, so it passed the affected site. GitHub's Vercel status reports deployment completion for `d56d095`; the Vercel connector could not read the project/deployments (404/403), and no local authenticated Vercel CLI was available. Production content identity is verified by HTTP bytes, not a claimed Vercel deployment inspection.

## Authoritative video evidence

For episodes 1, 2, 3, 5 and 9, the original public YouTube watch-page response identifies the expected exact video ID, episode number, and Mission One Eleven channel `UCpp2TgO-EiiiPnXgAFa4J5g`. Its `playerMicroformatRenderer.publishDate`, `uploadDate`, and HTML `meta[itemprop=datePublished]` agree, including seconds and timezone. These are publication timestamps of the linked YouTube uploads, **not a claim about the original television broadcast date**. Their descriptions match the existing episode synopses.

For episodes 4, 6, 7, 8, 10, 11, 12 and 13, the original public YouTube pages were inspected in the browser. Each exact canonical video URL and episode title matched the site, the channel link identified Mission One Eleven (`@missiononeeleven2447`), and the DOM `meta[itemprop=datePublished]` and `meta[itemprop=uploadDate]` agreed to the second and timezone. Browser extraction evidence is retained separately; no player-response fields are claimed for these DOM observations. All 13 dates are now established. Episode 10 was uploaded before several lower-numbered episodes; dates were not extrapolated from episode ordering.

The initial direct HTTP route stopped after a YouTube bot-confirmation response. These later browser observations loaded the normal public watch pages without a challenge. The manifest distinguishes original response hashes from hashes of canonical JSON DOM evidence records.

| Episode URL | Original video/source | Verified uploadDate |
| --- | --- | --- |
| [1](https://www.theassignmentshow.tv/episode-1/) | [Kv2HmDKY9Jk](https://www.youtube.com/watch?v=Kv2HmDKY9Jk) | 2021-07-02T09:24:37-07:00 |
| [2](https://www.theassignmentshow.tv/episode-2/) | [MqkBidv5LRU](https://www.youtube.com/watch?v=MqkBidv5LRU) | 2021-07-02T09:42:26-07:00 |
| [3](https://www.theassignmentshow.tv/episode-3/) | [pM91XLRN2CY](https://www.youtube.com/watch?v=pM91XLRN2CY) | 2021-07-02T10:02:39-07:00 |
| [4](https://www.theassignmentshow.tv/episode-4/) | [_curg73S194](https://www.youtube.com/watch?v=_curg73S194) | 2021-07-02T13:10:30-07:00 |
| [5](https://www.theassignmentshow.tv/episode-5/) | [VRdMOGj4HDI](https://www.youtube.com/watch?v=VRdMOGj4HDI) | 2021-07-07T12:24:03-07:00 |
| [6](https://www.theassignmentshow.tv/episode-6/) | [5a5uiTjnZLA](https://www.youtube.com/watch?v=5a5uiTjnZLA) | 2021-07-07T12:22:32-07:00 |
| [7](https://www.theassignmentshow.tv/episode-7/) | [2ZElpIsYFDE](https://www.youtube.com/watch?v=2ZElpIsYFDE) | 2021-07-07T12:28:22-07:00 |
| [8](https://www.theassignmentshow.tv/episode-8/) | [P2lYvwMZeDM](https://www.youtube.com/watch?v=P2lYvwMZeDM) | 2021-07-07T12:25:22-07:00 |
| [9](https://www.theassignmentshow.tv/episode-9/) | [kPEKNLH4UhU](https://www.youtube.com/watch?v=kPEKNLH4UhU) | 2021-07-07T12:27:19-07:00 |
| [10](https://www.theassignmentshow.tv/episode-10/) | [0Ae8sbsl-ws](https://www.youtube.com/watch?v=0Ae8sbsl-ws) | 2021-07-06T18:54:57-07:00 |
| [11](https://www.theassignmentshow.tv/episode-11/) | [Qqhjk7dfmLM](https://www.youtube.com/watch?v=Qqhjk7dfmLM) | 2021-07-07T08:30:41-07:00 |
| [12](https://www.theassignmentshow.tv/episode-12/) | [zoDEP70enGM](https://www.youtube.com/watch?v=zoDEP70enGM) | 2021-07-07T08:33:21-07:00 |
| [13](https://www.theassignmentshow.tv/episode-13/) | [3Jg2wFGJ-y4](https://www.youtube.com/watch?v=3Jg2wFGJ-y4) | 2021-07-07T08:34:43-07:00 |

Source evidence, retrieval timestamps, explicitly scoped hashes and verification methods are in [`../data/video-metadata.json`](../data/video-metadata.json). The eight browser DOM records are also retained in [youtube-dom-evidence-2026-10-29.json](youtube-dom-evidence-2026-10-29.json). Never extrapolate dates from another episode. The publisher webpage's 2025 `datePublished`, its image `/2020/11/` paths, the new site dates, and today's date are not video upload evidence.

## Proposed implementation

- Bind metadata to each exact video ID and episode number. Fail on mismatched provenance, invalid dates, future dates, missing source corroboration or catalog drift. Build without network access and without fallback dates.
- Emit the independently verified `uploadDate` for all 13 exact videos. Unknown-date handling remains available and never emits a fallback date.
- Use the unique episode images linked to each exact video on [the publisher's Assignment page](https://missiononeeleven.com/the-assignment/) for `VideoObject.thumbnailUrl`, replacing the shared stock landscape thumbnail. All 13 source images returned HTTP 200, image/png, 1920×1080. These metadata images depend on the existing publisher's host.
- Preserve all visible HTML, episode descriptions, outgoing links, navigation, canonical URLs, branding, existing image assets, Open Graph images, homepage, CSS, robots and sitemap byte-for-byte. Only episode JSON-LD changes. No TV air dates added.
- Require complete verified date coverage in CI. Diagnostic site checks can show unresolved dates as warnings; the release/CI command fails on each unresolved date. All 13 records now satisfy the strict release check.
- Disable automatic Vercel deployment for the exact repair branch `codex/verified-video-upload-dates` in its `vercel.json`. Other branches are unchanged. Do not remove this guard or merge without publication authorization.

## Validation

- `python3 .github/scripts/build_episodes.py --check`: PASS, 16 generated files reproduce exactly.
- `python3 -m unittest discover -s .github/scripts -p 'test_*.py'`: PASS, 7 tests for provenance, source identity, invalid/future dates, unknown-date omission, release reporting and reproducibility.
- `python3 .github/scripts/site_check.py --host www.theassignmentshow.tv --max-page-kb 1024`: PASS, 14 pages, 0 errors, **0 warnings**. This includes JSON-LD syntax, titles, canonical links, internal links/assets, robots and all 14 sitemap URLs.
- Same command with `--require-video-dates`: **PASS, 0 errors and 0 warnings**, covering all 13 episode dates. The workflow uses this stricter command.
- Google Rich Results Test, **CODE mode**: **13 valid Video items** for the exact corrected `VideoObject` payloads for episodes 1–13, submitted together in a test HTML wrapper. [Google result](https://search.google.com/test/rich-results/result?id=KyxoQ1VWm0SMu3XtUoB6_w). This is schema validation of proposed code, not validation of deployed URLs or indexing.
- [Validation screenshot](google-video-validation-2026-10-29.jpg).
- [Production response audit](production-audit-2026-10-29.json).
- All 13 page bodies and all head markup outside JSON-LD are identical to the inspected production baseline. No visual redesign or new player; no claim of a fresh Lighthouse/browser-accessibility audit.

## Remaining work and approval sequence

1. Separately review video-search eligibility: current episode pages only link to YouTube and contain no player. A valid VideoObject alone does not make these dedicated watch pages. Approve a suitable on-page video experience if video indexing on this domain is intended; this draft preserves the existing design.
2. Complete PR review and the strict GitHub CI check. Resolve all publication approvals/freezes. Update sitemap lastmod only for actual page changes at the approved release; it is not a video upload date.
3. Only after explicit release authorization, merge and deploy through the existing owner/team workflow. Re-fetch the live canonical URLs and verify their actual served markup and thumbnail reachability, then run Google's URL-mode Rich Results Test and Search Console URL Inspection.
4. In the specific Search Console issue, start **Validate fix** only after every affected live instance is corrected. Request recrawl where appropriate and monitor Google's validation results. A local/code test or PR does not clear the warning; Google must recrawl and reprocess. Correct markup does not guarantee a search feature.

## Reference documentation

- [Google VideoObject requirements](https://developers.google.com/search/docs/appearance/structured-data/video): uploadDate is the first publication timestamp, in ISO 8601.
- [Google video SEO requirements](https://developers.google.com/search/docs/appearance/video): dedicated watch pages and discoverable playable video.
- [Google rich-result report validation](https://support.google.com/webmasters/answer/7552505): fix all instances and validate after the live change.
- [Vercel per-branch deployment guard](https://vercel.com/docs/project-configuration/git-configuration).
