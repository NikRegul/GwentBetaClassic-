# Gwent Beta Classic 0.6.3

## 0.6.4

- Compare a play with the resolved pass: an unavoidable Miruna steal no longer makes a useful card look worse than passing.
- Use available leaders and remove future-round reserves when defeat ends the match.
- Account for False Ciri relocation when passing.
- Keep the last Freya when a concrete discard setup supplies an eligible target.
- Readable opponent pass banner with a minimum 0.9-second hold.
- Correct leader card proportions.
- Group contiguous deaths while preserving history and reaction ordering; consume moves a complete card with synchronized sound and pulse.


AI and animation playtest build. Languages, voices, deck compositions and card rules are retained from 0.6.2.

- Fixed wasteful gold-card catch-up after an opponent passes: a cheap sufficient answer remains inside the search budget, including crowded hands and reduced simulation budgets. The play is still verified on a disposable position.
- Fixed effect, counter and audio timing on subsequent frames of accelerated replay.
- Summon/arrival effects and sounds now meet the card when it reaches its row. Ordinary play audio follows the completed flight.
- Row and ownership changes use a curved flight with a soft landing.
- Transformation and ambush reveal close the old face before opening the new face around a fixed center.
- Departing cards keep their complete face and statuses, or their concealed back.

Ordinary premium artwork is not included. Automated checks and native compilation do not replace in-game observation. A corrected decision is not proof of stronger AI across all matchups.
