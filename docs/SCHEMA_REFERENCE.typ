// ============================================================================
// RADIOCALL SCHEMA REFERENCE
// A comprehensive guide to the data model and grading system
// ============================================================================

#import "@preview/cetz:0.3.2": canvas, draw

// ============================================================================
// THEME & CONFIGURATION
// ============================================================================

#let primary = rgb("#2563eb")      // Blue - primary actions, links
#let secondary = rgb("#7c3aed")    // Purple - reference data
#let success = rgb("#059669")      // Green - success states
#let warning = rgb("#d97706")      // Amber - warnings, weights
#let danger = rgb("#dc2626")       // Red - critical elements
#let neutral = rgb("#475569")      // Slate - neutral text

#let bg-light = rgb("#f8fafc")
#let bg-code = rgb("#1e293b")
#let border-light = rgb("#e2e8f0")

// ============================================================================
// DOCUMENT SETUP
// ============================================================================

#set document(title: "Radiocall Schema Reference", author: "Aevoli")
#set page(
  margin: (x: 2.5cm, y: 2cm),
  numbering: "1 / 1",
  number-align: right,
  header: context {
    if counter(page).get().first() > 1 [
      #set text(size: 9pt, fill: neutral)
      #grid(
        columns: (1fr, 1fr),
        align(left)[Radiocall Schema Reference],
        align(right)[Aevoli CMS]
      )
      #v(-0.5em)
      #line(length: 100%, stroke: 0.5pt + border-light)
    ]
  }
)

#set text(size: 10pt, fill: rgb("#1e293b"))
#set par(justify: true, leading: 0.65em)
#set heading(numbering: none)

// Heading styles
#show heading.where(level: 1): it => {
  v(1.5em)
  text(size: 18pt, weight: "bold", fill: primary)[#it.body]
  v(0.3em)
  line(length: 100%, stroke: 2pt + primary)
  v(0.8em)
}

#show heading.where(level: 2): it => {
  v(1.2em)
  text(size: 14pt, weight: "bold", fill: neutral)[#it.body]
  v(0.5em)
}

#show heading.where(level: 3): it => {
  v(0.8em)
  text(size: 11pt, weight: "bold", fill: neutral)[#it.body]
  v(0.3em)
}

// Code block styling
#show raw.where(block: true): it => {
  set text(size: 9pt)
  block(
    width: 100%,
    fill: bg-code,
    inset: 12pt,
    radius: 6pt,
  )[#text(fill: rgb("#e2e8f0"))[#it]]
}

#show raw.where(block: false): it => {
  box(
    fill: bg-light,
    inset: (x: 4pt, y: 2pt),
    radius: 3pt,
  )[#text(size: 9pt, fill: danger)[#it]]
}

// ============================================================================
// CUSTOM COMPONENTS
// ============================================================================

// Entity card for schema documentation
#let entity(name, color: primary, icon: "●", fields) = {
  block(
    width: 100%,
    stroke: 1.5pt + color,
    radius: 8pt,
    clip: true,
  )[
    #block(
      width: 100%,
      fill: color,
      inset: 10pt,
    )[
      #text(fill: white, weight: "bold", size: 11pt)[#icon #name]
    ]
    #block(
      width: 100%,
      fill: white,
      inset: 10pt,
    )[
      #set text(size: 9pt)
      #fields
    ]
  ]
}

// Callout box for important information
#let callout(title, body, color: primary, icon: "ℹ") = {
  block(
    width: 100%,
    fill: color.lighten(90%),
    stroke: (left: 3pt + color),
    inset: 12pt,
    radius: (right: 6pt),
  )[
    #text(weight: "bold", fill: color)[#icon #title]
    #v(0.3em)
    #body
  ]
}

