"""Classic 1.32 keeps the pre-0.9.4 profile fields saved.

Next-Gen 5.x writes and reads only the first 45 saved @addField properties of
W3PlayerWitcher (tools/saveprobe094), so there the legacy fields are plain
(non-saved) working copies; the engine still restores them from older saves.
That non-saved restore is unverified on 1.32, where fields are ordinary class
members. Classic therefore keeps them saved next to the single store, which is
authoritative on load on both platforms.
"""
import re

LEGACY = ('betaGwentCollectionSchema betaGwentOwnedIds betaGwentOwnedCopies betaGwentProgressionSeed betaGwentRewardedNpcs '
          'betaGwentRewardActorWins betaGwentStarterSetRevision betaGwentNewCardsSchema betaGwentNewCardIds betaGwentAnimationTempo '
          'betaGwentReducedEffects betaGwentDifficulty betaGwentAiPause betaGwentDeckSchema betaGwentDeckNames betaGwentDeckLeaders '
          'betaGwentDeckFactions betaGwentDeckLengths betaGwentDeckCards betaGwentPreferredDeck betaGwentStarterDeckSchema '
          'betaGwentStarterDeckNames betaGwentStarterDeckLeaders betaGwentStarterDeckFactions betaGwentStarterDeckLengths '
          'betaGwentStarterDeckCards betaGwentKegAutomatic betaGwentKegOffers betaGwentKegAutomaticScraps betaGwentKegsUnopened '
          'betaGwentOpponentBag betaGwentOpponentRecent betaGwentOpponentPoolSize betaGwentCleanupPending090 betaGwentScraps').split()


def patch(text, strict=True):
    """Return text with every legacy declaration marked saved (once each)."""
    for name in LEGACY:
        text, count = re.subn(r'\bprivate var ' + name + r'(\s*:)', r'private saved var ' + name + r'\1', text)
        if strict and count != 1:
            raise ValueError('Classic legacy field %s: %d declarations' % (name, count))
    return text
