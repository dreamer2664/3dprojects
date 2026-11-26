# Design decisions and reconstruction assumptions

1. **Exterior identity** follows the BADA serial-53338 object only. Rococo and
   generic Victorian ornament from comparison instruments is deliberately not
   copied onto this Art Nouveau / Empire instrument.
2. **Scale:** BADA's unitless 214/157 is verified as centimetres by the 1stDibs
   listing for the same serial. The model uses 2.14 × 1.57 × ≈0.99 m. Spline
   overshoot is clamped to those values. Intermediate dimensions (case depth,
   keyboard height, bridge positions) are inferred from the Met Bechstein and
   other period grand pianos and are recorded as assumptions, not as facts about
   serial 53338.
3. **Compass:** 88 keys (A0–C8) is a defensible late-1890s standard. The Met
   Bechstein has AAA–c5; no serial-53338 compass was found. This is an assumption.
4. **Stringing:** two unisons in the low bass and three elsewhere; copper-wound
   bass strings, plain steel treble. The Smithsonian 1900 Blüthner confirms
   Aliquot was available on an ornate Jubilee-plate instrument of the period,
   but not on this serial. Aliquot is therefore omitted rather than claimed.
5. **Pedals:** two, because BADA explicitly describes a two-pedal lyre. The
   common modern third pedal is not added.
6. **Key covering:** historically plausible light-coloured ivory-like naturals
   and dark ebony sharps (BADA notes old ivory registered with Defra). Modern
   plastic is not represented.
7. **Geometry strategy:** repeated parts use linked instances with high-resolution
   shared source meshes. This is a deliberate way to meet the evaluated-triangle
   target inside a 1.9 GB sandbox; it is not decimation.
8. **Texture strategy:** 8K rosewood source archived; 4K working maps in the
   shader because multi-8K loading OOMs. No lower-resolution proxy replaces the
   master geometry.
9. **Repository layout:** brief-mandated `assets/`, `renders/` and `docs/` paths
   are used instead of the repository's existing per-project folder pattern;
   documented in `docs/1899-bluthner-grand-piano/SETUP.md`.
10. **Denosing:** disabled. OIDN OOMs in this sandbox and can erase the thin
    string/filigree detail the commission requires.
