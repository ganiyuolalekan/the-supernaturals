"""
10 photorealistic scene prompts for The SuperNaturals.

Scenes kept (per final selection):
  Miracles & Power    : walking-on-water, commanding-the-storm
  Authority & Warfare : defeating-giants, silencing-the-lion, breaking-every-chain
  Fire & Spirit       : walking-through-fire, anointed-with-oil
  Ascension & Glory   : eagle-wings, army-of-angels, receiving-the-mantle

Each prompt is sourced from supernatural_prompt_book.md with two modifications:
  1. The trailing "No text…" line is stripped (re-appended by prompt_builder).
  2. Every scene dresses the subject in wardrobe chosen for that scene rather
     than preserving whatever they happened to wear in their upload — street
     clothes were pulling the generated portraits out of the scene. The styling
     is deliberately modern and clean (contemporary tailoring, no ancient
     robes or gowns) so people still look like themselves:
       walking-on-water      → crisp all-white modern, barefoot
       commanding-the-storm  → off-white shirt + long ivory storm coat
       defeating-giants      → white & gold battle armor
       silencing-the-lion    → sharp black modern tailoring, gold detail
       breaking-every-chain  → plain white tee, bare forearms
       walking-through-fire  → pristine white, spotless inside the furnace
       anointed-with-oil     → modern white ceremonial coat, gold embroidery
       eagle-wings           → white with a trailing lightweight overlayer
       army-of-angels        → white & gold battle armor
       receiving-the-mantle  → understated everyday stone-white and dark
     All 10 retain the "large white wings" supernatural identifier. Identity
     (face, skin tone, hair, build) is preserved by prompt_builder's identity
     lock, and a user's custom prompt still overrides the wardrobe.
"""

from datetime import date, timedelta

# Campaign schedule: one scene "live" per week, in the order below, starting
# launch week. Order matches the progression: Miracles & Power -> Authority &
# Warfare -> Fire & Spirit -> Ascension & Glory (see get_scene_ids()).
LAUNCH_DATE = date(2026, 8, 8)  # Week 1 — Walking on Water (Saturday)
WEEK_LENGTH_DAYS = 7

