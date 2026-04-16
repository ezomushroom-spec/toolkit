export type CanonicalWildcardGroup = {
  id: string
  token: string
  label: string
  description: string
  sourceFileName: string
  sourceSize: number
  totalOptions: number
  options: string[]
}

export type SkippedCanonicalWildcardSummary = {
  reason: string
  count: number
}

export const canonicalWildcardsSource = "E:\\自作アプリ集\\新しいフォルダー (2)\\data\\wildcards" as const

export const canonicalWildcards = [
  {
    "id": "school komono",
    "token": "__school komono__",
    "label": "school komono",
    "description": "",
    "sourceFileName": "school komono.txt",
    "sourceSize": 37,
    "totalOptions": 3,
    "options": [
      "school chair",
      "school desk",
      "school bag"
    ]
  },
  {
    "id": "tipo_location",
    "token": "__tipo_location__",
    "label": "tipo_location",
    "description": "https://danbooru.donmai.us/wiki_pages/tag_group%3Alocations",
    "sourceFileName": "tipo_location.txt",
    "sourceSize": 2457,
    "totalOptions": 229,
    "options": [
      "indoors",
      "ballroom",
      "bathroom",
      "bathtub",
      "toilet stall",
      "shower",
      "bedroom",
      "hotel room",
      "messy room",
      "otaku room",
      "cafeteria",
      "changing room",
      "classroom",
      "clubroom",
      "conservatory",
      "courtroom",
      "dining room",
      "dressing room",
      "dungeon",
      "prison cell",
      "fitting room",
      "gym",
      "locker room",
      "gym storeroom",
      "infirmary",
      "kitchen",
      "laboratory",
      "library",
      "living room",
      "office",
      "cubicle",
      "pool",
      "stage",
      "staff room",
      "storage room",
      "armory",
      "closet",
      "workshop",
      "outdoors",
      "beach",
      "shore",
      "canyon",
      "cave",
      "cliff",
      "desert",
      "oasis",
      "forest",
      "bamboo forest",
      "glacier",
      "hill",
      "island",
      "floating island",
      "jungle",
      "meadow",
      "mountain",
      "volcano",
      "nature",
      "park",
      "playground",
      "parking lot",
      "plain",
      "savannah",
      "wetland",
      "water",
      "geyser",
      "lake",
      "ocean",
      "seafloor",
      "pond",
      "river",
      "stream",
      "waterfall",
      "wasteland",
      "airfield",
      "runway",
      "amusement park",
      "carousel",
      "ferris wheel",
      "roller coaster",
      "aqueduct"
    ]
  },
  {
    "id": "view",
    "token": "__view__",
    "label": "view",
    "description": "",
    "sourceFileName": "view.txt",
    "sourceSize": 46,
    "totalOptions": 4,
    "options": [
      "from side",
      "from above",
      "from below",
      "from behind"
    ]
  }
] satisfies CanonicalWildcardGroup[]

export const skippedCanonicalWildcards = [
  {
    "reason": "汎用候補の確認が未完了のため初回除外",
    "count": 15
  },
  {
    "reason": "txt以外のため初回除外",
    "count": 1
  }
] satisfies SkippedCanonicalWildcardSummary[]
