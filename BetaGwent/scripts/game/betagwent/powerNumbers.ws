// Numeric boundary port; original40 fixtures passed, native acceptance pending.
// Numeric CardPower subset from original Beta0.9.24.3.432 IL.
// The final setter is a boundary: events, death and banish still need a live card.
abstract class CBetaGwentPowerNumbers extends IScriptable
{
    private var initialized : bool;
    private var basePower : int;
    private var permanentPower : int;
    private var currentPower : int;
    private var currentArmor : int;

    // Local reconstruction boundary, not original CardPower.Init/Reset.
    // Keeps raw fields: clamping belongs to the original operation/setter.
    public function InitFromFields(value : SBetaGwentPower) : bool
    {
        if (initialized) return false;
        basePower = value.basePower;
        permanentPower = value.permanentPower;
        currentPower = value.currentPower;
        currentArmor = value.armor;
        initialized = true;
        return true;
    }

    public function IsInitialized() : bool { return initialized; }
    public function GetBasePower() : int { return basePower; }
    public function GetPermanentPower() : int { return permanentPower; }
    public function GetCurrentPower() : int { return currentPower; }
    public function GetCurrentArmor() : int { return currentArmor; }
    public function Snapshot() : SBetaGwentPower
    {
        var value : SBetaGwentPower;
        value.basePower = basePower;
        value.permanentPower = permanentPower;
        value.currentPower = currentPower;
        value.armor = currentArmor;
        return value;
    }

    // Only the eventual SetPowerAndArmor implementation writes these fields.
    // Raw setters are also useful for controlled callback fixtures.
    protected function WriteCurrentPower(value : int) { currentPower = value; }
    protected function WriteCurrentArmor(value : int) { currentArmor = value; }
    protected function WriteBasePower(value : int) { basePower = value; }
    protected function WritePermanentPower(value : int) { permanentPower = value; }

    public function SetPower(value : int) : bool
    {
        if (!initialized) return false;
        return SetPowerAndArmor(value, currentArmor);
    }
    public function SetArmor(value : int) : bool
    {
        if (!initialized) return false;
        return SetPowerAndArmor(currentPower, value);
    }
    public function SetBasePower(value : int) : bool
    {
        if (!initialized) return false;
        return SetBasePowerAndArmor(value, currentArmor);
    }
    public function SetPermanentPower(value : int) : bool
    {
        if (!initialized) return false;
        return SetPermanentPowerAndArmor(value, currentArmor);
    }
    public function SetBasePowerAndArmor(value : int, armor : int) : bool
    {
        var delta : int;
        if (!initialized) return false;
        // Original delta uses the requested value BEFORE the nonnegative clamp.
        delta = value - basePower;
        basePower = Max(0, value);
        permanentPower = Max(-basePower, permanentPower);
        return SetPowerAndArmor(currentPower + delta, armor);
    }
    public function SetPermanentPowerAndArmor(value : int, armor : int) : bool
    {
        var delta : int;
        if (!initialized) return false;
        delta = value - permanentPower;
        permanentPower = Max(-basePower, value);
        return SetPowerAndArmor(currentPower + delta, armor);
    }
    public function RestorePower(value : int) : bool
    {
        var current : int;
        var maximum : int;
        var missing : int;
        if (!initialized) return false;
        current = currentPower;
        maximum = basePower + permanentPower;
        if (current >= maximum) return true;
        missing = maximum - current;
        // A negative restore argument is not clamped by the original method.
        return SetPowerAndArmor(current + Min(value, missing), currentArmor);
    }
    public function AddArmor(value : int) : bool
    {
        if (!initialized) return false;
        return SetPowerAndArmor(currentPower, currentArmor + value);
    }
    public function MultiplyArmor(multiplier : int) : bool
    {
        var multiplied : int;
        if (!initialized) return false;
        if (!MultiplyValue(currentArmor, multiplier, multiplied)) return false;
        return SetPowerAndArmor(currentPower, multiplied);
    }

    public function MultiplyValue(value : int, multiplier : int, out result : int) : bool
    {
        var factor : float;
        var product : float;
        // Keep float division/product. Integer percent arithmetic is different.
        factor = (float)multiplier / 100.0f;
        product = (float)value * factor;
        // conv.i4 outside Int32 is CLR/runtime dependent. Reject this unported
        // edge explicitly, rather than relying on native FloorF overflow.
        // The upper bound is exclusive because float rounds Int32.MaxValue up.
        if (product < -2147483648.0f || product >= 2147483648.0f) return false;
        result = FloorF(product);
        return true;
    }

    // Must be supplied by the live-card layer. A missing effect fails closed.
    // Failure does not roll back earlier base/permanent writes; original
    // setter callbacks can throw after those writes as well.
    protected function SetPowerAndArmor(power : int, armor : int) : bool
    {
        return false;
    }
}