SCENE_PROMPTS: dict[str, str] = {
    # ──────────────────────── MIRACLES & POWER ────────────────────────
    "walking-on-water": """A photorealistic fantasy realism full-body low-angle shot taken from just above water level,
looking up at a supernatural figure walking across the surface of a dark, churning ocean at
night. He moves forward with slow, deliberate confidence—one foot fully planted on the water,
the other mid-stride—looking directly into the camera with fearless calm authority. He is
dressed in crisp, modern all-white: a clean white long-sleeved shirt with the sleeves worn
down and unfolded, fully and properly buttoned, left untucked over loose, free-cut white
trousers (not tight or slim), the hems darkened and clinging where they meet the sea, feet
bare on the water—contemporary tailoring with visible fabric weave and stitching, not a robe
or gown; large white wings are spread wide to their full span, individual feathers defined. The water surface directly beneath each footstep glows with faint golden-white
ripples radiating outward like a pulse, as though the sea itself recognizes his authority.
The lighting is cinematic—strong volumetric god rays pierce downward through breaking storm
clouds, moonlight catches the water surface, and strong rim lighting traces his silhouette
against the dark sea. Realistic shadows, subsurface scattering on skin, physically accurate
reflections of the divine light on his clothing. In the blurry background, the distant storm
rages—dark churning waves, lightning on the far horizon. Cool dark oceanic color grading with
warm divine gold on the subject. Epic biblical scale.""",

    "commanding-the-storm": """A photorealistic fantasy realism full-body worm's-eye view shot of a supernatural warrior
commanding a raging storm to stop. He stands at the bow of a battered wooden ship on a
violently churning sea, both arms raised and spread to each side in a wide commanding posture,
looking upward into the heart of the storm with calm, absolute authority. He is dressed in a
modern storm-white ensemble: an off-white long-sleeved shirt with the sleeves worn down and
unfolded, fully and properly buttoned and left untucked, beneath a long, unlined ivory coat
that snaps and streams sideways in the gale, loose, free-cut dark trousers (not tight or slim)
and boots planted on the soaked deck—contemporary cut, no robes; massive white wings
spread to full span, each feather straining against the gale but unbroken. Directly before
him, the storm clouds are splitting open—a dramatic rent in the sky with brilliant golden
light flooding through the gap—while the sea directly beneath him begins to still in a
spreading circle of calm, ripples going flat. Massive black storm clouds curl away on either
side. Lightning arcs around him on both sides but does not touch him. The lighting is extreme
cinematic—strong volumetric god rays cut through the split in the clouds, deep shadow on the
raging storm around him contrasting the brilliant golden breach above. Realistic subsurface
scattering on skin, physically accurate wing feather displacement from wind force. In the
blurry background, towering dark waves. Dark storm grey and deep navy with explosive gold at
the center breach. Epic biblical scale.""",

    # ─────────────────────── AUTHORITY & WARFARE ───────────────────────
    "defeating-giants": """A photorealistic fantasy realism full-body extreme low-angle shot of a supernatural warrior
standing triumphant beside a defeated giant. He stands on flat open ground, his feet planted
wide and firm on the bare cracked earth—never standing on, stepping on or touching the giant's
body—looking directly into the camera with quiet steel-eyed confidence—calm after the battle, not
boasting. He wears white and gold ceremonial armor of a
heavenly warrior—a fitted white cuirass and shoulder pauldrons with ornate polished-gold edging
worn over flowing white robes, a long white fabric tabard embroidered with gold falling down the
front over the legs, a gold waist belt; the cloth drapes in natural folds and the silhouette is
regal, majestic and angelic;
large white wings spread fully behind him, tips nearly grazing the ground on each side. On the
ground in front of him and off to one side, the massive form of a fallen giant lies defeated on
the bare cracked earth—a huge, powerfully-built man of enormous size clad in heavy dark battle armor, a
rugged iron-grey breastplate and armored plates battered and dented from the fight, his large
armored body clearly and fully visible in the light, head fallen back and limbs sprawled,
unmistakably beaten; not a shadow or silhouette but a solid physical body. The warrior stands
clear of the giant, not on top of it. A single smooth stone, still glowing with
faint warm divine energy, rests on the ground beside the giant's body, and the earth is cracked
and disturbed where he fell.
The lighting is bright, soft and luminous—hazy heavenly daylight with strong volumetric god rays
pouring down from behind the warrior, rim-lighting his silhouette and wings in warm gold while
still lighting the fallen giant clearly and fully. Realistic subsurface scattering on skin.
In the softly blurred background stretches a vast battlefield host—a great crowd and army of many
figures behind him, with rows of pale tents and tall raised banners and flags on poles, receding
into bright atmospheric haze toward distant faint mountains. Luminous, warm golden light, epic
biblical scale.""",

    "silencing-the-lion": """A photorealistic fantasy realism full-body eye-level shot of a supernatural warrior with a
lion fully submitted before him. He stands tall on dark rocky ground, feet planted at shoulder
width, right hand lowered with palm open and facing the animal in a firm, quiet stay gesture—
no drama, no exertion, effortless dominion—looking down at the lion with calm, unruffled
authority, as though this submission is not a surprise. He is dressed in sharply tailored
modern black—a fitted single-breasted jacket open at the collar over a crisp white shirt,
slim black trousers and clean boots, a thin line of gold detail at the cuffs and collar;
understated, expensive, unmistakably present-day; large white wings are spread wide to their full span behind him,
individual feathers defined and still. Before him, a massive African lion—fully grown,
muscular, heavy-maned, visibly powerful but completely subdued—is prostrate: front legs
folded, enormous head bowed to the ground, eyes averted, body low. The air between them is
charged. The lighting is cinematic—a warm golden spotlight from above illuminates both the
warrior and the lion, strong rim light on the lion's mane creating a crown-like halo that
emphasises its greatness and its surrender simultaneously, shadows falling dramatically behind
both figures. Subsurface scattering on skin, hyper-detailed lion fur with individual hair
strands visible. In the blurry background, a wild rocky landscape at deep twilight. Warm amber
and dark ochre color grading with sharp golden spotlight on both figures. Powerful cinematic
scale.""",

    "breaking-every-chain": """A photorealistic fantasy realism full-body low-angle shot of a supernatural warrior at the
moment of total liberation. He stands with arms thrust outward to both sides in one explosive,
liberating motion—a freeze frame of maximum force—head tilted slightly back, eyes open wide
with fierce, triumphant authority. He is dressed in plain modern clothing—a simple white
fitted t-shirt and dark slim trousers, sleeves short so the bare forearms and wrists are fully
exposed where the shackles are shattering; the plainness is deliberate, the everyday clothing
of a present-day person walking out of captivity, no armor and no robes;
massive white wings are spread fully, every feather displaced outward from
the force of the breaking moment. Thick iron chains—deeply textured, corroded, dark metal with
visible rust and forge marks—are exploding outward from around his wrists, waist, and ankles,
fragments frozen mid-air in every direction with cinematic motion blur on each shard. Every
broken link glows red-hot at the fracture point, the heat of the break visible. A brilliant
white light erupts from the center of his chest—not a beam, but a detonation, the source of
the force that shattered everything. The lighting is explosive and high-contrast—the central
chest light as the primary source, casting hard dramatic shadows outward across the frame,
each chain fragment highlighted as a dark object against brilliant white. Realistic subsurface
scattering on skin. In the blurry background, ancient stone prison walls and floor. Deep black
with explosive white and gold burst at center frame. Epic, liberating scale.""",

    # ───────────────────────── FIRE & SPIRIT ─────────────────────────
    "walking-through-fire": """A photorealistic fantasy realism full-body low-angle shot of a supernatural warrior walking
unharmed through the heart of a raging furnace. He strides forward through a corridor of
massive, roaring flames—forty-foot walls of orange and white fire rising on both sides of
him—looking directly into the camera with absolute calm, not a strand of hair displaced,
not a thread of his clothing darkened. He is dressed in pristine modern white—a white
long-sleeved shirt with the sleeves worn down and unfolded, fully and properly buttoned and
left untucked, over loose, free-cut white trousers (not tight or slim), crisply pressed and
spotless inside the inferno, not a fibre burned, not a thread scorched, not a trace of soot or
smoke on the fabric; clean contemporary tailoring, no robes; large white wings
spread wide to their full span, feathers unsinged, the orange firelight reflecting off each one.
Beside him and one step behind, a fourth figure walks—tall, robed entirely in brilliant, dense
white light, form present but not fully defined, clearly supernatural—moving with the same
unhurried calm. The lighting is entirely from the fire—massive warm orange illumination from
both sides, realistic fire-light flickering on his clothing, face, and wings, creating deep
cast shadows between them, the white robed figure providing cool white counter-light.
Realistic flame physics, ember particles floating in the air, heat distortion visible in the
air above both figures. Deep charcoal and warm fire-orange color grading, the white divine
companion as the only cool element in the frame. Epic biblical scale.""",

    "anointed-with-oil": """A photorealistic fantasy realism full-body portrait shot of a supernatural figure being
anointed directly from heaven. He stands still, eyes gently closed, face tilted slightly
upward—a posture of deep, active receiving, the stillness of someone fully aware of what is
happening to them—arms at his sides, palms open. He wears modern white ceremonial dress—a
long-line tailored white coat worn open over a white long-sleeved shirt with the sleeves worn
down and unfolded, fully and properly buttoned to the collar and left untucked, and loose,
free-cut white trousers (not tight or slim), fine gold embroidery tracing the lapel, cuffs
and hem; the bearing of priest
and king rendered in contemporary tailoring rather than ancient robes, the embellishment
catching the descending light; large white wings extend to their fullest span behind him. From
directly above, a column of luminous golden oil descends from a point of brilliant light high
in the sky—not water, but something denser, deliberate, purposeful—pouring onto the crown of
his head and flowing down over his hair, his shoulders, his robes, leaving a glistening
golden trail that catches and refracts light within each rivulet. The oil has its own inner
luminescence. A pool of glowing golden liquid gathers at his feet and spreads slowly outward.
The lighting is top-down divine—the heavenly beam is the primary and only light source,
casting brilliant overhead gold illumination, strong rim light on his shoulders and the upper
face of each wing, deep warm shadow falling below. Subsurface scattering on skin illuminated
from directly above. In the blurry background, a high open place—mountaintop or rooftop—
against deep blue sky. Deep royal purple and rich gold color grading. Regal, consecrating
scale.""",

    # ──────────────────────── ASCENSION & GLORY ────────────────────────
    "eagle-wings": """A photorealistic fantasy realism full-body aerial shot looking upward from below at a
supernatural figure ascending into the sky. He is mid-ascent—feet just clearing a mountain
ridge below, body rising—looking downward and outward with peaceful, sovereign confidence,
arms slightly open, a posture between surrender and authority. He is dressed in clean modern
white—a white long-sleeved shirt with the sleeves worn down and unfolded, fully and properly
buttoned and left untucked, over loose, free-cut white trousers (not tight or slim), with a
long, lightweight ivory overlayer that trails and ripples below him, its edges snapping in the
updraft; light, aerodynamic, contemporary tailoring rather than robes; his large white wings are in full
upstroke—massive, powerful, each feather under maximum tension, the translucent edges of
outermost feathers lit against the sky above, individual barbs visible in razor detail.
Above him, the sky opens into brilliant golden-white light at high altitude, breaking through
high cloud cover. Below him, glimpsed in the softly blurred background, the mountain ridge
shrinks in scale—the height of the ascension already significant. The lighting is aerial
cinematic—primary light from the sun above creating top lighting with strong subsurface
scattering on upturned face and raised hands, warm rim light on the underside of wings from
the sunlit earth below, a deep gradient sky from warm gold above to atmospheric blue-grey
at distance below. Realistic atmospheric perspective, physically accurate light scattering on
feathers, motion visible in trailing fabric. Eagle gold and deep sky blue color grading with
brilliant solar gold at the apex. Soaring, free, biblical scale.""",

    "army-of-angels": """A photorealistic fantasy realism close full-body shot of a supernatural archangel warrior
king. He is standing on a dark volcanic rock, looking directly into the camera with a calm,
powerful expression. His armor is an elegant masterpiece of polished gold and layered white
fabric with visible weaves and stitching—sculpted to a clean, modern, athletic silhouette
rather than an ancient robed one. His massive white wings are spread wide to their full span, showing individual,
highly detailed feathers. The lighting is cinematic and dramatic—a low-angle shot with strong
volumetric god rays breaking through a dark, moody sky, casting realistic shadows and bright
highlights on his face and armor. In the blurry background, a massive army of thousands of
armored angels stands in a grand mountain pass. Dark, cinematic color grading, epic biblical
scale.""",

    "receiving-the-mantle": """A photorealistic fantasy realism full-body portrait low-angle shot of a supernatural figure
at the exact moment of receiving a divine mantle of authority. He stands on a high rocky
place—a hilltop or elevated ground—both arms raised fully upward, hands open, face raised
to the sky with complete surrender and holy anticipation—the expression of someone who knows
what is coming and is choosing to receive it fully. He is dressed in understated modern
clothing—a plain stone-white long-sleeved shirt with the sleeves worn down and unfolded, fully
and properly buttoned and left untucked, and loose, free-cut dark trousers (not tight or slim),
simple and current; the ordinariness of the clothing beneath the burning mantle is
deliberate—the body about to receive it is the body of this present-day person;
large white wings are spread behind him. Descending from a brilliant point of
white-gold fire in the sky directly above him, a supernatural mantle falls—a living cloak of
divine authority, made of fire and light, deep crimson and burning gold at its edges,
trailing sparks and embers as it descends through the air. It is alive. The leading edge of
the mantle is at the point of first contact—the moment of transfer, the mantle just touching
his outstretched fingertips, the authority beginning to flow. The fire of the descending
mantle illuminates the entire scene from above, casting dramatic warm orange and gold
downlighting on his upturned face, creating strong subsurface scattering on skin. Realistic
fire physics, individual ember particles suspended in the air around the descent path. In the
blurry background, the sky shows a fiery streak where the source departed—a trail of divine
exit above. Deep twilight blue sky and warm fire color grading—the world dark, the descending
mantle the only light source. Holy, consequential scale.""",
}


