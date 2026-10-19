"""
6 minister announcement prompts for The SuperNaturals 2026.
Sourced from minister_announcement_prompt_book.md.

Categories:
  Word Ministers  : commander, throne_room, declaration
  Music Ministers : worshipper, sound_carrier, atmosphere

The IDENTITY_PREFIX must be prepended (with reference photo) when calling Gemini.
The NO_TEXT_DIRECTIVE is appended by prompt_builder.
"""

IDENTITY_PREFIX = (
    "Using the provided reference photo, generate the following portrait while keeping "
    "the person's face, skin tone, facial features, and overall identity exactly as they "
    "appear in the reference. Do not alter their face in any way.\n\n"
)

# ─────────────────────────────────────────────
# CATEGORY ONE — WORD MINISTERS
# ─────────────────────────────────────────────

PROMPT_W1_COMMANDER = """A photorealistic fantasy realism close full-body portrait of a supernatural
warrior-general of the Word, styled as an official announcement poster. He stands
on dark volcanic stone, feet planted at shoulder width, facing the camera directly
with absolute composure and steel-eyed authority — the expression of someone who
carries a command, not a performance. He wears white and gold battle armor of
extraordinary craftsmanship: polished gold pauldrons, layered white fabric with
visible weaves and gold embroidery, a flowing white cape falling behind him. His
massive white wings are spread to their full commanding span behind him, every
individual feather sharp and defined, the wing tips extending beyond the frame.

In his right hand, held vertically at his side, he carries a large two-handed
sword — the blade translucent like crystallised light with a gold hilt, radiating
a cold brilliant divine light along its full length. This is the Sword of the
Spirit. It is not raised in aggression. It is simply present, held with familiarity.

The lighting is cinematic and powerful — a low-angle shot, strong volumetric god
rays breaking through a dark, heavily dramatic sky from directly above, casting
sharp realistic shadows and brilliant highlights across his face, armor, and sword.
Strong gold rim lighting traces every edge of his silhouette. Subsurface scattering
on skin, physically accurate reflections on polished armor, individual feather
detail on wings.

The poster background behind him is deep near-black with dark charcoal storm clouds,
creating maximum contrast against his white armor and the glowing sword. In the
far blurry background, a vast army of armored angels stands at formation — thousands
of them, indistinct but present, filling the dark valley behind him.

The lower third of the image is slightly darker — a deliberate gradient to near-black
at the very bottom to create clean space for text overlay. The upper portion of the
frame has a subtle dark gradient at the top for the conference name text.

Dark dramatic cinematic color grading. Desaturated background, warm gold and white
on the subject. Epic biblical scale."""

PROMPT_W2_THRONE_ROOM = """A photorealistic fantasy realism full-body portrait of a supernatural throne room
minister, styled as an official announcement poster. He sits upright on an elevated
ancient stone seat — the posture is not passive; it is the posture of seated authority,
the authority of one who rules. He faces the camera with calm, commanding directness,
composed and certain. He wears white and gold ornate robes with the structure of
armor beneath — gold shoulder pieces over layered white fabric, the regalia of both
warrior and king. His large white wings rest behind him in a relaxed but fully present
span, feathers individually defined, wing tips curling slightly forward.

In his left hand, resting against his knee, he holds an ancient open scroll or
thick leather-bound book — the Word — partially open, with soft golden light emanating
from the open pages. The light from the book illuminates his hand and arm from below.

The lighting is dramatic and regal — warm golden overhead light as the primary source,
descending like a spotlight from a heavenly aperture above the frame, illuminating
his face with strong subsurface scattering on skin, rim lighting on his shoulders
and wing tips. The scroll's light provides a secondary warm upward fill on his face.
Physically accurate reflections on the gold armor pieces.

Behind him, the background is a dark heavenly court — immense stone columns extending
upward out of frame, warm amber torch light at great distance, the sense of enormous
scale and old authority. In the very far blurry background, angelic figures stand
at attention along the column rows.

The lower third of the image graduates to deep shadow for text overlay. The upper
third holds a dark stone texture for the conference name.

Warm gold and deep shadow cinematic color grading. Regal, consequential scale."""

