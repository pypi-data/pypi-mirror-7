def ionization_fraction(obj, pH=None, I=None):
    """Return the ionization fractions of an ion.

    The ionization fraction is based on a given pH and ionic strength.
    """
    if pH is None:
        assert obj._pH, 'requires an input pH'
        pH = obj._pH

    if I is None:
        if obj._I:
            I = obj._I
        else:
            I = 0

    # Get the vector of products of acidity constants.
    L = obj.L(I)
    # Compute the concentration of H+ from the pH.
    cH = 10**(-pH)/obj.activity_coefficient(I, [1])[0]

    # Calculate the numerator of the function for ionization fraction.
    i_frac_vector = [Lp * cH ** z for (Lp, z) in zip(L, obj.z0)]

    # Calculate the vector of ionization fractions
    # Filter out the neutral fraction
    denom = sum(i_frac_vector)
    i_frac = [i/denom for (i, z) in zip(i_frac_vector, obj.z0) if z]

    return i_frac
