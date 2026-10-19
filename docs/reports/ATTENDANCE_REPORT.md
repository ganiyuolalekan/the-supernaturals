# Attendance report — IGC 2026 · The Supernaturals

Aggregates computed from the event's registration sheet, which the `/attend_event` check-in pages wrote to
(see [`portrait-app/backend/attendance.py`](../../portrait-app/backend/attendance.py)). **No names, phone numbers or
other personal data are published here.** The raw aggregates are in [`data/attendance.json`](data/attendance.json).

Event: Friday 16 – Sunday 18 October 2026 · Praise Assembly Parish, Karu Site, Abuja.

## Headline numbers

| Measure | Value |
|---|---:|
| Rows on the sheet (pre-registered + walk-ins) | **774** |
| Marked as attended on at least one day | **558** (72.1%) |
| Pre-registered through the form | 434 |
| …of whom checked in | 218 (50.2%) |
| Walk-ins added at the door | 340 (all checked in) |
| First-timers among attendees | 325 (58.2%) |
| Home church (RCCG Praise Assembly) among attendees | 313 (56.1%) |
| Visitors from other churches among attendees | 245 (43.9%) |

Walk-ins are the rows whose source is "Walk-in"; they never filled the form, so their transport, area and source
fields read "Not stated" in the tables below.

## By day

| Day | Checked in | First-timers | Home church | Other churches |
|---|---:|---:|---:|---:|
| Friday | 431 | 270 | 246 | 185 |
| Saturday | 312 | 146 | 190 | 122 |
| Sunday | 3 | 3 | 1 | 2 |

Came on 1 day: **371** · 2 days: **186** · all 3 days: **1**.

**Read Sunday with care.** Only 3 Sunday check-ins were recorded. The check-in desk was not used in the
same way that day, so this reflects the records, not Sunday's real turnout.

### Check-in times (hour of day, as stamped by the app)

- Friday: 00:00 → 1, 08:00 → 1, 15:00 → 22, 16:00 → 126, 17:00 → 137, 18:00 → 118, 19:00 → 2, 23:00 → 24
- Saturday: 08:00 → 139, 09:00 → 91, 10:00 → 65, 11:00 → 2, 12:00 → 10, 13:00 → 4, 19:00 → 1
- Sunday: 08:00 → 2, 18:00 → 1

Friday's 23:00 and 00:00 entries are most likely late data entry or clock differences rather than real arrivals.

## Who came

### Age group
| Age group | On the sheet | Attended | Attended / on sheet |
|---|---:|---:|---:|
| Young Adult (18-35) | 469 | 322 | 68.7% |
| Adult (35+) | 169 | 119 | 70.4% |
| Youth (13-17) | 131 | 113 | 86.3% |
| Not stated | 5 | 4 | 80.0% |

### Gender
| Gender | On the sheet | Attended | Attended / on sheet |
|---|---:|---:|---:|
| Female | 438 | 321 | 73.3% |
| Male | 336 | 237 | 70.5% |

### Home church or visiting
| Group | On the sheet | Attended | Attended / on sheet |
|---|---:|---:|---:|
| RCCG Praise Assembly | 414 | 313 | 75.6% |
| Other organisations | 360 | 245 | 68.1% |

### Other churches present (top 8, as typed on the form)

| Church | Attendees |
|---|---:|
| Rccg | 34 |
| Palace Of Praise | 7 |
| Faith And Power | 6 |
| Rccg Power House | 6 |
| Not stated | 5 |
| Church | 4 |
| Power House | 4 |
| Dunamis | 4 |

Names are shown exactly as typed, which is why "Rccg" appears separately from "Rccg Power House".

## How people heard and got there

### How they heard about the event
| Source | On the sheet | Attended | Attended / on sheet |
|---|---:|---:|---:|
| Walk-in | 340 | 340 | 100.0% |
| Church Announcement | 267 | 146 | 54.7% |
| WhatsApp | 54 | 28 | 51.9% |
| Other | 38 | 23 | 60.5% |
| Friend or Family | 37 | 13 | 35.1% |
| Flyer | 23 | 7 | 30.4% |
| Not stated | 12 | 1 | 8.3% |
| Instagram | 3 | 0 | 0.0% |

### Where they came from
| Area | On the sheet | Attended | Attended / on sheet |
|---|---:|---:|---:|
| Not stated | 340 | 340 | 100.0% |
| Karu (already near venue) | 230 | 123 | 53.5% |
| Kurudu / Jikwoyi | 95 | 53 | 55.8% |
| Orozo / Karshi | 38 | 18 | 47.4% |
| Others | 36 | 9 | 25.0% |
| Nyanya / Mararaba | 29 | 12 | 41.4% |
| AYA / Asokoro | 6 | 3 | 50.0% |

### Used the free transport
| Transport | On the sheet | Attended | Attended / on sheet |
|---|---:|---:|---:|
| Not stated | 340 | 340 | 100.0% |
| No | 299 | 152 | 50.8% |
| Yes | 135 | 66 | 48.9% |


## Method and caveats

- Source of truth: the registration Google Sheet, read through the same code the app used (774 rows at the time of the pull).
- "Attended" means a check-in stamp exists for that day. A person counts once in the headline attended number, however many days they came.
- "Home church" is matched with a forgiving regex over what people typed, so a few misspellings may be miscounted either way.
- First-timer is the answer the door agent recorded, and is only set for people who were checked in.