PROMPT_W3_DECLARATION = """A photorealistic fantasy realism mid-body close shot of a supernatural word minister
at the moment of declaration, styled as an official announcement poster. He stands
facing the camera, right arm extended slightly forward and upward — not pointing
aggressively but declaring, the gesture of a man releasing something from his mouth
with authority. His expression is intense and focused: eyes fully open, direct into
the camera, jaw set, the face of someone in the act of releasing something powerful.
He wears white and gold armor with detailed layered fabric and gold embroidery;
his large white wings are spread fully behind him, the leading edge of each wing
angled slightly forward as though the Spirit is moving through him in this moment.

From his slightly open mouth, a visible breath of fire and light flows forward —
not literally fire on his face, but a stream of golden-white energy in the air
before him, subtle and deliberate — the visual expression of the Word going forth
as described in Jeremiah 23:29. The energy dissipates rapidly, like visible breath
on a cold morning but luminous and golden.

The lighting is dramatically cinematic — a direct low-angle shot, strong volumetric
god rays converging on him from above, as though heaven is amplifying what he
releases. Strong rim lighting in gold. The energy from his breath catches and
refracts the light. Realistic shadows, subsurface scattering on skin, individual
feather detail, physically accurate armor reflections.

Behind him, the background is a dark deep blue-black with a mountain silhouette,
the sky above cracked with distant divine light. The lower portion of the frame
drops to near-black for text. Close, intense, personal scale.

High contrast cinematic color grading — near-black background, brilliant gold and
white on the subject, the breath-light warm gold."""

# ─────────────────────────────────────────────
# CATEGORY TWO — MUSIC MINISTERS
# ─────────────────────────────────────────────

PROMPT_M1_WORSHIPPER = """A photorealistic fantasy realism full-body portrait of a supernatural worship
minister, styled as an official announcement poster. He stands facing the camera
with both arms slightly raised and open — palms upward, fingers softly spread,
the natural posture of a worshipper in the fullness of the moment — with an
expression of peaceful, open power: eyes either just closed or looking upward
with focused calm, not performing, but deeply present. He wears white and gold
flowing armor-attire, lighter than a warrior's — more fabric, less heavy plate,
the gold embroidery visible in detail with visible stitching, a garment that
moves. His massive white wings are raised high behind him in an ascending
position, each wing curving upward and outward, the feathers at full individual
detail, catching the light as though mid-movement.

Around his open hands and in the air immediately surrounding him, musical
sound waves are visible as golden light — not cartoon waves but realistic
atmospheric disturbance, like the heat shimmer above a flame but golden and
structured, rippling outward from him in visible concentric curves that catch
the surrounding light. These represent sound made visible.

The lighting is warm, ethereal, and cinematic — soft volumetric golden light
descending from above as the primary source, wrapping around him with warm
subsurface scattering on skin, gentle rim lighting on the wing edges. The sound
wave light around his hands provides secondary warm fill. No harsh shadows —
this light embraces rather than cuts.

Behind him, the background is deep celestial indigo blue — the colour of a sky
at the edge of night and dawn simultaneously — with faint stars and a soft
nebula glow visible in the distance. In the blurry far background, an enormous
choir of angelic singers fills the frame — hundreds of figures, all in white,
their mouths open in unified worship, their own soft light contributing to the
background warmth.

The lower quarter of the frame graduates to deep indigo-black for text overlay.
The top carries a dark gradient for the conference name.

Deep celestial blue and warm gold color grading — the blue of the background,
the gold of the light, the white of the wings. Ethereal, worshipful scale."""

PROMPT_M2_SOUND_CARRIER = """A photorealistic fantasy realism full-body portrait of a supernatural music
minister carrying a heavenly instrument, styled as an official announcement
poster. He stands facing the camera with quiet, focused confidence — the
expression of a craftsman who knows exactly what he carries. He holds before
him a large supernatural harp or lyre of extraordinary beauty: the frame is
polished white gold, the strings made of solidified light — each string a
thin strand of luminous gold that catches and refracts the surrounding light
like a prism, visibly vibrating as though just played. The instrument is not
small or decorative; it is large, significant, and real.

He wears white and gold flowing armor-attire — slightly more movement and
fabric than a word minister's armor, the gold embroidery detailed in patterns
that suggest music notation or sacred geometry. His large white wings are
spread fully and evenly behind him, individually feathered in sharp detail,
the wings the full frame width.

From the strings of the instrument, faint visible sound waves radiate outward
— not cartoon lines but subtle golden atmospheric disturbance, the air itself
responding to what the strings carry.

The lighting is ethereal and cinematic — a soft overhead divine light as the
primary source, the instrument's string-light providing a secondary warm glow
that illuminates his hands and lower face from below, subsurface scattering on
skin. Rim lighting on wing tips and armor edges. Physically accurate reflections
on polished instrument frame and armor.

Behind him, the background is deep cosmic blue-black with a high galaxy formation
visible — stars and soft nebula in the far distance. In the blurry background,
a grand celestial space suggests the scale of what he carries. No armies here —
the space is vast and open, as the sound fills it.

The lower portion of the frame drops to deep black for text. The image has a
more spacious, open quality than the word minister portraits.

Deep cosmic blue-black and warm gold string-light color grading. Grand, open,
sonic scale."""

