# Freedom Vision v0.9 — design review (draft)

**Status: staged on a GitHub draft branch. Not merged or deployed.**

This update builds upon the existing Freedom Vision v0.8 read-only archive gateway and makes the newly researched cultural and educational collections easier to find.

## What's different

- Featured starting points for **Audiobooks & Stories**, **Science & Maths** and **Culture & Languages**.
- Eleven collection tiles remain available for classic cinema, cartoons, serials, music, books, world news, world cinema, language learning, science, audio lectures and audiobooks.
- Lightweight category buttons for quantum mechanics, particle physics, geometry, chemistry, biology, Japanese, French and audiobooks.
- Three clearly labeled source shelves linking directly to their official providers, with a collapsible full provider directory below.
- Responsive desktop/mobile design. No external image or font dependencies. No additional media requests until deliberately initiated.
- Distinction between source links, unverified embedding and approved direct video/audio playback. External providers may have their own adverts, rights terms or account restrictions.

## Featured direct-provider links

**Audio and stories:** [LibriVox](https://librivox.org/), [Lit2Go](https://etc.usf.edu/lit2go/), [Storybooks Canada](https://storybookscanada.ca/), [Global Storybooks](https://globalstorybooks.net/).

**Science:** [MIT OpenCourseWare (Quantum Physics I)](https://ocw.mit.edu/courses/8-04-quantum-physics-i-spring-2016/), [Yale Physics II](https://oyc.yale.edu/physics/phys-201), [CERN educational videos](https://educational-resources.web.cern.ch/videos-and-animations/), [PhET](https://phet.colorado.edu/), [OpenStax](https://openstax.org/higher-education).

**Culture, language and cinema:** [JFF Theater](https://en.jff.jpf.go.jp/), [Korean Film Archive](https://www.kmdb.or.kr/vod), [Japanese Animated Film Classics](https://animation.filmarchives.jp/en/index.html), [LanguageGuide](https://www.languageguide.org/), [NHK Easy Japanese](https://www.nhk.or.jp/lesson/en/).

The National Film Archive of Japan does not permit embedding its Animated Film Classics; the site is linked only. JFF Theater has a separate account/region model. No YouTube or Mixcloud player has been added.

## Operating principles remain unchanged

No advertising sold by Freedom Vision, no tracking, no autoplay, no media prefetch, 480p maximum and conservative bitrate checks on approved video, no bandwidth upsell, no donations routed through us. Verified links to the actual provider's official support page only. Use source-friendly metadata search with rate limiting and transparent failures.

## Review and deployment safeguards

The locally generated review prototype has been checked in headless Chromium at desktop (1440px) and mobile (390px) sizes: no JS errors, no horizontal overflow, all 11 collection tiles and source shelves visible; clicking audiobooks, quantum and world cinema displayed relevant source directories. This **does not** constitute live external API or rights validation.

Before merge, validate the actual GitHub branch in full-browser and GitHub Pages builds, with CORS, per-provider terms, file licences, international rights, exact URLs, accessibility and the existing mirror integrity suite. Update the developer source before treating the mirror as the primary editorial route.

Public homepage remains unchanged until that review is complete.


## Classic Free Movies and OldieFlix — external-only discovery (22 November 2026)
Two classic-film websites supplied by the project owner have been added as **external discovery links only** in the original-source directory and visible cinema cards:
- [Classic Free Movies](https://classicfreemovies.com/) — [film library](https://classicfreemovies.com/movie-library/) · [site search](https://classicfreemovies.com/search-movies/) · [Attack of the Giant Leeches](https://classicfreemovies.com/movies/attack-of-the-giant-leeches/).
- [OldieFlix](https://oldieflix.com/) — [original catalogue and search](https://oldieflix.com/) · [The Mummy's Tomb (1942)](https://oldieflix.com/titles/the-mummy-s-tomb-1942-harold-young.html).

**Verified:** Both root sites exist and promote free classic-film browsing; Classic Free Movies publicly claims an MP4 media server and offers embed codes. Its Terms request prior approval for portal links and restrict framed pages; its Privacy Policy names Google advertising. These policies may not reflect current player traffic but require review.
**Unverified:** No complete browser network trace for the linked film pages; therefore YouTube dependency, advertising at playback, low-resolution/rate limits and player permission cannot be ruled out or confirmed.
**Copyright:** Listing or linking does not establish public-domain status. In particular, *The Mummy's Tomb* is not marked as rights-cleared for reuse or embedding.

**Implementation:** Two provider directory entries (external), two visible website cards with direct film links and no iframes, third-party thumbnails, autoplay, scraping, API searches or automatic remote connections. External websites control their own privacy, advertising and playback once opened; Freedom Vision's own page remains non-advertising and lightweight.

**Before enabling an internal player:** Obtain confirmation of a permitted embed, inspect the browser requests for any YouTube and advertising, establish a suitable ≤480p existing stream, check rights for relevant territories, and agree source-friendly limits. Classic Free Movies' linking policy should be addressed before public launch.

**Visitor-choice rule:** The default action for each added classic-film website is **Browse the full catalogue** or **Search on the original website**, not play a preselected movie. The two user-submitted titles appear in collapsed, optional example sections. No browser makes a media request for these websites from Freedom Vision; visitors choose an item after opening a provider website. Site-level restrictions and rights reviews remain open.
