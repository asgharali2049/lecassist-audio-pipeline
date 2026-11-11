import json
from pathlib import Path


def _overlap_duration(segment, turn):
    """Return the duration shared by a transcript segment and speaker turn."""
    return max(0.0, min(segment["end"], turn["end"]) - max(segment["start"], turn["start"]))


def _speaker_for_segment(segment, speaker_turns):
    """Select the speaker with the greatest overlap, or UNKNOWN if none overlaps."""
    best_turn = None
    best_overlap = 0.0
    for turn in speaker_turns:
        overlap = _overlap_duration(segment, turn)
        if overlap > best_overlap:
            best_turn = turn
            best_overlap = overlap
    return best_turn["speaker"] if best_turn else "UNKNOWN"


def merge_transcript(segments, speaker_turns, text_path, json_path):
    """Assign speakers and write a paragraph transcript plus structured JSON."""
    merged = []
    text_chunks = []
    for segment in segments:
        speaker = _speaker_for_segment(segment, speaker_turns)
        text = segment["text"].strip()
        record = {
            "start": segment["start"],
            "end": segment["end"],
            "speaker": speaker,
            "text": segment["text"],
        }
        merged.append(record)
        if text:
            text_chunks.append(text)

    text_path = Path(text_path)
    json_path = Path(json_path)
    text_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.write_text(" ".join(text_chunks) + "\n", encoding="utf-8")
    with json_path.open("w", encoding="utf-8") as merged_file:
        json.dump(merged, merged_file, ensure_ascii=False, indent=2)
    return merged