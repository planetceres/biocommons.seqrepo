import pytest

from biocommons.seqrepo import SeqRepo


@pytest.fixture(scope="session")
def seqrepo(tmpdir_factory):
    dir = str(tmpdir_factory.mktemp('seqrepo'))
    return SeqRepo(dir, writeable=True)


@pytest.fixture(scope="session")
def seqrepo_ro(tmpdir_factory):
    dir = str(tmpdir_factory.mktemp('seqrepo'))
    sr = SeqRepo(dir, writeable=True)
    del sr    # close it
    return SeqRepo(dir)


@pytest.fixture(scope="session")
def seqrepo_keepcase(tmpdir_factory):
    dir = str(tmpdir_factory.mktemp('seqrepo'))
    return SeqRepo(dir, upcase=False, writeable=True)


def test_create(seqrepo):
    assert str(seqrepo).startswith('SeqRepo(root_dir=/')


def test_store(seqrepo):
    seqrepo.store("SMELLASSWEET", [{"namespace": "en", "alias": "rose"}, {"namespace": "fr", "alias": "rose"}])
    seqrepo.store("smellassweet", [{"namespace": "es", "alias": "rosa"}])    # same sequence, new alias

    seqrepo.store("ASINCHANGE", [{"namespace": "en", "alias": "coin"}])    # same alias, diff seqs in diff namespaces
    seqrepo.store("ASINACORNER", [{"namespace": "fr", "alias": "coin"}])
    seqrepo.commit()


def test_fetch(seqrepo):
    assert seqrepo.fetch("rose") == "SMELLASSWEET"
    assert seqrepo["rose"] == "SMELLASSWEET"
    assert seqrepo.fetch("rosa") == "SMELLASSWEET"
    assert "rosa" in seqrepo

    assert len(list(rec for rec in seqrepo)) == 3

    assert seqrepo.fetch("rosa", start=5, end=7) == "AS"

    with pytest.raises(KeyError):
        assert seqrepo.fetch("bogus")    # non-existent alias

    with pytest.raises(KeyError):
        assert seqrepo.fetch("coin")    # ambiguous alias

    assert seqrepo.fetch("coin", namespace="en") == "ASINCHANGE"
    assert seqrepo.fetch("coin", namespace="fr") == "ASINACORNER"

    assert seqrepo.fetch_uri("en:coin") == "ASINCHANGE"
    assert seqrepo.fetch_uri("fr:coin") == "ASINACORNER"


def test_digests(seqrepo):
    """tests one set of digests"""

    # to get aliases, add "import time; time.sleep(120)" above, then:
    # (3.5) snafu$ SEQREPO_ROOT_DIR=/tmp/pytest-of-reece/pytest-0/seqrepo0 seqrepo export -i .
    assert seqrepo.fetch_uri("fr:coin") == "ASINACORNER"
    assert seqrepo.fetch_uri("MD5:ea81b52627e387fc6edd8b9412cd3a99") == "ASINACORNER"
    assert seqrepo.fetch_uri("SEGUID:aMQF/cdHkAayLkVYs8XV2u+Hy34") == "ASINACORNER"
    assert seqrepo.fetch_uri("SHA1:68c405fdc7479006b22e4558b3c5d5daef87cb7e") == "ASINACORNER"
    assert seqrepo.fetch_uri("VMC:GS_LDz34B6fA_fLxFoc2agLrXQRYuupOGGM") == "ASINACORNER"
    

def test_errors(seqrepo_ro):
    with pytest.raises(RuntimeError):
        seqrepo_ro.store("SHOULDFAIL", [{"namespace": "fr", "alias": "coin"}])


def test_keepcase(seqrepo_keepcase):
    seqrepo_keepcase.store("ifIonlyHADaBRAIN", [{"namespace": "me", "alias": "iiohab"}])
    assert seqrepo_keepcase["iiohab"] == "ifIonlyHADaBRAIN"