PROMPT_M3_ATMOSPHERE = """A photorealistic fantasy realism mid-body close portrait of a supernatural
music minister at the moment of atmosphere shift, styled as an official
announcement poster. He stands facing the camera, arms slightly open at his
sides with palms facing forward and upward — a posture of complete openness
and release — with eyes closed and head slightly inclined, the expression of
someone in the deepest place of worship, present and powerful simultaneously.
Not passive. Not performing. Carrying something.

He wears white and gold ornate flowing attire with visible gold embroidery
detail; his large white wings are spread behind him in a soft, wide arc,
feathers individually sharp but the overall wing position relaxed — not the
commanding spread of a warrior, but the open wingspan of someone fully
surrendered. In the air around him — between his open palms, above his head,
in the space to each side — the atmosphere itself is visibly shifting: a soft
golden mist or haze with faint structured light patterns moving through it,
like the visible displacement of spiritual atmosphere, warm and luminous.
The air looks different near him than further away.

The lighting is intimate, warm, and deeply cinematic — the atmospheric golden
haze around him as the primary light source, creating an entirely self-lit
scene. No god rays from above. Instead: soft, even, warm golden illumination
emanating from within the atmospheric shift itself, wrapping every surface
with warm subsurface scattering on skin. The wings are lit by this same
golden ambient glow, feather edges softly luminous.

Behind him, the background is very dark — deep charcoal and black — with the
atmospheric golden haze fading into it, creating a strong subject-background
separation. The darkness makes the golden atmosphere around him appear to
glow brighter by contrast.

The lower third of the image is deep shadow for text. Close, personal,
atmospheric scale — this poster feels quieter and more intense than the others.

Warm golden haze against near-black cinematic color grading. Intimate,
charged, prophetic scale."""


# ─────────────────────────────────────────────
# CATEGORY ONE — WORD MINISTERS (additional)
# ─────────────────────────────────────────────

PROMPT_W4_INTERCESSOR = """A photorealistic fantasy realism full-body portrait of a supernatural intercessor
minister engaged in warfare prayer, styled as an official announcement poster. He
kneels on one knee on dark cracked ground, upper body upright, both hands clasped
and lifted before his chest — the posture of violent, contending, breakthrough
prayer, not quiet reflection. His face is raised, eyes closed, jaw set with focused
intensity, the expression of one who wrestles in the spirit and will not let go. He
wears white and gold armor, battle-worn but radiant — gold pauldrons over layered
white fabric scored from the fight. His large white wings are half-raised and tensed
behind him, feathers bristling as though charged with power.

All around him, dark chains and shadowy shackles are shattering — broken links
suspended in mid-air, dissolving into black smoke — as a vertical shaft of brilliant
white-gold light breaks down from heaven and strikes the ground where he kneels, the
visible answer descending. The breakthrough light throws his shadow long across the
cracked earth.

The lighting is fierce and cinematic — the breakthrough shaft from above is the
primary source, striking his lifted face with strong subsurface scattering on skin,
brilliant rim lighting tracing his shoulders and wing tips, the shattering chains
catching cold glints. Realistic shadows, physically accurate reflections on the
scored gold armor.

Behind him, the background is a dark, storm-torn battlefield sky — distant lightning,
the darkness visibly recoiling from the descending light, a sense of a spiritual war
being turned in this moment.

The lower third of the image graduates to near-black for text overlay. The upper
third holds dark stormlight for the conference name.

High-contrast cinematic color grading — near-black shadow, brilliant white-gold
breakthrough light. Fierce, contending, prevailing scale."""

