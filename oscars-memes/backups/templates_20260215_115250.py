"""Meme template registry with context for LLM generation."""

MEME_TEMPLATES = {
    "drake": {
        "id": "drake",
        "name": "Drake Approves/Disapproves",
        "filename": "What drake likes, what drake doesn't like.png",
        "text_slots": 2,
        "slot_names": ["reject_text", "approve_text"],
        "irony_type": "preference_contrast",
        "description": "Top panel: thing being rejected with dismissive gesture. Bottom panel: thing being approved with satisfied expression.",
        "tone": "Clear preference statement. First option is 'bad', second is 'good'.",
        "max_chars_per_slot": 40,
        "example": {"reject_text": "Generic Oscar bait", "approve_text": "One Battle After Another"},
        "generator_function": "create_drake_meme",
    },

    "strong_doge": {
        "id": "strong_doge",
        "name": "Strong vs Weak Doge",
        "filename": "Strong vs weak version .png",
        "text_slots": 2,
        "slot_names": ["strong_text", "weak_text"],
        "irony_type": "superiority_comparison",
        "description": "Muscular doge (superior/strong) vs small doge (inferior/weak). Used to compare two things where one is clearly better.",
        "tone": "The strong side is praised, the weak side is mocked. Both labels describe the same category of thing.",
        "max_chars_per_slot": 45,
        "example": {"strong_text": "Classic vampire movies", "weak_text": "Sinners"},
        "generator_function": "create_doge_meme",
    },

    "spongebob_evolution": {
        "id": "spongebob_evolution",
        "name": "Spongebob Strength Evolution",
        "filename": "Spongebob strengths evolution.png",
        "text_slots": 3,
        "slot_names": ["weak_text", "medium_text", "strong_text"],
        "irony_type": "escalating_quality",
        "description": "Three panels showing progression from weak to incredibly strong. Used to show escalating levels of quality/intensity.",
        "tone": "Each level is a step up. The final panel is the ultimate/best version.",
        "max_chars_per_slot": 35,
        "example": {"weak_text": "Regular drama", "medium_text": "Oscar contender", "strong_text": "OBAA"},
        "generator_function": "create_spongebob_meme",
    },

    "chad_wojak": {
        "id": "chad_wojak",
        "name": "Chad vs Crying Wojak",
        "filename": "Nerds crying vs strong men standing firm.png",
        "text_slots": 2,
        "slot_names": ["wojak_text", "chad_text"],
        "irony_type": "fan_comparison",
        "description": "Crying emotional wojak (cringe/weak opinion) vs stoic chad (based/strong opinion). Used to mock one group while praising another.",
        "tone": "Wojak says something cringe/emotional. Chad responds with based/cool statement.",
        "max_chars_per_slot": 45,
        "example": {"wojak_text": "Sinners fans: 'It's deep bro'", "chad_text": "Classic cinema enjoyers"},
        "generator_function": "create_chad_wojak_meme",
    },

    "rollsafe": {
        "id": "rollsafe",
        "name": "Roll Safe / Thinking Guy",
        "filename": "Thinking_Black_Guy_Meme_Template_V1.jpg",
        "text_slots": 2,
        "slot_names": ["top_text", "bottom_text"],
        "irony_type": "sarcastic_logic",
        "description": "Man tapping head with 'big brain' expression. Used for ironic/sarcastic 'clever' logic that's actually dumb or a hot take.",
        "tone": "Presents flawed logic as if it's genius. Top sets up premise, bottom delivers punchline.",
        "max_chars_per_slot": 50,
        "example": {"top_text": "Can't be called overrated", "bottom_text": "If you nominate it 16 times"},
        "generator_function": "create_rollsafe_meme",
    },

    "happy_concerned": {
        "id": "happy_concerned",
        "name": "Happy at First, Concerned Later",
        "filename": "Happy at first, concerned later.png",
        "text_slots": 2,
        "slot_names": ["happy_text", "concerned_text"],
        "irony_type": "expectation_subversion",
        "description": "Same person: first panel happy/excited, second panel worried/concerned. Used when initial good news leads to bad realization.",
        "tone": "First panel is positive news. Second panel reveals the catch or downside.",
        "max_chars_per_slot": 45,
        "example": {"happy_text": "A new vampire movie!", "concerned_text": "It's 3 hours of Oscar bait"},
        "generator_function": "create_happy_concerned_meme",
    },

    "monkey_puppet": {
        "id": "monkey_puppet",
        "name": "Awkward Monkey Puppet",
        "filename": "Something that is Awkward.png",
        "text_slots": 1,
        "slot_names": ["caption"],
        "irony_type": "awkward_situation",
        "description": "Puppet looking away awkwardly. Used for uncomfortable situations or things you don't want to acknowledge.",
        "tone": "Caption describes an awkward or embarrassing situation/realization.",
        "max_chars_per_slot": 60,
        "example": {"caption": "How does this get 16 Oscar nominations??"},
        "generator_function": "create_monkey_puppet_meme",
    },

    "want_holding": {
        "id": "want_holding",
        "name": "What I Want vs What's Holding Me Back",
        "filename": "What I want vs what is holding me back of having it.png",
        "text_slots": 2,
        "slot_names": ["want_text", "holding_text"],
        "irony_type": "desire_blocked",
        "description": "Person reaching for thing (want) but grabbed from behind by obstacle (holding back). Used for relatable frustrations.",
        "tone": "Want is something desirable. Holding back is the obstacle preventing it.",
        "max_chars_per_slot": 35,
        "example": {"want_text": "Watching OBAA again", "holding_text": "Responsibilities"},
        "generator_function": "create_want_holding_meme",
    },

    "two_buttons": {
        "id": "two_buttons",
        "name": "Two Buttons Hard Choice",
        "filename": "Heroe Struggles between two options.png",
        "text_slots": 2,
        "slot_names": ["button1", "button2"],
        "irony_type": "impossible_choice",
        "description": "Person sweating over two button choices. Used for difficult/impossible choices or ironic non-choices.",
        "tone": "Both options are presented as difficult to choose between (can be ironic if one is obviously better).",
        "max_chars_per_slot": 35,
        "example": {"button1": "Admit Sinners is mid", "button2": "Defend 16 nominations"},
        "generator_function": "create_two_buttons_meme",
    },

    "disbelief": {
        "id": "disbelief",
        "name": "Disbelief and Disappointment",
        "filename": "Disbelief and Disappointment.png",
        "text_slots": 1,
        "slot_names": ["caption"],
        "irony_type": "shocked_disappointment",
        "description": "Man with disappointed/disbelieving expression. Used for situations that are frustratingly unbelievable.",
        "tone": "Caption states something shocking or disappointing that happened.",
        "max_chars_per_slot": 50,
        "example": {"caption": "Sinners got 16 Oscar nominations"},
        "generator_function": "create_disbelief_meme",
    },

    "mj_crying": {
        "id": "mj_crying",
        "name": "Michael Jordan Crying",
        "filename": "MJ crying in disbelief.png",
        "text_slots": 2,
        "slot_names": ["top_text", "bottom_text"],
        "irony_type": "emotional_aftermath",
        "description": "Michael Jordan with tears. Used for moments of deep disappointment or emotional reaction.",
        "tone": "Top text sets up the context (who/when). Bottom text is what caused the tears.",
        "max_chars_per_slot": 40,
        "example": {"top_text": "Sinners fans after", "bottom_text": "actually watching it"},
        "generator_function": "create_mj_crying_meme",
    },

    "wojak_mask": {
        "id": "wojak_mask",
        "name": "Wojak Mask (Crying Inside)",
        "filename": "Internally suffering, outside smiling.png",
        "text_slots": 1,
        "slot_names": ["caption"],
        "irony_type": "hidden_pain",
        "description": "Happy mask hiding crying face. Used for pretending to be okay while suffering inside.",
        "tone": "Caption describes what you're pretending/saying publicly while secretly suffering.",
        "max_chars_per_slot": 55,
        "example": {"caption": "Me saying Sinners deserved the nominations"},
        "generator_function": "create_wojak_mask_meme",
    }
}


def get_template(template_id: str) -> dict:
    """Get a template by ID."""
    if template_id not in MEME_TEMPLATES:
        raise ValueError(f"Unknown template: {template_id}. Available: {list(MEME_TEMPLATES.keys())}")
    return MEME_TEMPLATES[template_id]


def get_all_template_ids() -> list:
    """Get all available template IDs."""
    return list(MEME_TEMPLATES.keys())


def get_templates_by_slots(num_slots: int) -> list:
    """Get templates that have a specific number of text slots."""
    return [
        tid for tid, t in MEME_TEMPLATES.items()
        if t["text_slots"] == num_slots
    ]


def get_templates_by_irony_type(irony_type: str) -> list:
    """Get templates by irony type."""
    return [
        tid for tid, t in MEME_TEMPLATES.items()
        if t["irony_type"] == irony_type
    ]