// Relation arrow component
#let relation(from, to, label, type: "M:1") = {
  grid(
    columns: (1fr, auto, 1fr),
    align: center + horizon,
    gutter: 8pt,
    text(weight: "medium")[#from],
    box(
      fill: bg-light,
      inset: (x: 8pt, y: 4pt),
      radius: 4pt,
    )[
      #text(size: 8pt, fill: neutral)[#type]
      #h(4pt)
      #text(size: 10pt)[→]
      #h(4pt)
      #text(size: 8pt, fill: neutral)[#label]
    ],
    text(weight: "medium")[#to],
  )
}

// Difficulty badge
#let difficulty-badge(level) = {
  let colors = (
    "super_easy": success,
    "easy": rgb("#22c55e"),
    "medium": warning,
    "hard": danger,
  )
  let color = colors.at(level, default: neutral)
  box(
    fill: color.lighten(80%),
    stroke: 1pt + color,
    inset: (x: 8pt, y: 3pt),
    radius: 12pt,
  )[#text(size: 8pt, fill: color, weight: "bold")[#upper(level.replace("_", " "))]]
}

// Weight indicator (visual bar)
#let weight-bar(value, critical: false) = {
  let color = if critical { danger } else { warning }
  stack(
    dir: ltr,
    spacing: 6pt,
    box(
      width: 60pt,
      height: 8pt,
      fill: border-light,
      radius: 4pt,
    )[
      #box(
        width: 60pt * value,
        height: 8pt,
        fill: color,
        radius: 4pt,
      )
    ],
    text(size: 8pt, fill: neutral)[#calc.round(value, digits: 1)],
  )
}

// ============================================================================
// TITLE PAGE
// ============================================================================

#v(3cm)

#align(center)[
  #block(
    width: 80%,
    inset: 2em,
  )[
    #text(size: 36pt, weight: "bold", fill: primary)[Radiocall]
    #v(-0.3em)
    #text(size: 36pt, weight: "bold", fill: neutral)[Schema Reference]
    
    #v(1.5em)
    
    #text(size: 14pt, fill: neutral)[
      Data Model & Grading System Documentation
    ]
    
    #v(2em)
    
    #line(length: 40%, stroke: 2pt + border-light)
    
    #v(2em)
    
    #grid(
      columns: 3,
      gutter: 2em,
      align: center,
      [
        #text(size: 24pt, weight: "bold", fill: primary)[8]
        #v(-0.5em)
        #text(size: 10pt, fill: neutral)[Collections]
      ],
      [
        #text(size: 24pt, weight: "bold", fill: secondary)[9]
        #v(-0.5em)
        #text(size: 10pt, fill: neutral)[Relations]
      ],
      [
        #text(size: 24pt, weight: "bold", fill: success)[500]
        #v(-0.5em)
        #text(size: 10pt, fill: neutral)[Radiocalls]
      ],
    )
  ]
]

#v(1fr)

#align(center)[
  #text(fill: neutral)[Aevoli Training Platform]
  #v(0.3em)
  #text(size: 9pt, fill: neutral.lighten(30%))[Version 1.0 · January 2026]
]

#pagebreak()

// ============================================================================
// TABLE OF CONTENTS
// ============================================================================

#outline(
  title: [Contents],
  indent: 1.5em,
  depth: 2,
)

#pagebreak()

// ============================================================================
// SECTION 1: CONCEPTUAL OVERVIEW
// ============================================================================

= Conceptual Overview

The radiocall system enables structured practice of ATC readback skills. Understanding *why* the data is structured this way is key to using it effectively.

== The Core Problem

When a pilot receives an ATC instruction, they must read back critical elements accurately. Grading this requires:

#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 1em,
  callout("Decomposition", [Break transmission into individual instructions], color: primary, icon: "①"),
  callout("Classification", [Know which elements are critical], color: secondary, icon: "②"),
  callout("Weighting", [Score based on severity], color: warning, icon: "③"),
)

#v(1em)

== The Solution: Hierarchical Data

#callout(
  "Key Insight",
  [A single transmission contains multiple instructions. Each instruction has a *type* that determines its grading weight. This hierarchy enables granular, fair scoring.],
  color: success,
  icon: "💡"
)

#v(1em)

