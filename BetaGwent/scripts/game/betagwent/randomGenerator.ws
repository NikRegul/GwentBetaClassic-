// Seeded Beta 0.9.24 integer RNG. Signed storage preserves uint32 bit patterns.
// Source: GwentCore.MersenneTwisterRandom, beta-cancel-rng-il.txt.
// The original increments a scalar cursor after twist; do not replace it with
// the usual MT array cursor. All shifts and the seed recurrence below avoid
// overflowing signed arithmetic; do not rely on a host's unchecked multiply.
function BetaGwentLogicalShift(value : int, bits : int) : int
{
    var i, divisor, result : int;
    if (bits == 0) return value;
    if (bits == 31) { if (value < 0) return 1; return 0; }
    divisor = 1;
    for (i = 0; i < bits; i += 1) divisor *= 2;
    result = (value & 2147483647) / divisor;
    if (value < 0) result += 1073741824 / (divisor / 2);
    return result;
}

function BetaGwentRngShiftLeft(value : int, bits : int) : int
{
    var factor, i, result, mask : int;
    if (bits == 0) return value;
    if (bits == 31) { if ((value & 1) != 0) return -1073741824 - 1073741824; return 0; }
    // The generator uses only these three shifts. Keep its hot path bounded.
    if (bits == 1) factor = 2;
    else if (bits == 7) factor = 128;
    else if (bits == 15) factor = 32768;
    else { factor = 1; for (i = 0; i < bits; i += 1) factor *= 2; }
    // Only the low31-bits part is multiplied. Its product is <= Int32.Max.
    mask = 2147483647 / factor;
    result = (value & mask) * factor;
    if ((value & (mask + 1)) != 0)
    {
        result = result - 1073741824;
        result = result - 1073741824;
    }
    return result;
}

function BetaGwentRngSeedMultiply(value : int) : int
{
    var low, high : int;
    // 69069 = 65536 +3533. Every partial product fits signed32.
    low = (value & 65535) * 3533;
    high = (value & 2147483647) / 65536;
    if (value < 0) high += 32768;
    high = (high * 3533 + (value & 65535) + low / 65536) & 65535;
    low = low & 65535;
    if (high >= 32768) high -= 65536;
    return high * 65536 + low;
}

// Remainder through integer division. Retail 1.32 returns wrong results for
// "%" on large operands (logged: 255-like values), while "/" is verified by
// the seeding contract. Requires value >= 0 and maximum > 0.
function BetaGwentRngMod(value : int, maximum : int) : int
{
    var quotient : int;
    quotient = value / maximum;
    return value - quotient * maximum;
}

