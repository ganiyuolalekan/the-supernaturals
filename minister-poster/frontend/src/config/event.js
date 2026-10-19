// Everything event-specific the UI prints lives here. Edit this file first.
// (The poster text itself is drawn by the backend: see EVENT_DATES in backend/.env.)
export const EVENT = {
  name: 'Your Event 2027',
  dates: 'DD – DD Month YYYY',
  hashtag: '#YourEvent2027',
  handle: '@YourEvent',
  audience: 'Internal use only',
  guest: 'Guest',          // what you call the people being announced
  guests: 'Guests',
  shareTitle: (name) => `${name} — CONFIRMED | Your Event 2027`,
  shareText: (name) => `${name} is confirmed for Your Event 2027. #YourEvent2027`,
  // Two groups of poster styles. Rename them, or add a third by extending
  // GROUPS here, ministerStyles.js and backend/minister_prompts.py together.
  groups: [
    { id: 'a', label: 'GROUP A', sub: 'First kind of guest', icon: '⭐', badge: 'Group A Guest' },
    { id: 'b', label: 'GROUP B', sub: 'Second kind of guest', icon: '🎤', badge: 'Group B Guest' },
  ],
}