#align(center)[
  #canvas(length: 1cm, {
    import draw: *
    
    // Main radiocall box
    rect((-4, 0), (4, 2), fill: primary.lighten(90%), stroke: primary, radius: 0.2)
    content((0, 1), text(weight: "bold", fill: primary)[radiocall])
    content((0, 0.3), text(size: 8pt, fill: neutral)["Lufthansa 4AB, climb FL350, turn left heading 270"])
    
    // Arrow down
    line((0, 0), (0, -0.5), stroke: 1.5pt + neutral, mark: (end: ">"))
    
    // Instructions
    rect((-5.5, -2.5), (-2, -1), fill: warning.lighten(85%), stroke: warning, radius: 0.2)
    content((-3.75, -1.5), text(size: 9pt, weight: "bold", fill: warning)[Instruction 1])
    content((-3.75, -2.1), text(size: 8pt)["climb FL350"])
    
    rect((-1.5, -2.5), (1.5, -1), fill: warning.lighten(85%), stroke: warning, radius: 0.2)
    content((0, -1.5), text(size: 9pt, weight: "bold", fill: warning)[Instruction 2])
    content((0, -2.1), text(size: 8pt)["left heading 270"])
    
    // Arrow to type
    line((-3.75, -2.5), (-3.75, -3), stroke: 1pt + neutral, mark: (end: ">"))
    line((0, -2.5), (0, -3), stroke: 1pt + neutral, mark: (end: ">"))
    
    // Types
    rect((-5, -4.2), (-2.5, -3.2), fill: secondary.lighten(85%), stroke: secondary, radius: 0.2)
    content((-3.75, -3.7), text(size: 8pt, fill: secondary)[ALTITUDE])
    
    rect((-1, -4.2), (1, -3.2), fill: secondary.lighten(85%), stroke: secondary, radius: 0.2)
    content((0, -3.7), text(size: 8pt, fill: secondary)[HEADING])
    
    // Weights
    content((-3.75, -4.8), text(size: 8pt, fill: danger)[weight: 1.0 ⚠])
    content((0, -4.8), text(size: 8pt, fill: warning)[weight: 0.8])
  })
]

#v(0.5em)
#align(center)[
  #text(size: 9pt, fill: neutral)[Figure 1: Hierarchical decomposition of a transmission]
]

#pagebreak()

// ============================================================================
// SECTION 2: ENTITY REFERENCE
// ============================================================================

= Entity Reference

== Reference Data #text(size: 10pt, fill: neutral, weight: "regular")[(populated once, used by all radiocalls)]

These collections define the "vocabulary" of the system.

#v(0.5em)

#grid(
  columns: (1fr, 1fr),
  gutter: 1em,
  
  entity("instruction_type", color: secondary, icon: "◆", [
    #table(
      columns: (auto, 1fr),
      stroke: none,
      inset: 4pt,
      [`code`], [Unique identifier (e.g., `CLIMB`, `DESCEND`)],
      [`category`], [Grouping: altitude, heading, speed...],
      [`is_critical`], [Must be read back correctly?],
      [`grading_weight`], [0.0–1.0 scoring multiplier],
    )
  ]),
  
  entity("callsign_format", color: secondary, icon: "◆", [
    #table(
      columns: (auto, 1fr),
      stroke: none,
      inset: 4pt,
      [`airline_code`], [ICAO code (e.g., `DLH`)],
      [`airline_callsign`], [Spoken name (e.g., `Lufthansa`)],
      [`difficulty`], [Complexity level],
      [`phonetic_template`], [How to speak the callsign],
    )
  ]),
)

#v(1em)

== Core Data #text(size: 10pt, fill: neutral, weight: "regular")[(generated content)]

#v(0.5em)