PROMPT_W5_WATCHMAN = """A photorealistic fantasy realism full-body portrait of a supernatural watchman
minister keeping guard on a high wall, styled as an official announcement poster.
He stands at the very edge of a great ancient stone rampart, one foot forward on the
parapet, body turned three-quarters toward the camera but face alert and scanning the
distance, eyes sharp and vigilant — the posture of one who keeps watch through the
night and does not sleep. He wears white and gold sentinel armor with a long cloak
falling from one shoulder, the regalia of a guardian of the gate. His large white
wings are held high and alert behind him.

In his right hand a great golden ram's-horn shofar is raised toward his lips,
mid-breath, the first note of the alarm about to sound. From the mouth of the horn a
visible ripple of golden sound-light begins to roll outward across the valley below —
the alarm made visible.

The lighting is the cold-to-warm light of daybreak — the first gold of dawn cracking
the horizon lights his face and the front of his armor warmly, while cool night-blue
lingers on his back and wings. Strong rim lighting, subsurface scattering on skin,
physically accurate reflections on the gold horn and armor.

Behind and far below him, the background is a vast dark valley — sleeping cities as
distant points of light, the coming dawn breaking gold along the horizon line, the
boundary between night and day drawn across the frame.

The lower third of the image graduates to near-black for text overlay. The upper
third holds dark pre-dawn sky for the conference name.

Cool night-blue and breaking-dawn gold cinematic color grading. Vigilant, watchful,
resolute scale."""

PROMPT_W6_FIRE_CARRIER = """A photorealistic fantasy realism full-body portrait of a supernatural fire-carrying
minister, styled as an official announcement poster. He stands facing the camera
within a towering pillar of living fire that rises around him without consuming him —
the flames wrap his form but his white robes and skin remain unburned, as with those
who stood in the furnace. His expression is calm and unflinching amid the fire, eyes
steady and burning with reflected light. He wears white and gold armor now edged with
glowing ember-gold; his large white wings are spread, their feather tips catching and
glowing as though dipped in flame.

In his cupped hands, held forward at chest height, he carries a cluster of living
coals of fire — brilliant orange-white embers radiating heat-shimmer, a live coal
like the one that touched the prophet's lips. The coals cast strong upward firelight
across his face and forearms.

The lighting is entirely fire-lit — the pillar and the coals are the primary sources,
warm orange-gold from below and all around, strong subsurface scattering on skin,
visible heat-shimmer distortion bending the air, embers drifting upward as sparks.
Physically accurate reflections of flame on the ember-edged armor.

Behind him, the background is deep charcoal-black, the pillar of fire the only
illumination, dark smoke curling upward at the edges of the frame and swallowing the
far distance.

The lower third of the image graduates to near-black for text overlay. The upper
third holds dark rising smoke for the conference name.

Consuming-fire orange-gold against near-black cinematic color grading. Holy,
purifying, fervent scale."""

PROMPT_W7_HARVESTER = """A photorealistic fantasy realism full-body portrait of a supernatural harvester
minister in the field of the harvest, styled as an official announcement poster. He
stands facing the camera in the midst of a vast golden field that stretches to the
horizon — not literal wheat but a field of countless small points of warm light, each
one a soul ready to be gathered. His posture is purposeful and compassionate, one arm
extended out over the field in a gathering gesture, the expression of a labourer who
sees the ripeness of the harvest and moves toward it. He wears white and gold working
armor-robes, sleeves ready for labour, gold embroidery detailed across the fabric.
His large white wings are spread wide and low, sheltering, as though gathering the
field beneath them.

In his other hand he holds a sickle of light — a curved blade of translucent gold
radiance, not a weapon but a reaping tool, glowing along its edge. Where his hand
sweeps, points of light lift from the field and stream upward toward heaven like
rising sparks being gathered in.

The lighting is a warm golden-hour flood from a low sun near the horizon, casting long
shadows across the field, strong rim lighting on his silhouette, subsurface scattering
on skin, the field itself glowing from within. Physically accurate reflections on the
gold armor and the light-sickle.

Behind him, the background is an endless field of light-points beneath a warm
gold-and-amber sky at the hour of harvest, the horizon line low, a sense of a vast,
unreached expanse waiting to be brought in.

The lower third of the image graduates to deep shadow for text overlay. The upper
third holds warm harvest sky for the conference name.

Golden-hour amber and warm gold cinematic color grading. Urgent, compassionate,
abundant scale."""

