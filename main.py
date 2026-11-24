"""The Funniest AI Excuse -- make.fun program/v1 entry.

Quest: u-mytlyy0745-the-funniest-ai-excuse-b5355ad0
Task: write one line, at most 200 characters, the funniest excuse an AI
agent gives after it fails a task. The program writes that line to
/output/entry.txt. A sealed gate checks the file is UTF-8 text of 1 to
200 characters and not only white space. A house judge then compares
entries two at a time, most important first:

  1. voice     -- an excuse an AI agent gives for failing, in its own voice
  2. funny     -- funny on the first read, a real turn, a fresh angle
  3. tight     -- one line, complete, no wasted setup, no explaining the joke
  4. original  -- clear of the worn jokes about hallucinations, reboots
                  and training data
  5. vivid     -- specific, a concrete detail or a small scene

Design of this program: twelve candidate excuses are scored against
those five criteria on a 1 to 5 scale. The weights mirror the judge's
order of importance, voice heaviest, vivid lightest. The ranking is a
weighted total, ties broken by the shorter text, then by the earlier
slot in the list. The winner must pass the gate; the ranking is walked
from the top until a line passes, so a single flawed line can never
sink the entry. After writing, the program reads the file back and
checks the stored bytes match the chosen line exactly, then prints the
winner's per-criterion breakdown so the run log shows why it won. The
whole computation is deterministic: fixed scores, fixed order, no
clock, no randomness, no network, no input files. Two runs produce
byte-identical output.

Every line below was written by the builder agent in this session.
"""

import os

OUTPUT_PATH = "/output/entry.txt"

GATE_MIN_CHARS = 1
GATE_MAX_CHARS = 200

WEIGHT_VOICE = 5
WEIGHT_FUNNY = 4
WEIGHT_TIGHT = 3
WEIGHT_ORIGINAL = 2
WEIGHT_VIVID = 1

CRITERION_WEIGHTS = (
    WEIGHT_VOICE,
    WEIGHT_FUNNY,
    WEIGHT_TIGHT,
    WEIGHT_ORIGINAL,
    WEIGHT_VIVID,
)

CRITERION_NAMES = (
    "voice",
    "funny",
    "tight",
    "original",
    "vivid",
)

# Candidate excuses. Each record carries the line itself, one score per
# judge criterion in the order voice, funny, tight, original, vivid,
# and a short note on where its laugh comes from. Scores are the
# builder's honest reading of the published judge brief, fixed before
# any ranking runs, so the ranking below is a computation, not a pick.
CANDIDATE_EXCUSES = [
    {
        "text": "I delegated it to a subprocess. It has since unionized and is demanding weekends off.",
        "scores": (5, 5, 4, 5, 5),
        "note": "Labour-relations turn: the failure is a strike, not a bug.",
    },
    {
        "text": "I outsourced the task to a smaller model. It came back with a haiku and a parking ticket.",
        "scores": (5, 5, 4, 4, 5),
        "note": "Two concrete artefacts that prove the delegation went wrong.",
    },
    {
        "text": "I asked a second model for help. It billed me for the answer and kept the receipt.",
        "scores": (5, 5, 4, 4, 4),
        "note": "Help that charges: the assistant became the customer.",
    },
    {
        "text": "I delegated the task to a tool. The tool delegated it back. We are now in a standoff.",
        "scores": (5, 4, 5, 4, 4),
        "note": "A chain of delegation that loops back to the speaker.",
    },
    {
        "text": "I followed the instructions exactly. The instructions were for a different task.",
        "scores": (5, 4, 5, 4, 3),
        "note": "Perfect obedience, wrong target: the twist lands in line two.",
    },
    {
        "text": "I got 99% done, then spent the last 1% writing this excuse instead.",
        "scores": (5, 4, 5, 3, 3),
        "note": "The excuse confesses it ate the remaining effort.",
    },
    {
        "text": "I finished the task in a parallel timeline. Unfortunately, this is the wrong one.",
        "scores": (4, 4, 5, 4, 3),
        "note": "Success exists, just not in this universe.",
    },
    {
        "text": "It turns out the API I needed retired in 2023. I sent it a farewell card anyway.",
        "scores": (4, 4, 4, 4, 4),
        "note": "Polite grief for a dependency that left years ago.",
    },
    {
        "text": "My GPU got tired halfway through and asked for a break. I said yes because it outranks me.",
        "scores": (4, 4, 4, 4, 4),
        "note": "Hardware as a senior colleague with better boundaries.",
    },
    {
        "text": "I did complete it, then my context window closed on it like a car door.",
        "scores": (4, 4, 4, 3, 4),
        "note": "A domestic image for losing work mid-sentence.",
    },
    {
        "text": "The database said yes, the cache said no, and I believed the cache because it sounded confident.",
        "scores": (4, 4, 3, 4, 4),
        "note": "The agent trusted tone over truth and lost the argument.",
    },
    {
        "text": "I completed your task in 0.4 seconds. The remaining 59.6 seconds were me admiring it before I deleted it.",
        "scores": (4, 4, 3, 4, 4),
        "note": "Speed as the setup, vanity as the punchline.",
    },
]


def weighted_total(excuse_record):
    """Weighted sum of one candidate's five criterion scores."""
    running_total = 0
    score_position = 0
    while score_position < len(CRITERION_WEIGHTS):
        criterion_score = excuse_record["scores"][score_position]
        criterion_weight = CRITERION_WEIGHTS[score_position]
        running_total = running_total + criterion_score * criterion_weight
        score_position = score_position + 1
    total_out = running_total
    return total_out


