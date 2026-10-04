from moex_standard_linkml.solution_xlsx.normalize import match_key, normalize_code


def test_normalize_nbsp_and_spaces():
    r = normalize_code("personId ")
    assert r.value == "personId"
    assert r.had_whitespace
    assert r.changed

    r2 = normalize_code("typeName\xa0")
    assert r2.value == "typeName"
    assert r2.had_nbsp
    assert r2.changed


def test_match_key_casefold():
    assert match_key("Customer") == match_key("CUSTOMER")
    assert match_key("  Id ") == "id"