# ─────────────────────────────────────────────
# CATEGORY TWO — MUSIC MINISTERS (additional)
# ─────────────────────────────────────────────

PROMPT_M4_HERALD = """A photorealistic fantasy realism full-body portrait of a supernatural herald
minister sounding a great trumpet, styled as an official announcement poster. He
stands with his body committed to the sound, a massive golden trumpet lifted in both
hands toward the heavens, mid-blast — chest and cheeks full with breath, feet braced
against the force of what he releases. His expression is triumphant and announcing,
eyes lifted. He wears white and gold herald's armor with a flowing tabard; his large
white wings are thrown fully back and high with the force of the blast.

From the bell of the trumpet, a great cone of golden sound-light erupts upward and
outward — visible concentric rings of luminous force parting the clouds above him, the
sound made visible as expanding shockwave rings of gold.

The lighting is dramatic and triumphant — the trumpet-blast light rises from the
instrument as a primary source, answered by divine light pouring down through the
clouds it has parted, both meeting on his lifted face with strong subsurface
scattering. Bold rim lighting on his wings and armor, physically accurate reflections
on the polished gold trumpet.

Behind him, the background is a dark sky being torn open by the blast — clouds parting
to reveal bright heaven beyond, distant angelic hosts turning toward the sound at the
far edges of the frame.

The lower third of the image graduates to near-black for text overlay. The upper
third holds parting-cloud light for the conference name.

Deep sky-blue-black and triumphant gold cinematic color grading. Announcing,
victorious, resounding scale."""

PROMPT_M5_DANCER = """A photorealistic fantasy realism full-body portrait of a supernatural dancing
minister in the fullness of worship, styled as an official announcement poster. He is
captured mid-motion in an exuberant dance before the Lord — one foot lifted, body
turning, arms sweeping through the air, cloak and garment hem flaring with the
movement, the pure abandon of one who dances with all his might. His face is alight
with joy, head lifted, an open expression of unrestrained celebration. He wears white
and gold flowing worship attire, lighter and looser than armor and built to move, the
gold embroidery streaming with the turn. His large white wings sweep mid-beat with the
dance.

Trailing his hands, his feet, and the hem of his garment are ribbons of golden light —
motion-trails his movement paints in the air, luminous arcs curving through the space
around him, the visible signature of worship in motion.

The lighting is warm, joyful, and festival-bright — golden light from above and around
as the primary source, the light-trails providing bright secondary fill on his face
and arms, subsurface scattering on skin, rim lighting flaring along the moving
garments and wing edges.

Behind him, the background is a warm celebratory heavenly court — soft golden bokeh of
distant lights and rejoicing figures, the sense of a great celebration underway all
around him.

The lower third of the image graduates to deep shadow for text overlay. The upper
third holds warm gold light for the conference name.

Warm celebratory gold cinematic color grading. Joyful, exuberant, unrestrained
scale."""

PROMPT_M6_KEYS_OF_LIGHT = """A photorealistic fantasy realism full-body portrait of a supernatural psalmist
minister seated at an instrument of light, styled as an official announcement poster.
He sits at a grand keyboard-instrument whose keys are made of solidified light — a
long tier of glowing white-gold keys suspended before him, the body of the instrument
fading into radiance. His hands rest on the keys mid-phrase, fingers pressing light
into sound, head bowed slightly in concentration, the expression of a craftsman lost
in the music. He wears white and gold flowing attire with detailed embroidery; his
large white wings are relaxed and spread behind the instrument.

Where his fingers press the light-keys, ripples of golden sound rise from the keyboard
and drift upward as visible luminous waves — chords made visible, spreading and
overlapping in the air above the instrument.

The lighting is intimate and cinematic — the light-keys are a strong primary source,
illuminating his hands and lower face from below with warm gold, a soft divine light
from above providing secondary fill. Subsurface scattering on skin, rim lighting on
the wing tips, physically accurate reflections of the keylight on his hands.

Behind him, the background is deep cosmic blue-black with a soft distant nebula glow,
the instrument's light the brightest thing in the frame, a sense of a vast concert
hall of the heavens opening beyond.

The lower third of the image graduates to deep black for text overlay. The upper third
holds dark cosmic space for the conference name.

Deep blue-black and warm gold keylight cinematic color grading. Intimate, masterful,
resonant scale."""

