# Dynamic Contracts experiment — code & instructions review

**Scope.** Full read-through of the four active oTree apps in the live session configs
(`SBC_consent_form` → `SBC_S1_t1_` for Part 1; `SBC_consent_t2` → `SBC_S1_t2_` for Part 2),
plus `settings.py` and the shared templates they include. Checked for English/clarity errors,
inconsistencies (across time points, across treatments, and vs. the code), and programming errors,
with particular attention to the Part-1 → Part-2 data handoff.

**Treatment map** (`participant.treatment`): `0` = static, buy at t=1 · `1` = static, buy at t=2 ·
`2` = dynamic, option · `3` = dynamic, refund.

---

## Priority summary

| # | Severity | Type | Issue | File |
|---|----------|------|-------|------|
| 1.1 | 🟠 Must-fix | Programming | A failed t1→t2 lookup crashes Part 2 (None `treatment`/`x_draw`), no fallback | `SBC_consent_t2` |
| 1.2 | 🟠 Must-fix | Programming + Inconsistency | Quiz locks out after **2** fails (text says 3); a correct 3rd attempt is still rejected | both consent apps |
| 1.3 | 🟠 Must-fix | Inconsistency | t2 quiz "Reveal Instructions" embeds the **Part-1** instructions file | `SBC_consent_t2/Quiz.html` |
| 3.1 | 🟡 Medium | Inconsistency | `instr.html` reveal panel describes the treatment-2 overwrite wrongly | both consent apps |
| 4 | 🟢 Low | Programming | Latent `@staticmethod` duplication; probability off-by-one; T1 example input loss | various |
| 5 | ❓ Confirm | — | Is informed consent captured anywhere? Is the "no payment if you don't return" rule real? | — |

---

## 1. Must-fix before data collection

