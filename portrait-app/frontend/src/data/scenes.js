// Scene cards shown in the picker. Each `id` must match a key in
// backend/scene_prompts.py (SCENE_PROMPTS). Order = schedule order: `week` is
// the week the scene goes live (week 1 starts on LAUNCH_DATE in backend/.env).
export const SCENE_CATEGORIES = [
  {
    id: 'category-one',
    name: 'Category One',
    icon: '✦',
    scenes: [
      {
        id: 'example-scene-one',
        title: 'Example Scene One',
        description:
          'One or two sentences telling people what they will see: the setting, the action, the mood.',
        wardrobe: 'Crisp modern all-white, white sneakers.',
        caption: 'Optional line under the title',
        week: 1,
      },
      {
        id: 'example-scene-two',
        title: 'Example Scene Two',
        description:
          'Keep it short. People choose a scene from this card, so lead with the feeling.',
        wardrobe: 'Stone linen shirt, dark trousers.',
        caption: 'Optional line under the title',
        week: 2,
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