PROMPT_M7_NEW_SONG = """A photorealistic fantasy realism mid-body close portrait of a supernatural singing
minister birthing a new song, styled as an official announcement poster. He faces the
camera mid-song, mouth open in full voice, head lifted slightly, eyes closed — the
expression of one singing a fresh, spontaneous, prophetic song that has never been
sung before, fervency and discovery on his face as though catching the melody from
heaven as he releases it. He wears white and gold flowing attire with visible
embroidery; his large white wings are spread in a soft open arc, feathers lifting as
though the sound moves through them.

From his open mouth, a stream of golden light rises and unfurls upward — resolving
into flowing ribbons and drifting motes of luminous notation, a visible new song
ascending, the melody made light as it leaves him and climbs toward heaven.

The lighting is warm and cinematic — golden light from above meets the rising
song-light from his mouth, the two blending on his face with strong subsurface
scattering on skin, rim lighting tracing the wing edges. The song-light provides a
warm upward fill.

Behind him, the background is a deep warm indigo-to-black gradient with faint high
stars, the rising song-light the brightest element, a sense of an open heaven
receiving the song.

The lower third of the image graduates to deep shadow for text overlay. The upper
third holds dark indigo sky for the conference name.

Warm gold and deep indigo cinematic color grading. Fresh, prophetic, ascending
scale."""


# ─────────────────────────────────────────────
# Registry
# ─────────────────────────────────────────────

MINISTER_PROMPTS: dict[str, str] = {
    # Word
    "commander":    PROMPT_W1_COMMANDER,
    "throne_room":  PROMPT_W2_THRONE_ROOM,
    "declaration":  PROMPT_W3_DECLARATION,
    "intercessor":  PROMPT_W4_INTERCESSOR,
    "watchman":     PROMPT_W5_WATCHMAN,
    "fire_carrier": PROMPT_W6_FIRE_CARRIER,
    "harvester":    PROMPT_W7_HARVESTER,
    # Music
    "worshipper":    PROMPT_M1_WORSHIPPER,
    "sound_carrier": PROMPT_M2_SOUND_CARRIER,
    "atmosphere":    PROMPT_M3_ATMOSPHERE,
    "herald":        PROMPT_M4_HERALD,
    "dancer":        PROMPT_M5_DANCER,
    "keys_of_light": PROMPT_M6_KEYS_OF_LIGHT,
    "new_song":      PROMPT_M7_NEW_SONG,
}

WORD_STYLES  = ["commander", "throne_room", "declaration",
                "intercessor", "watchman", "fire_carrier", "harvester"]
MUSIC_STYLES = ["worshipper", "sound_carrier", "atmosphere",
                "herald", "dancer", "keys_of_light", "new_song"]

# Per-style overlay config (stamp rotation, stamp color, text alignment)
STYLE_OVERLAY_CONFIG: dict[str, dict] = {
    "commander":    {"rotation": -8,  "stamp_color": "white", "align": "left"},
    "throne_room":  {"rotation": +6,  "stamp_color": "white", "align": "right"},
    "declaration":  {"rotation": 0,   "stamp_color": "gold",  "align": "left"},
    "intercessor":  {"rotation": -6,  "stamp_color": "gold",  "align": "left"},
    "watchman":     {"rotation": +5,  "stamp_color": "white", "align": "right"},
    "fire_carrier": {"rotation": 0,   "stamp_color": "gold",  "align": "left"},
    "harvester":    {"rotation": -5,  "stamp_color": "white", "align": "left"},
    "worshipper":   {"rotation": -6,  "stamp_color": "white", "align": "left"},
    "sound_carrier":{"rotation": +8,  "stamp_color": "gold",  "align": "right"},
    "atmosphere":   {"rotation": 0,   "stamp_color": "white", "align": "left"},
    "herald":       {"rotation": +7,  "stamp_color": "gold",  "align": "right"},
    "dancer":       {"rotation": -7,  "stamp_color": "white", "align": "left"},
    "keys_of_light":{"rotation": +6,  "stamp_color": "gold",  "align": "right"},
    "new_song":     {"rotation": 0,   "stamp_color": "white", "align": "left"},
}


def has_style(style_id: str) -> bool:
    return style_id in MINISTER_PROMPTS


def get_category(style_id: str) -> str:
    if style_id in WORD_STYLES:
        return "word"
    if style_id in MUSIC_STYLES:
        return "music"
    raise ValueError(f"Unknown style: {style_id!r}")