#entity("radiocall", color: primary, icon: "●", [
  #grid(
    columns: (1fr, 1fr),
    gutter: 1em,
    [
      *Identification*
      #table(
        columns: (auto, 1fr),
        stroke: none,
        inset: 3pt,
        [`aircraft_callsign`], [e.g., "DLH4AB"],
        [`callsign_phonetic`], [e.g., "Lufthansa 4 Alpha Bravo"],
        [`airport`], [→ linked airport],
      )
    ],
    [
      *Classification*
      #table(
        columns: (auto, 1fr),
        stroke: none,
        inset: 3pt,
        [`category`], [ground, departure, enroute...],
        [`difficulty`], [super_easy → hard],
        [`flight_phase`], [taxi, takeoff, cruise...],
      )
    ],
  )
  #v(0.5em)
  *Content*
  #table(
    columns: (auto, 1fr),
    stroke: none,
    inset: 3pt,
    [`full_transmission`], [Complete ATC message as spoken],
    [`expected_readback`], [What pilot should say back],
    [`critical_elements`], [JSON array of gradable elements],
  )
])

#v(1em)

#grid(
  columns: (1fr, 1fr),
  gutter: 1em,
  
  entity("radiocall_instruction", color: warning, icon: "▸", [
    Links to parent `radiocall` and `instruction_type`
    #table(
      columns: (auto, 1fr),
      stroke: none,
      inset: 3pt,
      [`sequence`], [Order in transmission (1, 2, 3...)],
      [`raw_value`], [The actual value (e.g., "FL350")],
      [`readback_text`], [Expected spoken readback],
    )
  ]),
  
  entity("acceptable_variation", color: success, icon: "✓", [
    Alternative correct readbacks
    #table(
      columns: (auto, 1fr),
      stroke: none,
      inset: 3pt,
      [`radiocall`], [→ parent radiocall],
      [`variation_text`], [Alternative phrasing],
      [`notes`], [When this is acceptable],
    )
  ]),
)

#v(1em)

#entity("common_error", color: danger, icon: "✗", [
  Typical mistakes for targeted feedback
  #grid(
    columns: (1fr, 1fr),
    gutter: 1em,
    [
      #table(
        columns: (auto, 1fr),
        stroke: none,
        inset: 3pt,
        [`error_code`], [e.g., `WRONG_ALTITUDE`],
        [`severity`], [critical, major, minor],
      )
    ],
    [
      #table(
        columns: (auto, 1fr),
        stroke: none,
        inset: 3pt,
        [`example`], [What users might say wrong],
        [`feedback_text`], [Constructive feedback],
      )
    ],
  )
])

#pagebreak()

// ============================================================================
// SECTION 3: RELATIONSHIPS
// ============================================================================

= Relationships

== Visual Schema

