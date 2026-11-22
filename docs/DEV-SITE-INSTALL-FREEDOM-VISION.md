# The Green Tank DEV Site — Freedom Vision integration handoff

**Status: prepared; NOT published to the `chatgpt.site` development website.**

Development site: https://the-green-tank.alexiscoderpenguy.chatgpt.site

This file is intended for the editor of the above ChatGPT-hosted development project. The GitHub repository is the separate **verified mirror**, not the editable source of the development site. Do not change that mirror to pretend the development site has been updated.

## Goal

Create an independent, accessible **Freedom Vision** page at `/freedom-vision` and place a prominent **Freedom Vision** navigation tab/button on the Green Tank homepage.

The page must preserve the existing site sections, publications, machine-readable Sub Space data, research, all existing routes, identity and colour scheme. It must be independently reversible.

## Reviewed source on the draft GitHub branch

- [Freedom Vision page HTML](https://github.com/Thegreentank2/Thegreentank-deployment-2/blob/feature/freedom-vision-v0.6/freedom_vision_source/index.html)
- [JavaScript behaviour and provider directory](https://github.com/Thegreentank2/Thegreentank-deployment-2/blob/feature/freedom-vision-v0.6/freedom_vision_source/app.js)
- [Responsive CSS](https://github.com/Thegreentank2/Thegreentank-deployment-2/blob/feature/freedom-vision-v0.6/freedom_vision_source/styles.css)
- [Full design and source review](https://github.com/Thegreentank2/Thegreentank-deployment-2/blob/feature/freedom-vision-v0.6/docs/freedom-vision-v0.9-review.md)

Use an isolated route/component so the new CSS cannot overwrite existing Green Tank styling. If the editor framework is not static HTML, **adapt** rather than pasting an entire second HTML document into the home page. Reuse approved site routing and deploy processes.

## Minimum testable DEV functionality

1. Green Tank homepage contains a visible and accessible Freedom Vision link.
2. `/freedom-vision` loads independently with working mobile/desktop navigation.
3. Contents: discover, watch, listen, read, world news, world cinema, culture and languages, science and mathematics, audio lessons, audiobooks and stories.
4. Eleven collection cards and a featured section for stories, science and culture.
5. Source directory includes Internet Archive, Wikimedia Commons, Project Gutenberg, LibriVox, other institutional sources, Classic Free Movies and OldieFlix.
6. **Classic Free Movies** and **OldieFlix** are ordinary links to their searchable home/catalogue pages, with the two sample film links kept optional. Do not embed either player or transfer their films.
7. Internet Archive, Wikimedia Commons, Gutendex and LibriVox metadata search is user-initiated only, using existing request pacing, timeouts, cache and 429/503 cool-down logic. Test API CORS and actual search before enabling any connection.
8. Provider-hosted playable video: only where permission, licence, exact pre-existing file dimensions/bitrate and same-origin/cross-origin access are verified. Video ≤480p with no high-resolution downloads or automatic video transcoding. Do not load video automatically. If uncertain, display source link only.
9. No Freedom Vision advertising, affiliate links, analytics, sign-in wall, paid bandwidth, YouTube or Mixcloud. External websites may have separate terms; label them accurately. No user data collected for tracking.
10. Donation links only to **verified official provider destinations**. Do not process donations on behalf of providers.

## Protection and verification

- Take a backup/snapshot of the development site's current version first.
- Change only the new route and the minimum homepage navigation area.
- Validate that existing content and all site routes still work.
- Do not merge or publish the GitHub mirror PR in place of modifying the development site.
- Confirm live `/freedom-vision` route, source browsing, mobile behaviour, accessible buttons and that **no media is fetched on initial page load**.
- If launch tests fail, roll back just the Freedom Vision addition; do not delete or alter existing Green Tank content.

## Recommended editing request

> Add the Freedom Vision v0.9 public archive gateway to this Green Tank development project at /freedom-vision, using the reviewed HTML, JS and CSS on the specified GitHub draft branch as design and implementation references. Include a front-page tab, preserve all existing site material, and keep the new route isolated. The initial public test should link to third-party movie catalogues rather than embedding their players. Retain all low-bandwidth, no-advertising, no-autoplay and server-protection rules. Publish to the **development site**, not the GitHub mirror, and return the working URL only after verifying it.

**The draft repository code is prepared for integration but is not a substitute for access to the actual development-site editor.**