# The wardrobe boundary each scene has to stay inside when a user's custom
# prompt asks for different clothing. The garment itself is theirs to choose —
# gown instead of a shirt, agbada instead of a suit — but it has to satisfy the
# rule below, so the outfit still belongs to the scene. prompt_builder injects
# the matching rule into the custom-prompt block.
SCENE_WARDROBE_RULES: dict[str, str] = {
    "walking-on-water": (
        "the outfit must be white or off-white with no other colour dominant, clean and "
        "uncluttered, and the feet stay bare. Any garment type is fine — gown, dress, kaftan, "
        "agbada, suit, shirt and trousers — as long as it is white and clean-lined; dark, "
        "heavily printed or heavily ornamented clothing is not"
    ),
    "commanding-the-storm": (
        "the outfit must be white, off-white or ivory, and must include at least one long, "
        "loose layer the gale can catch and stream sideways. Any garment type is fine as long "
        "as it is that colour and has fabric for the wind to move; dark or busily patterned "
        "clothing is not"
    ),
    "defeating-giants": (
        "the outfit must remain battle armor in white and gold. Its cut, cultural style and "
        "detailing are open to the user, but plain civilian clothing does not satisfy this "
        "scene — if they ask for something else, render it as an armored version of it"
    ),
    "silencing-the-lion": (
        "the outfit must stay in deep dark tones — black, charcoal or deep brown — with "
        "restrained gold accents, sharply cut and composed. Any garment type is fine in those "
        "tones; a dominantly white, bright, casual or scruffy outfit is not"
    ),
    "breaking-every-chain": (
        "the outfit must be simple and unadorned in white or a light neutral, and the "
        "forearms and wrists must stay bare and visible so the shattering chains read. Any "
        "plain garment is fine; armor, heavy ornamentation, or sleeves covering the wrists "
        "are not"
    ),
    "walking-through-fire": (
        "the outfit must be white or near-white and perfectly pristine inside the furnace — "
        "unburned, unscorched, no soot, no singeing, no smoke staining — whatever the garment"
    ),
    "anointed-with-oil": (
        "the outfit must be white with gold ornamentation and must read as consecrated "
        "ceremonial dress rather than casual wear. Coat, gown, robe, agbada or dress are all "
        "fine within that; everyday casual clothing is not"
    ),
    "eagle-wings": (
        "the outfit must be white or ivory, light and aerodynamic, and must include at least "
        "one loose layer that trails and ripples below in the updraft. Heavy, bulky or dark "
        "clothing is not"
    ),
    "army-of-angels": (
        "the outfit must remain battle armor in polished gold over white. Its cut and "
        "detailing are open to the user, but plain civilian clothing does not satisfy this "
        "scene — if they ask for something else, render it as an armored version of it"
    ),
    "receiving-the-mantle": (
        "the outfit must stay understated and everyday in white, stone or dark neutral tones, "
        "quiet enough that the burning mantle overhead remains the brightest thing in frame. "
        "Any simple garment is fine; armor, gold, or anything ornate and attention-grabbing "
        "is not"
    ),
}


