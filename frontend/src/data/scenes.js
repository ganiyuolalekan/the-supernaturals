export const SCENE_CATEGORIES = [
  {
    id: "miracles",
    name: "Miracles & Power",
    icon: "⚡",
    scenes: [
      {
        id: "walking-on-water",
        title: "Walking on Water",
        description:
          "Standing on a glowing, calm sea at night, divine light reflecting on the surface, golden ripples radiating outward beneath every step.",
        wardrobe:
          "Crisp modern all-white — rolled-sleeve shirt, white trousers, barefoot on the water.",
        scripture: "Matthew 14:29",
        week: 1,
      },
      {
        id: "commanding-the-storm",
        title: "Commanding the Storm",
        description:
          "Dark storm clouds splitting apart, lightning bending away at your command, violent winds visibly calming — divine stillness at the center.",
        wardrobe:
          "Off-white shirt under a long ivory storm coat streaming in the gale.",
        scripture: "Mark 4:39",
        week: 2,
      },
    ],
  },
  {
    id: "authority",
    name: "Authority & Warfare",
    icon: "🗡️",
    scenes: [
      {
        id: "defeating-giants",
        title: "Defeating Giants",
        description:
          "Standing tall and victorious over a massive fallen shadow, a stone suspended mid-air, the ground cracked beneath the fallen form.",
        wardrobe:
          "White and gold battle armour, modern athletic cut.",
        scripture: "1 Samuel 17",
        week: 3,
      },
      {
        id: "silencing-the-lion",
        title: "Silencing the Roaring Lion",
        description:
          "A massive supernatural lion crouching low and subdued at your feet, head bowed, standing calm and commanding above it.",
        wardrobe:
          "Sharp black modern tailoring over a crisp white shirt, thin gold detail.",
        scripture: "1 Peter 5:8",
        week: 4,
      },
      {
        id: "breaking-every-chain",
        title: "Breaking Every Chain",
        description:
          "Heavy iron chains shattered, fragments flying outward with explosive divine force, golden light erupting from every breaking point.",
        wardrobe:
          "Plain white tee and dark trousers — bare forearms where the chains break.",
        scripture: "Acts 16:26",
        week: 5,
      },
    ],
  },
  {
    id: "fire",
    name: "Fire & Spirit",
    icon: "🔥",
    scenes: [
      {
        id: "walking-through-fire",
        title: "Walking Through Fire",
        description:
          "Standing completely unscathed inside a roaring furnace, a glowing fourth figure of divine light walking beside you in the flames.",
        wardrobe:
          "Pristine white shirt and trousers, spotless inside the furnace.",
        scripture: "Daniel 3:25",
        week: 6,
      },
      {
        id: "anointed-with-oil",
        title: "Anointed with Oil",
        description:
          "Golden light pouring from above like a river of oil over your crown, cascading down in luminous streams, saturating the atmosphere.",
        wardrobe:
          "Modern white ceremonial coat with fine gold embroidery.",
        scripture: "Psalm 23:5",
        week: 7,
      },
    ],
  },
  {
    id: "ascension",
    name: "Ascension & Glory",
    icon: "🦅",
    scenes: [
      {
        id: "eagle-wings",
        title: "Ascending on Eagle's Wings",
        description:
          "Massive, majestic eagle wings fully extended, suspended above the ground in divine lift, wind and light streaming past.",
        wardrobe:
          "Clean white with a lightweight ivory overlayer trailing in the updraft.",
        scripture: "Isaiah 40:31",
        week: 8,
      },
      {
        id: "army-of-angels",
        title: "Guarded by an Army of Angels",
        description:
          "Rows upon rows of towering warrior angels in full armour stretching behind you into the horizon — an uncountable heavenly host.",
        wardrobe:
          "White and gold battle armour, polished and modern.",
        scripture: "2 Kings 6:17",
        week: 9,
      },
      {
        id: "receiving-the-mantle",
        title: "Receiving the Mantle",
        description:
          "A fiery, glowing prophetic cloak descending from the sky onto your shoulders in a blaze of light, the weight of authority settling visibly.",
        wardrobe:
          "Understated stone-white shirt and dark trousers — everyday, present-day.",
        scripture: "2 Kings 2:13",
        week: 10,
      },
    ],
  },
]

export function getAllScenes() {
  return SCENE_CATEGORIES.flatMap((c) => c.scenes)
}

export function findScene(id) {
  return getAllScenes().find((s) => s.id === id) || null
}