#align(center)[
  #canvas(length: 0.9cm, {
    import draw: *
    
    // Airport (top center)
    rect((3, 8), (7, 9.5), fill: success.lighten(85%), stroke: 1.5pt + success, radius: 0.3)
    content((5, 8.75), text(weight: "bold", size: 10pt, fill: success)[airport])
    
    // radiocall (center)
    rect((2.5, 4), (7.5, 6), fill: primary.lighten(85%), stroke: 2pt + primary, radius: 0.3)
    content((5, 5.3), text(weight: "bold", size: 11pt, fill: primary)[radiocall])
    content((5, 4.6), text(size: 8pt, fill: neutral)[central entity])
    
    // instruction_type (left)
    rect((-2, 0), (2, 1.5), fill: secondary.lighten(85%), stroke: 1.5pt + secondary, radius: 0.3)
    content((0, 0.75), text(weight: "bold", size: 10pt, fill: secondary)[instruction_type])
    
    // radiocall_instruction (center bottom)
    rect((3, 0), (7, 1.5), fill: warning.lighten(85%), stroke: 1.5pt + warning, radius: 0.3)
    content((5, 0.75), text(weight: "bold", size: 10pt, fill: warning)[radiocall_instruction])
    
    // acceptable_variation (right)
    rect((8, 3), (12, 4.5), fill: success.lighten(85%), stroke: 1.5pt + success, radius: 0.3)
    content((10, 3.75), text(weight: "bold", size: 9pt, fill: success)[acceptable_variation])
    
    // common_error (right bottom)
    rect((8, 5.5), (12, 7), fill: danger.lighten(85%), stroke: 1.5pt + danger, radius: 0.3)
    content((10, 6.25), text(weight: "bold", size: 10pt, fill: danger)[common_error])
    
    // radiocall_set (left top)
    rect((-2, 6), (2, 7.5), fill: neutral.lighten(70%), stroke: 1.5pt + neutral, radius: 0.3)
    content((0, 6.75), text(weight: "bold", size: 10pt, fill: neutral)[radiocall_set])
    
    // radiocall_set_items (left middle)  
    rect((-2, 3), (2, 4.5), fill: neutral.lighten(70%), stroke: 1.5pt + neutral, radius: 0.3)
    content((0, 3.75), text(weight: "bold", size: 9pt, fill: neutral)[radiocall_set_items])
    
    // Connections
    // airport -> radiocall
    line((5, 8), (5, 6), stroke: 1pt + success, mark: (end: ">"))
    content((5.8, 7), text(size: 7pt, fill: success)[M:1])
    
    // airport -> radiocall_set
    line((3, 8.5), (2, 7.5), stroke: 1pt + success, mark: (end: ">"))
    
    // radiocall -> radiocall_instruction
    line((5, 4), (5, 1.5), stroke: 1pt + warning, mark: (end: ">"))
    content((5.8, 2.75), text(size: 7pt, fill: warning)[1:N])
    
    // radiocall_instruction -> instruction_type
    line((3, 0.75), (2, 0.75), stroke: 1pt + secondary, mark: (end: ">"))
    content((2.5, 1.2), text(size: 7pt, fill: secondary)[M:1])
    
    // radiocall -> acceptable_variation
    line((7.5, 5), (8, 4.2), stroke: 1pt + success, mark: (end: ">"))
    content((8.2, 4.8), text(size: 7pt, fill: success)[1:N])
    
    // radiocall -> common_error
    line((7.5, 5.5), (8, 6), stroke: 1pt + danger, mark: (end: ">"))
    content((8.2, 5.5), text(size: 7pt, fill: danger)[1:N])
    
    // radiocall_set -> radiocall_set_items
    line((0, 6), (0, 4.5), stroke: 1pt + neutral, mark: (end: ">"))
    
    // radiocall_set_items -> radiocall
    line((2, 3.75), (2.5, 4.5), stroke: 1pt + primary, mark: (end: ">"))
  })
]

#v(1em)

== Relationship Table

#table(
  columns: (2fr, auto, 2fr, 3fr),
  stroke: 0.5pt + border-light,
  inset: 8pt,
  fill: (_, row) => if row == 0 { bg-light } else { white },
  
  [*From*], [*Type*], [*To*], [*Purpose*],
  
  [`radiocall`], [M:1], [`airport`], [Where the transmission occurs],
  [`radiocall_instruction`], [M:1], [`radiocall`], [Parent transmission (ordered by sequence)],
  [`radiocall_instruction`], [M:1], [`instruction_type`], [Classification for grading weight],
  [`acceptable_variation`], [M:1], [`radiocall`], [Alternative correct answers],
  [`common_error`], [M:1], [`radiocall`], [Expected mistakes for feedback],
  [`radiocall_set`], [M:1], [`airport`], [Airport-specific practice sets],
  [`radiocall_set_items`], [M:1], [`radiocall_set`], [Parent set],
  [`radiocall_set_items`], [M:1], [`radiocall`], [Member radiocall (ordered by sequence)],
)

#pagebreak()

// ============================================================================
// SECTION 4: GRADING SYSTEM
// ============================================================================

= Grading System

The grading system is designed to be *fair*, *educational*, and *realistic*.

== Critical Elements

Each radiocall stores a `critical_elements` JSON array. This is the "answer key" for grading:

```json
{
  "critical_elements": [
    {"type": "callsign", "value": "DLH4AB", "display": "Lufthansa 4AB", "weight": 1.0},
    {"type": "altitude", "value": "FL350", "display": "flight level 350", "weight": 1.0},
    {"type": "heading", "value": "270", "display": "heading 270", "weight": 0.8}
  ]
}
```