def get_wardrobe_rule(scene_id: str) -> str:
    """The scene's wardrobe boundary, used to constrain custom prompts."""
    return SCENE_WARDROBE_RULES[scene_id]


def get_scene_ids() -> list[str]:
    """Returns all 10 active scene IDs."""
    return list(SCENE_PROMPTS.keys())


def has_scene(scene_id: str) -> bool:
    return scene_id in SCENE_PROMPTS


def get_active_scene_id(today: date | None = None) -> str:
    """Returns the one scene scheduled for the current week.

    Before launch, week 1's scene is active (so the app is testable ahead of
    time). After the last scheduled week, the final scene stays active.
    """
    if today is None:
        today = date.today()
    scene_ids = get_scene_ids()
    if today < LAUNCH_DATE:
        return scene_ids[0]
    week_index = (today - LAUNCH_DATE).days // WEEK_LENGTH_DAYS
    week_index = min(week_index, len(scene_ids) - 1)
    return scene_ids[week_index]


def get_scene_schedule() -> list[dict]:
    """Returns every scene with its scheduled week number and active date range."""
    schedule = []
    for i, scene_id in enumerate(get_scene_ids()):
        starts = LAUNCH_DATE + timedelta(days=i * WEEK_LENGTH_DAYS)
        ends = starts + timedelta(days=WEEK_LENGTH_DAYS - 1)
        schedule.append({
            "scene_id": scene_id,
            "week": i + 1,
            "starts": starts.isoformat(),
            "ends": ends.isoformat(),
        })
    return schedule
