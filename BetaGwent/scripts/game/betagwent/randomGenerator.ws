// Seeded Beta 0.9.24 integer RNG. Signed storage preserves uint32 bit patterns.
// Source: GwentCore.MersenneTwisterRandom, beta-cancel-rng-il.txt.
// The original increments a scalar cursor after twist; do not replace it with
// the usual MT array cursor. Native overflow/shift acceptance remains deferred.
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

class CBetaGwentRandomGenerator extends IScriptable
{
    private var words : array<int>;
    private var remaining, cursor, reseedValue, initialSeed, draws : int;

    public function Initialize(seed : int)
    {
        initialSeed = seed; draws = 0; reseedValue = seed;
        SeedWords(seed);
    }
    private function SeedWords(seed : int)
    {
        var i, value : int;
        words.Resize(625); value = seed | 1;
        words[0] = value;
        for (i = 1; i < 624; i += 1) { value *= 69069; words[i] = value; }
        words[624] = 0; remaining = 0;
    }
    public function InitialSeed() : int { return initialSeed; }
    public function DrawCount() : int { return draws; }
    private function Mix(first : int, second : int) : int
    { return (first & (-2147483647 - 1)) | (second & 2147483647); }
    private function Temper(value : int) : int
    {
        value = value ^ BetaGwentLogicalShift(value, 11);
        value = value ^ ((value * 128) & -1658038656);
        value = value ^ ((value * 32768) & -272236544);
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
        draws += 1; remaining -= 1;
        if (remaining < 0) return Twist();
        value = cursor; cursor += 1;
        value = Temper(value); reseedValue = value * 2;
        return value;
    }
    public function NextBounded(maximum : int) : int
    {
        var value : int;
        if (maximum <= 0) return 0;
        value = NextBits();
        if (value == (-2147483647 - 1)) value = 2147483647;
        else if (value < 0) value = -value;
        return value % maximum;
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
