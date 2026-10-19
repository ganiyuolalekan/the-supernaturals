// Poster styles shown in the picker. Each `id` must exist in
// backend/minister_prompts.py (MINISTER_PROMPTS) and, if you use the video step,
// in backend/video_client.py (_STYLE_PROMPTS).
export const GROUP_A_STYLES = [
  {
    id: 'example_a',
    name: 'Example Style A',
    subtitle: 'Who this style suits',
    description: 'One line describing the look: pose, setting, mood. Edit me.',
    mood: 'Heroic',
    icon: '⭐',
  },
]

export const GROUP_B_STYLES = [
  {
    id: 'example_b',
    name: 'Example Style B',
    subtitle: 'Who this style suits',
    description: 'One line describing the look: pose, setting, mood. Edit me.',
    mood: 'Warm',
    icon: '🎤',
  },
]
