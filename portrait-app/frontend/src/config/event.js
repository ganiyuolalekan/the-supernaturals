// Everything event-specific that the UI prints lives here. Edit this file first,
// then replace the images in public/ and the scenes in src/data/scenes.js.
export const EVENT = {
  name: 'Your Event 2027',
  kicker: 'Your Event',                 // small label above headings
  titleLines: ['Be Part', 'Of It'],     // landing page headline, one entry per line
  quote: null,                          // e.g. { text: 'A line you like.', cite: 'Someone' }
  tagline: ['Ready to join us?', 'Show the world.'],
  intro: 'Upload your photo. Get your portrait. Share it.',
  generateLabel: 'Generate My Image',
  hashtag: '#YourEvent',
  handle: '@YourEvent',
  // Shown after generation. Leave a URL empty ('') to hide that button.
  registerUrl: 'https://example.com/register',
  instagramUrl: 'https://www.instagram.com/yourevent/',
  aboutUrl: 'https://example.com',
  shareHeadline: "✨ I'm part of Your Event 2027",
  // Attendance pages: the group you want counted separately as "home".
  homeOrg: 'Home Organisation',
  downloadPrefix: 'portrait',           // downloaded file name: <prefix>-<name>.jpg
  sessionKey: 'event_session',
  // Public assets: swap the files, keep the names.
  logo: '/logo.png',                    // favicon + brand mark
  watermark: '/logo_stamp.png',         // stamped on every download, top-right
}
