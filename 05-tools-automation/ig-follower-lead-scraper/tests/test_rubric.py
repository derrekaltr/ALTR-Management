from pipeline.common import load_rubric
from pipeline.rubric import score_profile

CFG = load_rubric()


def profile(**overrides):
    base = {
        "username": "testuser",
        "full_name": "Ashley Rose",
        "biography": "content creator | link below",
        "external_url": "https://linktr.ee/ashley",
        "followers": 80_000,
        "is_private": False,
    }
    base.update(overrides)
    return base


def score(**overrides):
    return score_profile(profile(**overrides), CFG)["score"]


# --- hard gates (score 0 = disqualified) ---

def test_private_disqualified():
    assert score(is_private=True) == 0


def test_under_25k_disqualified():
    assert score(followers=24_999) == 0
    assert score(followers=25_000) > 0


def test_male_disqualified():
    assert score(full_name="Michael Johnson", biography="creator | collab") == 0


def test_he_him_disqualified_even_with_female_name():
    assert score(biography="he/him | content creator") == 0


def test_agency_in_username_disqualified():
    assert score(username="omidigital.mgmt", full_name="Omi", biography="top models") == 0


def test_agency_self_describing_bio_disqualified():
    assert score(full_name="Cinderella", biography="Top Modeling Agency in the world") == 0
    assert score(full_name="CreatorsInc", biography="Private Management for the top 0.01%") == 0


def test_agency_word_in_name_disqualified():
    assert score(full_name="Elite Agency", biography="check my highlights") == 0


def test_creator_tagging_their_manager_is_kept():
    # real creator who merely credits the agency repping them — must NOT be dropped
    assert score(full_name="Heloise", biography="model 📍LA | mgmt: @scoutmodelagency",
                 external_url="https://linktr.ee/h") == 4


def test_normal_creator_not_excluded():
    assert score(full_name="Ashley Rose", biography="check my highlights") == 4


def test_business_usernames_disqualified():
    # the user's real examples — all gender-unknown business/theme pages
    for u in ("skategroundmag", "attaboymusic", "rizefighting",
              "techminimalsound", "eletronicas_tracks_tops", "vip_towing"):
        assert score(username=u, full_name="", biography="cool page",
                     external_url="https://linktr.ee/x") == 0, u


def test_business_term_mid_word_not_matched():
    # 'mag' inside 'image', 'dj' inside 'sadjeans': no word edge → not a business
    assert score(username="imagegirl", full_name="🌸", biography="", external_url="https://x.com") > 0
    assert score(username="sadjeans", full_name="🌸", biography="", external_url="https://x.com") > 0


def test_female_creator_with_business_term_kept():
    # confirmed-female accounts are exempt — she's a person, not a page
    assert score(username="ariana.music", full_name="Ariana Lee",
                 biography="check my highlights") == 4


# --- score tiers ---

def test_onlyfans_domain_scores_5():
    assert score(biography="spoil me", external_url="https://onlyfans.com/ash") == 5


def test_onlyfans_keyword_scores_5():
    assert score(biography="link to my onlyfans 🔥", external_url="") == 5


def test_linkhub_domain_scores_4():
    assert score(biography="just me", external_url="https://beacons.ai/girl") == 4


def test_highlights_mention_scores_4():
    assert score(biography="check my highlights 💕", external_url="") == 4


def test_snapchat_handle_scores_4():
    assert score(biography="snap: ashrose 👻", external_url="https://mysite.com") == 4


def test_link_plus_creator_keyword_scores_3():
    assert score(biography="content creator", external_url="https://mysite.com") == 3


def test_link_only_scores_2():
    assert score(biography="living my best life", external_url="https://mysite.com") == 2


def test_keyword_only_scores_2():
    assert score(biography="content creator", external_url="") == 2


def test_bare_pass_scores_1():
    assert score(biography="just a girl", external_url="") == 1


# --- gender-unknown cap ---

def test_unknown_gender_capped_at_3():
    # would be 5 (onlyfans) but gender unknown → capped at 3
    r = score_profile(profile(full_name="🌹🌹", biography="my onlyfans 🔥", external_url=""), CFG)
    assert r["gender"] == "unknown"
    assert r["score"] == 3


def test_unknown_gender_below_cap_unchanged():
    r = score_profile(profile(full_name="🌹🌹", biography="just here", external_url="https://x.com"), CFG)
    assert r["gender"] == "unknown"
    assert r["score"] == 2


def test_confirmed_female_not_capped():
    assert score(full_name="Ashley Rose", biography="my onlyfans", external_url="") == 5