### 1.1 A failed t1→t2 handoff crashes Part 2
Part 1 and Part 2 are **separate oTree sessions**, so nothing carries automatically; the link is a DB
lookup on `participant.label` (Prolific ID). In the t2 session there is no `creating_session`, so
`participant.x_draw / treatment / random_draw_1 / random_draw_2` are supplied *only* by
[`retrieve_data`](SBC_consent_t2/__init__.py#L115-L154). That function returns early — leaving those
values `None` — when the label is empty (lines 117–119), when no prior session is found (lines
134–136), or when the source session lacks `x_draw` (lines 151–154).

The next page then crashes: [`Instructions.vars_for_template`](SBC_consent_t2/__init__.py#L187-L197)
computes `A_BAR + participant.x_draw` → `TypeError (int + None)`, and
[`SBC_S1_t2_/draw_order`](SBC_S1_t2_/__init__.py#L98-L112) does `C.PRICES_T1[None]` → `TypeError`.
This fires for empty/duplicate labels and for anyone who reaches Part 2 without a recoverable Part 1.

**Fix.** After `retrieve_data`, check for `None` and route to a clean "we couldn't find your Part 1 —
please contact us" page instead of letting the template crash. Also pick a deterministic rule for
*which* prior session is the Part-1 source (currently `max(session.id)`, which is fragile if a
participant ever restarted Part 1).

### 1.2 Quiz lock-out logic is wrong
[`SBC_consent_form/__init__.py:204-207`](SBC_consent_form/__init__.py#L204-L207) and
[`SBC_consent_t2/__init__.py:233-236`](SBC_consent_t2/__init__.py#L233-L236) set `return_study = 1`
when `quiz_attempts >= 2`:

- The intro promises **"up to three attempts"**
  ([`Quiz.html:256-263`](SBC_consent_t2/Quiz.html#L256-L263)), and the code comment says
  *"3 fails => return the study,"* but the lock-out fires after the **2nd** failure.
- Because the `... and player.return_study == 0` guard stops re-checking once the flag flips, a
  participant who then answers **correctly on the 3rd attempt is still sent to ReturnStudy** — the
  correct answer is discarded.

**Fix.** Raise the threshold to `>= 3` to match "three attempts," and separate "is the answer
correct?" from "has the attempt cap been reached?" so a correct final attempt passes. Same fix in
both consent apps.

### 1.3 t2 quiz "Reveal Instructions" shows the Part-1 instructions
[`SBC_consent_t2/Quiz.html:491`](SBC_consent_t2/Quiz.html#L491) includes
`SBC_consent_form/instr.html` (the Part-1 file) instead of `SBC_consent_t2/instr.html`. A Part-2
participant who opens the reference panel during the comprehension quiz reads Part-1 framing
("This is Part 1," "Part 2 will take place next week," and for treatment 0 "you decide today"), which
contradicts the page they are on. The t2 Decision and ExperimentStarts pages correctly include the
Part-2 file ([`Decision.html:388`](SBC_S1_t2_/Decision.html#L388)), so the quiz is the only page
pointing at the wrong instructions.

**Fix.** One-line change: include `SBC_consent_t2/instr.html` in the t2 quiz.

---

## 2. The t1 → t2 information passing

The core handoff works correctly on the normal path:

- `x_draw` and `treatment` are set in Part 1
  ([`SBC_consent_form/draw_x`](SBC_consent_form/__init__.py#L71-L75)); `random_draw_1/2`, `indexes`,
  and `price_order_*` in [`SBC_S1_t1_/draw_order`](SBC_S1_t1_/__init__.py#L92-L112); the per-round
  record `participant.vars["rounds"]` in
  [`Results.before_next_page`](SBC_S1_t1_/__init__.py#L272-L306).
- Part 2 re-queries the Part-1 participant by label
  ([`SBC_consent_t2/retrieve_data`](SBC_consent_t2/__init__.py#L115-L154)), re-shuffles a fresh
  Part-2 order, and matches each round back to Part 1 **by `index`**
  ([`SBC_S1_t2_/retrieve_data`](SBC_S1_t2_/__init__.py#L115-L173)). Matching on `index` is robust to
  the re-shuffle and to duplicate price pairs.
- The treatment-specific payoff formulas in [`compute_payoff`](SBC_S1_t2_/__init__.py#L195-L303)
  match the participant-facing descriptions (Results, quizzes, Example) for all four treatments.

The residual risks on this path are §1.1 (a failed lookup crashes rather than degrading gracefully)
and the latent code issue in §4.

---

## 3. Medium

### 3.1 `instr.html` reveal panel describes the treatment-2 overwrite wrongly
`instr.html` is the live "Reveal Instructions" panel embedded in the Quiz/Example/ExperimentStarts/
Decision pages, separate from the standalone `Instructions.html` page. For **treatment 2**, the
overwrite paragraph in `instr.html` says participants are *"treated as if they had purchased the
lottery ticket,"* whereas `Instructions.html` correctly says *"the **option to buy** the lottery
ticket."* For the option treatment that distinction matters. A closing "Random Selection" sentence
also differs slightly (a missing "or") between the two files, in both the t1 and t2 versions.

**Fix.** Make the treatment-2 overwrite sentence and the closing sentence in `instr.html` identical to
`Instructions.html`; better, factor the shared instruction body into one included fragment so the page
and the panel cannot drift again.

---

## 4. Low priority (programming)

- **Duplicate `@staticmethod`** on
  [`SBC_S1_t1_/__init__.py:270-272`](SBC_S1_t1_/__init__.py#L270-L272) — `Results.before_next_page`,
  the function that saves `participant.vars["rounds"]` (the entire payload Part 2 reads back). It works
  on Python ≥ 3.10 (which this deploys on, since `numpy>=2` forces a modern Python), but on Python
  < 3.10 a stacked staticmethod is not callable, so the rounds would never save and every Part-2
  retrieval would fail to match. Remove the duplicate decorator; one-line fix.
- **Probability off-by-one:** `random.randint(0, 100)` produces **101** equally likely values, so the
  "{{ payment_prob }}%" payment selection is actually 10/101 ≈ 9.9% and the "2%" overwrite is
  2/101 ≈ 1.98% ([`SBC_S1_t2_/__init__.py:229, 291`](SBC_S1_t2_/__init__.py#L229)). Use
  `randint(1, 100)`.
- **Treatment-1 Example inputs lose typed values on a wrong answer.** The treatment-0/2/3 number inputs
  carry `{% if eN_last is not none %}value="{{ eN_last }}"{% endif %}`, but the treatment-1 block omits
  it ([`SBC_consent_form/Example.html:475-548`](SBC_consent_form/Example.html#L475)), so a treatment-1
  participant who answers incorrectly loses all three numbers they typed. Add the same attribute to the
  treatment-1 inputs.

---

## 5. To confirm (not code bugs, but verify before launch)

- **Is informed consent captured anywhere?** `ConsentForm` is commented out of **both** page sequences
  and the `consent` model field is commented out
  ([`SBC_consent_form/__init__.py:88-90,228`](SBC_consent_form/__init__.py#L88),
  [`SBC_consent_t2/__init__.py:161-164,252`](SBC_consent_t2/__init__.py#L161)). Confirm consent is
  collected somewhere (e.g. on Prolific or a separate page) before data collection. The commented-out
  page also still declares `form_fields=['consent']`, which would crash if it were re-enabled as-is.
- **Is the "no payment unless you return" rule actually true?** The t1 quiz keys Q2 to "No" — i.e. no
  payment at all if the participant does not return for Part 2. Confirm this matches how the study is
  configured on Prolific (and the ethics protocol), since a Part-1-only participant typically still
  receives the Part-1 participation fee.
