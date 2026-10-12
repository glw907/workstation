package tellscan

// hardSlopPatterns flag on any occurrence. An entry earns its place
// through corpus or production-filter evidence, or as a register rule
// the workstation standard bans outright whatever the corpus says.
// Publicized words decay; "delves" fell from an excess ratio of x39.5
// to x8.0 within a year. The list is versioned 2026-09 and due for
// yearly re-derivation from evals/research/data/excess_words.csv, whose
// tiers are documented in
// evals/research/2026-09-01-ai-tell-evidence-base.md.
var hardSlopPatterns = res(
	// Tier A, r >= 4.5 (Kobak et al. 2025, 15.1M abstracts).
	`(?i)\bdelv(?:e|es|ed|ing)\b`,
	`(?i)\bunderscor(?:e|es|ed|ing)\b`,
	// The bare noun is not matched: it is the cairn example site's name.
	`(?i)\bshowcas(?:es|ed|ing)\b`,
	`(?i)\bmeticulous(?:ly)?\b`,
	`(?i)\bintricate(?:ly)?\b`,
	`(?i)\bintricacies\b`,
	`(?i)\bsurpassing\b`,
	`(?i)\bcommendable\b`,
	`(?i)\bexcels\b`,
	`(?i)\bgarnered\b`,
	// Phrase form only: a bare "realm" is a technical term in auth
	// contexts (Kerberos, HTTP, ARM CCA).
	`(?i)\bin the realms? of\b`,
	`(?i)\brenowned\b`,
	`(?i)\bgrappl(?:es|ing)\b`,
	`(?i)\bgroundbreaking\b`,
	// Strong catalogue phrases with corpus or production-filter support
	// (Wikipedia AbuseFilter 1325, WP:AILEGACY, WP:AIPUFFERY; boasting
	// r=16.2, tapestry 5.5, testament-to per AbuseFilter).
	`(?i)\btapestry\b`,
	`(?i)\btestament to\b`,
	`(?i)\bboast(?:s|ing)?\b`,
	`(?i)\bstands as\b`,
	`(?i)\bnestled\b`,
	`(?i)\bplays a (?:vital|crucial|pivotal|key) role\b`,
	`(?i)\bindelible mark\b`,
	`(?i)\bseamless(?:ly)?\b`,
	`(?i)\brevolutioniz\w*\b`,
	// Register rules: banned by the workstation standard as marketing
	// filler even though the corpus gives the tokens no excess ratio.
	`(?i)\bgame[- ]?changer\b`,
	`(?i)\bin today['’]s\b`,
	`(?i)\bfast-paced\b`,
	`(?i)\bever-evolving\b`,
	`(?i)\bcutting[- ]edge\b`,
	`(?i)\bstate-of-the-art\b`,
	`(?i)\beffortless(?:ly)?\b`,
	`(?i)\blook no further\b`,
	`(?i)\bunlock(?:s|ed|ing)? the\b`,
	`(?i)\belevat(?:e|es|ing) your\b`,
	`(?i)\bsupercharge\w*\b`,
	`(?i)\bin the world of\b`,
	`(?i)\bat the end of the day\b`,
	`(?i)\ba wealth of\b`,
	`(?i)\bwhether you['’]re a\b`,
)

// softSlopPatterns count toward density and never flag on their own.
// Each is a judgment word that can be exact in context, so a lone
// occurrence proves nothing.
var softSlopPatterns = res(
	// Tier B/C, r roughly 2.0-4.7. Real excess, common in human prose.
	`(?i)\bemphasizing\b`,
	`(?i)\badvancements\b`,
	`(?i)\bheightened\b`,
	`(?i)\bfoster(?:s|ed|ing)?\b`,
	`(?i)\bleverag(?:e|es|ed|ing)\b`,
	`(?i)\bpivotal\b`,
	`(?i)\btransformative\b`,
	`(?i)\bmultifaceted\b`,
	`(?i)\bnuanced\b`,
	`(?i)\bnotably\b`,
	`(?i)\bstreamlin(?:e|es|ed|ing)\b`,
	`(?i)\bbolster\w*\b`,
	`(?i)\bburgeoning\b`,
	`(?i)\bnoteworthy\b`,
	`(?i)\bpoised\b`,
	`(?i)\bempower(?:s|ed|ing)?\b`,
	`(?i)\binterplay\b`,
	`(?i)\benduring\b`,
	`(?i)\butilizing\b`,
	`(?i)\bcrucial\b`,
	`(?i)\bcomprehensive\b`,
	`(?i)\bakin to\b`,
	`(?i)\bpaving the way\b`,
	// Weak or catalogue-only, r <= ~1.5. Counted because the standard
	// watches them, with no claim of corpus evidence.
	`(?i)\brobust\b`,
	`(?i)\bvital\b`,
	`(?i)\bholistic\b`,
	`(?i)\blandscape\b`,
	`(?i)\bjourney\b`,
	`(?i)\bvibrant\b`,
	`(?i)\bdeep dive\b`,
	`(?i)\bdive into\b`,
	`(?i)\bwhen it comes to\b`,
	`(?i)\bkeep in mind\b`,
)