#callout(
  "Grading Algorithm",
  [
    For each critical element, check if it appears in the user's readback. \
    Score = Σ(matched elements × weight) / Σ(all weights)
  ],
  color: primary,
  icon: "📊"
)

#v(1em)

== Instruction Type Weights

Weights reflect real-world consequences of errors:

#v(0.5em)

#table(
  columns: (2fr, auto, auto, 3fr),
  stroke: 0.5pt + border-light,
  inset: 8pt,
  fill: (_, row) => if row == 0 { bg-light } else { white },
  
  [*Instruction Type*], [*Weight*], [*Critical?*], [*Rationale*],
  
  [Runway Assignment], [#weight-bar(1.0, critical: true)], [#text(fill: danger)[✓]], [Wrong runway = potential collision],
  [Altitude / Flight Level], [#weight-bar(1.0, critical: true)], [#text(fill: danger)[✓]], [Altitude busts cause separation loss],
  [Heading], [#weight-bar(0.8, critical: true)], [#text(fill: danger)[✓]], [Heading deviations affect traffic flow],
  [Frequency], [#weight-bar(0.7, critical: true)], [#text(fill: danger)[✓]], [Wrong frequency = lost communication],
  [Speed], [#weight-bar(0.6)], [—], [Usually has margin for correction],
  [Squawk Code], [#weight-bar(0.5)], [—], [Incorrect but ATC will notice],
  [QNH / Altimeter], [#weight-bar(0.4)], [—], [Can be corrected before departure],
  [Taxi Instructions], [#weight-bar(0.6)], [—], [Ground speed allows correction],
)

#v(1em)

== Difficulty Tiers

#grid(
  columns: 4,
  gutter: 0.8em,
  
  block(
    width: 100%,
    stroke: 1pt + success,
    radius: 8pt,
    inset: 10pt,
    fill: success.lighten(95%),
  )[
    #align(center)[#difficulty-badge("super_easy")]
    #v(0.5em)
    #text(size: 9pt)[
      - 1 instruction
      - Common callsigns
      - Clear phraseology
      - Standard situations
    ]
  ],
  
  block(
    width: 100%,
    stroke: 1pt + rgb("#22c55e"),
    radius: 8pt,
    inset: 10pt,
    fill: rgb("#22c55e").lighten(95%),
  )[
    #align(center)[#difficulty-badge("easy")]
    #v(0.5em)
    #text(size: 9pt)[
      - 1–2 instructions
      - Standard phraseology
      - No conditionals
      - Common airports
    ]
  ],
  
  block(
    width: 100%,
    stroke: 1pt + warning,
    radius: 8pt,
    inset: 10pt,
    fill: warning.lighten(95%),
  )[
    #align(center)[#difficulty-badge("medium")]
    #v(0.5em)
    #text(size: 9pt)[
      - 2–3 instructions
      - Some complexity
      - Varied callsigns
      - Multiple elements
    ]
  ],
  
  block(
    width: 100%,
    stroke: 1pt + danger,
    radius: 8pt,
    inset: 10pt,
    fill: danger.lighten(95%),
  )[
    #align(center)[#difficulty-badge("hard")]
    #v(0.5em)
    #text(size: 9pt)[
      - 3–4 instructions
      - Conditionals
      - Amendments
      - Rapid delivery
    ]
  ],
)

#pagebreak()

// ============================================================================
// SECTION 5: DATA FLOW
// ============================================================================

= Data Flow

== Generation Pipeline

#align(center)[
  #canvas(length: 0.8cm, {
    import draw: *
    
    let step-box(pos, num, label, color) = {
      rect(
        (pos, 0), 
        (pos + 3, 1.5),
        fill: color.lighten(90%),
        stroke: 1.5pt + color,
        radius: 0.2
      )
      content((pos + 1.5, 1), text(weight: "bold", fill: color)[#num])
      content((pos + 1.5, 0.4), text(size: 8pt)[#label])
    }
    
    // Steps
    step-box(0, "1", "Select Airport", success)
    step-box(4, "2", "Generate Callsign", secondary)
    step-box(8, "3", "Pick Category", primary)
    
    // Arrows
    line((3, 0.75), (4, 0.75), stroke: 1pt + neutral, mark: (end: ">"))
    line((7, 0.75), (8, 0.75), stroke: 1pt + neutral, mark: (end: ">"))
    
    // Second row
    set-origin((0, -2.5))
    step-box(0, "4", "Build Instructions", warning)
    step-box(4, "5", "Compose Text", primary)
    step-box(8, "6", "Extract Critical", danger)
    
    line((3, 0.75), (4, 0.75), stroke: 1pt + neutral, mark: (end: ">"))
    line((7, 0.75), (8, 0.75), stroke: 1pt + neutral, mark: (end: ">"))
    
    // Connect rows
    set-origin((0, 2.5))
    line((11, 0), (11, -1), stroke: 1pt + neutral, mark: (end: ">"))
    line((11, -1), (11.5, -1), stroke: 1pt + neutral)
    line((11.5, -1), (11.5, -2.5), stroke: 1pt + neutral)
    line((11.5, -2.5), (11, -2.5), stroke: 1pt + neutral, mark: (end: ">"))
  })
]

#v(2em)

#grid(
  columns: 2,
  gutter: 1.5em,
  
  [
    === Generation Details
    
    + *Select Airport* — Random selection from 37 DACH airports
    + *Generate Callsign* — Using `callsign_format` templates matched to difficulty
    + *Pick Category* — Based on difficulty tier distribution
    + *Build Instructions* — 1–4 instructions using `instruction_type` definitions
    + *Compose Text* — Natural ATC phraseology
    + *Extract Critical* — Identify gradable elements with weights
  ],
  
  callout(
    "Output",
    [
      Each generation creates:
      - 1 × `radiocall` record
      - N × `radiocall_instruction` records
      - JSON `critical_elements` array
    ],
    color: success,
    icon: "📦"
  )
)

#v(1em)

== Consumer Pipeline (Grading)

#callout(
  "Integration Pattern",
  [
    Your frontend fetches a `radiocall` with nested relations, presents the audio/text, captures user input, then compares against `critical_elements` for scoring.
  ],
  color: primary,
  icon: "🔌"
)

#v(0.5em)

```
1. Fetch radiocall with instructions
   GET /items/radiocall/{id}?fields=*,instructions.*,instructions.instruction_type.*

2. Present transmission (audio/text)

3. Capture user readback

4. For each critical_element:
   - Normalize user input (remove filler words, standardize numbers)
   - Check if element value appears
   - Apply weight to score

5. Calculate final score: matched_weight / total_weight

6. Match errors against common_error for feedback
```

#pagebreak()

// ============================================================================
// SECTION 6: API PATTERNS
// ============================================================================

= API Patterns

== Fetching with Relations

Get a radiocall with all data needed for grading:

```
GET /items/radiocall/{id}?fields=
  id,
  aircraft_callsign,
  full_transmission,
  expected_readback,
  critical_elements,
  difficulty,
  airport.icao_code,
  airport.name,
  instructions.sequence,
  instructions.raw_value,
  instructions.readback_text,
  instructions.instruction_type.code,
  instructions.instruction_type.grading_weight,
  instructions.instruction_type.is_critical
```

== Filtering by Difficulty

```
GET /items/radiocall?filter[difficulty][_eq]=medium&limit=10
```

== Random Selection

```
GET /items/radiocall?filter[category][_eq]=departure&sort=rand()&limit=1
```

== Category Distribution

```
GET /items/radiocall?aggregate[count]=id&groupBy[]=category
```

#v(2em)

#align(center)[
  #block(
    width: 70%,
    fill: bg-light,
    stroke: 1pt + border-light,
    radius: 8pt,
    inset: 1.5em,
  )[
    #text(size: 11pt, fill: neutral)[
      *Questions?* This schema is designed for extensibility. \
      Add new instruction types, callsign formats, or error patterns as needed.
    ]
    
    #v(0.5em)
    
    #text(size: 9pt, fill: neutral.lighten(30%))[
      Aevoli CMS · Schema v1.0
    ]
  ]
]
