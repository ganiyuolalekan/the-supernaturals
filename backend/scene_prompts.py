"""
10 photorealistic scene prompts for The SuperNaturals 2026.

Scenes kept (per final selection):
  Miracles & Power    : walking-on-water, commanding-the-storm
  Authority & Warfare : defeating-giants, silencing-the-lion, breaking-every-chain
  Fire & Spirit       : walking-through-fire, anointed-with-oil
  Ascension & Glory   : eagle-wings, army-of-angels, receiving-the-mantle

Each prompt is sourced from supernatural_prompt_book.md with two modifications:
  1. The trailing "No text…" line is stripped (re-appended by prompt_builder).
  2. The attire paragraph follows the per-scene matrix:
       - defeating-giants, army-of-angels → white & gold battle armor
       - anointed-with-oil               → white regal robes with gold trim
       - all others (7 scenes)           → preserve original clothing from photo
     All 10 retain the "large white wings" supernatural identifier.
"""

from datetime import date, timedelta

# Campaign schedule: one scene "live" per week, in the order below, starting
# launch week. Order matches the progression: Miracles & Power -> Authority &
# Warfare -> Fire & Spirit -> Ascension & Glory (see get_scene_ids()).
LAUNCH_DATE = date(2026, 8, 10)  # Week 1 — Walking on Water
WEEK_LENGTH_DAYS = 7

SCENE_PROMPTS: dict[str, str] = {
    # ──────────────────────── MIRACLES & POWER ────────────────────────
    "walking-on-water": """A photorealistic fantasy realism full-body low-angle shot taken from just above water level,
looking up at a supernatural figure walking across the surface of a dark, churning ocean at
night. He moves forward with slow, deliberate confidence—one foot fully planted on the water,
the other mid-stride—looking directly into the camera with fearless calm authority. He wears
the clothing from the reference photo, preserved exactly—every fabric, colour, and detail of
his original attire kept intact; large white wings are folded back, individual feathers
defined. The water surface directly beneath each footstep glows with faint golden-white
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
looking upward into the heart of the storm with calm, absolute authority. He wears the
clothing from the reference photo, preserved exactly—any flowing fabric catches the violent
wind, whipping dramatically to one side, his original attire intact; massive white wings
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
standing triumphant over a defeated giant. He stands on a dark rocky outcrop, feet planted
wide in a steady, grounded stance, looking directly into the camera with quiet steel-eyed
confidence—calm after the battle, not boasting. He wears white and gold battle armor,
intricately detailed with polished gold pauldrons and layered white fabric with visible weaves;
large white wings spread fully behind him, tips nearly grazing the ground on each side. Beneath
and below him, the massive form of a fallen giant lies in deep shadow—an enormous dark figure,
the scale suggesting forty or fifty feet—the ground cracked and disturbed where it fell.
A single smooth stone, still warm with faint divine energy, rests on the ground nearby.
The lighting is backlit and dramatic—strong volumetric god rays break over his shoulders from
behind the hill at the horizon, casting long dramatic shadows forward across the fallen giant,
his silhouette blazing with rim lighting in gold. Realistic subsurface scattering on skin.
In the blurry background, a vast open valley battlefield extends to distant dark mountains.
Dark dramatic color grading with warm god-ray gold on the subject only. Epic biblical scale.""",

    "silencing-the-lion": """A photorealistic fantasy realism full-body eye-level shot of a supernatural warrior with a
lion fully submitted before him. He stands tall on dark rocky ground, feet planted at shoulder
width, right hand lowered with palm open and facing the animal in a firm, quiet stay gesture—
no drama, no exertion, effortless dominion—looking down at the lion with calm, unruffled
authority, as though this submission is not a surprise. He wears the clothing from the
reference photo, preserved exactly—every fabric, colour, and detail of his original attire
kept intact, natural and recognisable; large white wings rest naturally folded behind him,
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
with fierce, triumphant authority. He wears the clothing from the reference photo, preserved
exactly—every fabric, colour, and detail of his original attire kept intact even as chains
shatter around him; massive white wings are spread fully, every feather displaced outward from
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
not a thread of his clothing darkened. He wears the clothing from the reference photo,
preserved exactly—every fabric, colour, and detail of his original attire pristine and
untouched inside the inferno, not a fibre burned, not a thread darkened; large white wings
spread partially open, feathers unsinged, the orange firelight reflecting off each one.
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
happening to them—arms at his sides, palms open. He wears flowing white regal robes with
rich gold embroidery and trim, a garment between priest and king with detailed embellishment
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
arms slightly open, a posture between surrender and authority. He wears the clothing from
the reference photo, preserved exactly—any loose fabric trails below him as he rises, caught
by the updraft, every detail of his original attire intact; his large white wings are in full
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
fabric with visible weaves and stitching. His massive white wings show individual, highly
detailed feathers. The lighting is cinematic and dramatic—a low-angle shot with strong
volumetric god rays breaking through a dark, moody sky, casting realistic shadows and bright
highlights on his face and armor. In the blurry background, a massive army of thousands of
armored angels stands in a grand mountain pass. Dark, cinematic color grading, epic biblical
scale.""",

    "receiving-the-mantle": """A photorealistic fantasy realism full-body portrait low-angle shot of a supernatural figure
at the exact moment of receiving a divine mantle of authority. He stands on a high rocky
place—a hilltop or elevated ground—both arms raised fully upward, hands open, face raised
to the sky with complete surrender and holy anticipation—the expression of someone who knows
what is coming and is choosing to receive it fully. He wears the clothing from the reference
photo, preserved exactly—the body that is about to receive the mantle is the body of this
present-day person, every fabric and detail of his original attire intact beneath what is
descending; large white wings are spread behind him. Descending from a brilliant point of
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