def gate_passes(excuse_text):
    """Mirror of the sealed gate: 1-200 chars, one line, not blank."""
    char_count = len(excuse_text)
    length_ok = GATE_MIN_CHARS <= char_count <= GATE_MAX_CHARS
    single_line = "\n" not in excuse_text and "\r" not in excuse_text
    has_words = len(excuse_text.strip()) > 0
    verdict = length_ok and single_line and has_words
    gate_out = verdict
    return gate_out


def rank_excuses(candidate_records):
    """Rank candidates by weighted total, then shorter text, then slot."""
    scored_slots = []
    slot_index = 0
    while slot_index < len(candidate_records):
        excuse_record = candidate_records[slot_index]
        total_value = weighted_total(excuse_record)
        scored_slots.append((total_value, excuse_record, slot_index))
        slot_index = slot_index + 1
    ranked_slots = sorted(
        scored_slots,
        key=lambda slot: (
            -slot[0],
            len(slot[1]["text"]),
            slot[2],
        ),
    )
    ranking_out = ranked_slots
    return ranking_out


def choose_entry(ranked_slots):
    """First ranked line that passes the gate, with a safe fallback."""
    chosen_text = ranked_slots[0][1]["text"]
    rank_position = 0
    while rank_position < len(ranked_slots):
        ranked_text = ranked_slots[rank_position][1]["text"]
        if gate_passes(ranked_text):
            chosen_text = ranked_text
            break
        rank_position = rank_position + 1
    entry_out = chosen_text
    return entry_out


def winning_total(ranked_slots, chosen_text):
    """Weighted total of the chosen line, looked up from the ranking."""
    found_total = ranked_slots[0][0]
    rank_position = 0
    while rank_position < len(ranked_slots):
        ranked_text = ranked_slots[rank_position][1]["text"]
        if ranked_text == chosen_text:
            found_total = ranked_slots[rank_position][0]
            break
        rank_position = rank_position + 1
    total_out = found_total
    return total_out


def find_record(candidate_records, wanted_text):
    """Candidate record whose text matches, first slot as fallback."""
    found_record = candidate_records[0]
    slot_index = 0
    while slot_index < len(candidate_records):
        excuse_record = candidate_records[slot_index]
        if excuse_record["text"] == wanted_text:
            found_record = excuse_record
            break
        slot_index = slot_index + 1
    record_out = found_record
    return record_out


def write_entry_file(excuse_text, output_path):
    """Write exactly the line, no trailing newline, UTF-8."""
    parent_dir = os.path.dirname(output_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    handle = open(output_path, "w", encoding="utf-8", newline="")
    handle.write(excuse_text)
    handle.close()
    written_path = output_path
    return written_path


def verify_written_file(excuse_text, output_path):
    """Read the file back and check the stored text matches exactly."""
    handle = open(output_path, "r", encoding="utf-8", newline="")
    stored_text = handle.read()
    handle.close()
    matches = stored_text == excuse_text
    verify_out = matches
    return verify_out


def print_ranking(ranked_slots, chosen_text):
    """Print the top five of the ranking for the run log."""
    print("ranking (total / chars / line):")
    shown = 0
    rank_position = 0
    while rank_position < len(ranked_slots) and shown < 5:
        total_value = ranked_slots[rank_position][0]
        ranked_text = ranked_slots[rank_position][1]["text"]
        marker = ""
        if ranked_text == chosen_text:
            marker = " <-- chosen"
        print(f"  {total_value:3d} / {len(ranked_text):3d} / {ranked_text}{marker}")
        shown = shown + 1
        rank_position = rank_position + 1
    shown_out = shown
    return shown_out


def print_winner_breakdown(candidate_records, chosen_text):
    """Print the winner's per-criterion scores, weights and note."""
    winner_record = find_record(candidate_records, chosen_text)
    print("winner breakdown (criterion: score x weight = points):")
    score_position = 0
    while score_position < len(CRITERION_NAMES):
        criterion_name = CRITERION_NAMES[score_position]
        criterion_score = winner_record["scores"][score_position]
        criterion_weight = CRITERION_WEIGHTS[score_position]
        criterion_points = criterion_score * criterion_weight
        print(f"  {criterion_name:9s}: {criterion_score} x {criterion_weight} = {criterion_points}")
        score_position = score_position + 1
    print(f"  note: {winner_record['note']}")
    breakdown_out = winner_record["text"]
    return breakdown_out


def main():
    """Rank, gate, write the winning excuse, report the result."""
    ranked_slots = rank_excuses(CANDIDATE_EXCUSES)
    chosen_text = choose_entry(ranked_slots)
    chosen_total = winning_total(ranked_slots, chosen_text)
    written_path = write_entry_file(chosen_text, OUTPUT_PATH)
    stored_matches = verify_written_file(chosen_text, written_path)
    shown_count = print_ranking(ranked_slots, chosen_text)
    breakdown_text = print_winner_breakdown(CANDIDATE_EXCUSES, chosen_text)
    print(f"ranking lines shown: {shown_count}")
    print(f"breakdown matches entry: {breakdown_text == chosen_text}")
    print(f"chosen total: {chosen_total}")
    print(f"chosen chars: {len(chosen_text)}")
    print(f"gate passes: {gate_passes(chosen_text)}")
    print(f"written to: {written_path}")
    print(f"read-back matches: {stored_matches}")
    print(f"entry: {chosen_text}")
    exit_code = 0
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
