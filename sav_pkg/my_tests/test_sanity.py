def test_sanity_import():
    import sav_pkg
    from sav_pkg.policies.sav import ProcedureX

    assert sav_pkg is not None
    assert ProcedureX.name == "Procedure X"