class CBetaGwentRandomGenerator extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var words : array<int>;
    public var remaining, cursor, reseedValue, initialSeed, draws : int;
    // A failed native integer contract must not silently give every game the
    // same shuffle. Engine samples are captured ONCE and copied with the RNG,
    // so search branches never advance the live engine's random stream.
    public var implementationChecked, engineTapeMode : bool;
    public var engineTape : array<int>;
    public var engineTapeCursor : int;

    public function Initialize(seed : int)
    {
        var first, second, i : int;
        var valid : bool;
        if (!implementationChecked)
        {
            // Saved original Beta seed1 vectors, signed storage.
            engineTapeMode = false; SeedWords(1);
            first = NextBits(); second = NextBits();
            valid = first == -498792314 && second == -1379700580;
            SeedWords(123456789); first = NextBits(); second = NextBits();
            valid = valid && first == -1796496267 && second == 2018078858;
            SeedWords(-1); first = NextBits(); second = NextBits();
            valid = valid && first == 1779771923 && second == -1033671691;
            // Retail 1.32 passed the two-value vectors above yet produced the
            // same deck order for every seed. Exercise the full live path
            // (large seed, cursor draws, bounded draws and Shuffle) and also
            // require two seeds to differ. Small ints compare exactly.
            if (valid && ShuffleSignature(490106781) != "18,5,14,6,9,1,3,21,13,16,17,4,2,10,20,8,12,19,0,23,11,22,24,15,7/1")
            { valid = false; BetaGwentLog("DUEL_RNG_CONTRACT failed=shuffle seed=490106781 got=" + ShuffleSignature(490106781) + " raw=" + RawSignature(490106781)); }
            if (valid && ShuffleSignature(783167041) != "1,10,4,23,17,16,18,13,15,20,5,3,9,24,11,2,7,0,22,6,14,21,8,19,12/1")
            { valid = false; BetaGwentLog("DUEL_RNG_CONTRACT failed=shuffle seed=783167041 got=" + ShuffleSignature(783167041)); }
            if (valid && ShuffleSignature(490106781) == ShuffleSignature(783167041))
            { valid = false; BetaGwentLog("DUEL_RNG_CONTRACT failed=diversity"); }
            implementationChecked = true;
            engineTapeMode = !valid;
            BetaGwentLog("DUEL_RNG_CONTRACT valid=" + valid + " engineTape=" + engineTapeMode);
        }
        initialSeed = seed; draws = 0; reseedValue = seed;
        if (engineTapeMode)
        {
            if (engineTape.Size() == 0)
            {
                engineTape.Resize(1024);
                for (i = 0; i < 1024; i += 1) engineTape[i] = RandRange(1000000000);
            }
            engineTapeCursor = seed; if (engineTapeCursor < 0) engineTapeCursor = 0 - (engineTapeCursor + 1);
            engineTapeCursor = BetaGwentRngMod(engineTapeCursor, 1024);
            return;
        }
        SeedWords(seed);
    }
    public function UsesEngineTape() : bool { return engineTapeMode; }
    // First raw draws and bounded draws, logged only when the contract fails.
    private function RawSignature(seed : int) : string
    {
        var text : string;
        engineTapeMode = false; SeedWords(seed);
        text = "" + NextBits(); text = text + "," + NextBits();
        text = text + "|" + NextBounded(25) + "," + NextBounded(24) + "," + NextBounded(1000);
        text = text + "|mod=" + (745565131 % 1000) + "," + (300 % 7) + " div=" + (745565131 / 1000) + " helper=" + BetaGwentRngMod(745565131, 1000);
        return text;
    }
    // Order of 0..24 after Shuffle plus the next NextBounded(2), as text.
    private function ShuffleSignature(seed : int) : string
    {
        var ids : array<int>; var i : int; var text : string;
        engineTapeMode = false; SeedWords(seed);
        for (i = 0; i < 25; i += 1) ids.PushBack(i);
        Shuffle(ids);
        text = "";
        for (i = 0; i < ids.Size(); i += 1) { if (i > 0) text = text + ","; text = text + ids[i]; }
        text = text + "/" + NextBounded(2);
        return text;
    }
    private function SeedWords(seed : int)
    {
        var i, value : int;
        words.Resize(625); value = seed | 1;
        words[0] = value;
        for (i = 1; i < 624; i += 1) { value = BetaGwentRngSeedMultiply(value); words[i] = value; }
        words[624] = 0; remaining = 0;
    }
    public function InitialSeed() : int { return initialSeed; }
    public function DrawCount() : int { return draws; }
    private function Mix(first : int, second : int) : int
    { return (first & (-2147483647 - 1)) | (second & 2147483647); }
    private function Temper(value : int) : int
    {
        value = value ^ BetaGwentLogicalShift(value, 11);
        value = value ^ (BetaGwentRngShiftLeft(value, 7) & -1658038656);
        value = value ^ (BetaGwentRngShiftLeft(value, 15) & -272236544);
        return value ^ BetaGwentLogicalShift(value, 18);
    }
    private function Twist() : int
    {
        var i, mixed, parity, first, second : int;
        if (remaining < -1) SeedWords(reseedValue);
        remaining = 623;
        // This assignment precedes mutation of words[1] in the original IL.
        cursor = words[1]; first = words[0]; second = words[1];
        for (i = 0; i < 227; i += 1)
        {
            mixed = Mix(first, second); parity = 0;
            if ((second & 1) != 0) parity = -1727483681;
            words[i] = words[i + 397] ^ BetaGwentLogicalShift(mixed, 1) ^ parity;
            first = second; second = words[i + 2];
        }
        for (i = 227; i < 623; i += 1)
        {
            mixed = Mix(first, second); parity = 0;
            if ((second & 1) != 0) parity = -1727483681;
            words[i] = words[i - 227] ^ BetaGwentLogicalShift(mixed, 1) ^ parity;
            first = second; second = words[i + 2];
        }
        second = words[0]; mixed = Mix(first, second); parity = 0;
        if ((second & 1) != 0) parity = -1727483681;
        words[623] = words[396] ^ BetaGwentLogicalShift(mixed, 1) ^ parity;
        return Temper(second);
    }
    public function NextBits() : int
    {
        var value : int;
        draws += 1;
        if (engineTapeMode)
        {
            value = engineTape[engineTapeCursor];
            engineTapeCursor += 1;
            if (engineTapeCursor == engineTape.Size()) engineTapeCursor = 0;
            return value;
        }
        remaining -= 1;
        if (remaining < 0) return Twist();
        value = cursor;
        if (cursor == 2147483647) cursor = -1073741824 - 1073741824;
        else cursor += 1;
        value = Temper(value); reseedValue = BetaGwentRngShiftLeft(value, 1);
        return value;
    }
    public function NextBounded(maximum : int) : int
    {
        var value, remainder, largest : int;
        if (maximum <= 0) return 0;
        value = NextBits();
        if (value >= 0) return BetaGwentRngMod(value, maximum);
        // Original: absolute value, Int32.MinValue becomes Int32.MaxValue.
        // Retail 1.32: avoid "%", unary minus and Int32 limit literals here.
        value = 0 - (value + 1);
        largest = 1073741823 + 1073741824;
        if (value == largest) return BetaGwentRngMod(largest, maximum);
        remainder = BetaGwentRngMod(value, maximum) + 1;
        if (remainder == maximum) remainder = 0;
        return remainder;
    }
    public function Shuffle(out ids : array<int>)
    {
        var count, index, temporary : int;
        count = ids.Size();
        // ListExt.Shuffle: draw bounds N,N-1,...,2 (no bound1 draw).
        while (count > 1)
        {
            count -= 1; index = NextBounded(count + 1);
            temporary = ids[index]; ids[index] = ids[count]; ids[count] = temporary;
        }
    }
}
