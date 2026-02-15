#!/usr/bin/env python3
"""
Oscar Meme Generator - Creates personalized memes based on sentiment analysis.
Generates Pro-OBAA and Anti-Sinners memes using various meme templates.
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

# Paths
TEMPLATE_DIR = Path("/Users/joseguardo/Desktop/ICAI/OSCARS/MemeTemplate")
OUTPUT_DIR = Path("/Users/joseguardo/Desktop/ICAI/OSCARS/oscars-memes/generated")

# Try to use Impact font, fall back to default
def get_font(size):
    """Get the best available font for memes."""
    font_paths = [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/Library/Fonts/Impact.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    return ImageFont.load_default()


def draw_outlined_text(draw, pos, text, font, fill="white", outline="black", outline_width=3):
    """Draw text with outline for better readability."""
    x, y = pos
    # Draw outline
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline)
    # Draw main text
    draw.text((x, y), text, font=font, fill=fill)


def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] > max_width:
            if len(current_line) > 1:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(test_line)
                current_line = []

    if current_line:
        lines.append(' '.join(current_line))

    return '\n'.join(lines)


def create_drake_meme(reject_text, approve_text, output_path, category):
    """Create Drake approves/disapproves meme."""
    template = Image.open(TEMPLATE_DIR / "What drake likes, what drake doesn't like.png")
    draw = ImageDraw.Draw(template)

    width, height = template.size
    font = get_font(36)

    # Text area is on the right side
    text_x = width // 2 + 30
    text_width = width // 2 - 60

    # Reject text (top right)
    wrapped_reject = wrap_text(reject_text, font, text_width, draw)
    draw_outlined_text(draw, (text_x, height // 4 - 30), wrapped_reject, font)

    # Approve text (bottom right)
    wrapped_approve = wrap_text(approve_text, font, text_width, draw)
    draw_outlined_text(draw, (text_x, height * 3 // 4 - 30), wrapped_approve, font)

    template.save(output_path)
    print(f"Created: {output_path}")


def create_doge_meme(strong_text, weak_text, output_path, category):
    """Create strong vs weak doge meme."""
    template = Image.open(TEMPLATE_DIR / "Strong vs weak version .png")
    draw = ImageDraw.Draw(template)

    width, height = template.size
    font = get_font(32)

    # Strong doge (left) - text above
    wrapped_strong = wrap_text(strong_text, font, width // 2 - 40, draw)
    draw_outlined_text(draw, (20, 20), wrapped_strong, font)

    # Weak doge (right) - text above
    wrapped_weak = wrap_text(weak_text, font, width // 2 - 40, draw)
    bbox = draw.textbbox((0, 0), wrapped_weak, font=font)
    text_width = bbox[2] - bbox[0]
    draw_outlined_text(draw, (width - text_width - 20, 20), wrapped_weak, font)

    template.save(output_path)
    print(f"Created: {output_path}")


def create_spongebob_meme(text1, text2, text3, output_path, category):
    """Create Spongebob strength evolution meme."""
    template = Image.open(TEMPLATE_DIR / "Spongebob strengths evolution.png")
    draw = ImageDraw.Draw(template)

    width, height = template.size
    font = get_font(28)
    panel_height = height // 3

    # Text on right side of each panel
    text_x = width // 2 + 20
    text_width = width // 2 - 40

    # Panel 1 (weak)
    wrapped1 = wrap_text(text1, font, text_width, draw)
    draw_outlined_text(draw, (text_x, panel_height // 3), wrapped1, font)

    # Panel 2 (medium)
    wrapped2 = wrap_text(text2, font, text_width, draw)
    draw_outlined_text(draw, (text_x, panel_height + panel_height // 3), wrapped2, font)

    # Panel 3 (strong)
    wrapped3 = wrap_text(text3, font, text_width, draw)
    draw_outlined_text(draw, (text_x, 2 * panel_height + panel_height // 3), wrapped3, font)

    template.save(output_path)
    print(f"Created: {output_path}")


def create_chad_wojak_meme(chad_text, wojak_text, output_path, category):
    """Create Chad vs Wojak (nerds crying vs strong men) meme."""
    template = Image.open(TEMPLATE_DIR / "Nerds crying vs strong men standing firm.png")
    draw = ImageDraw.Draw(template)

    width, height = template.size
    font = get_font(28)

    # Wojak (left) - crying/weak
    wrapped_wojak = wrap_text(wojak_text, font, width // 2 - 40, draw)
    draw_outlined_text(draw, (20, 20), wrapped_wojak, font)

    # Chad (right) - strong
    wrapped_chad = wrap_text(chad_text, font, width // 2 - 40, draw)
    bbox = draw.textbbox((0, 0), wrapped_chad, font=font)
    text_width = bbox[2] - bbox[0]
    draw_outlined_text(draw, (width - text_width - 20, 20), wrapped_chad, font)

    template.save(output_path)
    print(f"Created: {output_path}")


def create_rollsafe_meme(top_text, bottom_text, output_path, category):
    """Create Roll Safe (thinking guy) meme."""
    template = Image.open(TEMPLATE_DIR / "Thinking_Black_Guy_Meme_Template_V1.jpg")
    draw = ImageDraw.Draw(template)

    width, height = template.size
    font = get_font(24)

    # Top text
    wrapped_top = wrap_text(top_text, font, width - 40, draw)
    draw_outlined_text(draw, (20, 10), wrapped_top, font)

    # Bottom text
    wrapped_bottom = wrap_text(bottom_text, font, width - 40, draw)
    bbox = draw.textbbox((0, 0), wrapped_bottom, font=font)
    text_height = bbox[3] - bbox[1]
    draw_outlined_text(draw, (20, height - text_height - 20), wrapped_bottom, font)

    template.save(output_path)
    print(f"Created: {output_path}")


def create_happy_concerned_meme(happy_text, concerned_text, output_path, category):
    """Create happy at first, concerned later meme."""
    template = Image.open(TEMPLATE_DIR / "Happy at first, concerned later.png")
    draw = ImageDraw.Draw(template)

    width, height = template.size
    font = get_font(28)

    # Happy (top panel) - text on left
    wrapped_happy = wrap_text(happy_text, font, width // 2 - 40, draw)
    draw_outlined_text(draw, (20, height // 4 - 40), wrapped_happy, font)

    # Concerned (bottom panel) - text on left
    wrapped_concerned = wrap_text(concerned_text, font, width // 2 - 40, draw)
    draw_outlined_text(draw, (20, height * 3 // 4 - 40), wrapped_concerned, font)

    template.save(output_path)
    print(f"Created: {output_path}")


def create_monkey_puppet_meme(top_text, output_path, category):
    """Create monkey puppet (awkward look) meme."""
    template = Image.open(TEMPLATE_DIR / "Something that is Awkward.png")
    draw = ImageDraw.Draw(template)

    width, height = template.size
    font = get_font(32)

    # Text at top
    wrapped = wrap_text(top_text, font, width - 40, draw)
    draw_outlined_text(draw, (20, 20), wrapped, font)

    template.save(output_path)
    print(f"Created: {output_path}")


def create_want_holding_meme(want_text, holding_text, output_path, category):
    """Create 'what I want vs what's holding me back' meme."""
    template = Image.open(TEMPLATE_DIR / "What I want vs what is holding me back of having it.png")
    draw = ImageDraw.Draw(template)

    width, height = template.size
    font = get_font(24)

    # Want text (yellow ball area - top right)
    wrapped_want = wrap_text(want_text, font, width // 3, draw)
    draw_outlined_text(draw, (width * 2 // 3 - 50, 30), wrapped_want, font)

    # Holding back text (pink blob - bottom left area)
    wrapped_holding = wrap_text(holding_text, font, width // 3, draw)
    draw_outlined_text(draw, (20, height * 2 // 3), wrapped_holding, font)

    template.save(output_path)
    print(f"Created: {output_path}")


def create_two_buttons_meme(button1, button2, output_path, category):
    """Create two buttons (hard choice) meme."""
    template = Image.open(TEMPLATE_DIR / "Heroe Struggles between two options.png")
    draw = ImageDraw.Draw(template)

    width, height = template.size
    font = get_font(20)

    # Get the top panel height (buttons area)
    button_panel_height = height // 2

    # Button 1 (left button)
    wrapped1 = wrap_text(button1, font, width // 3 - 20, draw)
    draw_outlined_text(draw, (40, button_panel_height // 3), wrapped1, font)

    # Button 2 (right button)
    wrapped2 = wrap_text(button2, font, width // 3 - 20, draw)
    draw_outlined_text(draw, (width // 2 + 20, button_panel_height // 3), wrapped2, font)

    template.save(output_path)
    print(f"Created: {output_path}")


def create_disbelief_meme(text, output_path, category):
    """Create disbelief and disappointment meme."""
    template = Image.open(TEMPLATE_DIR / "Disbelief and Disappointment.png")
    draw = ImageDraw.Draw(template)

    width, height = template.size
    font = get_font(40)

    # Text at top
    wrapped = wrap_text(text, font, width - 40, draw)
    draw_outlined_text(draw, (20, 20), wrapped, font)

    template.save(output_path)
    print(f"Created: {output_path}")


def create_mj_crying_meme(top_text, bottom_text, output_path, category):
    """Create MJ crying meme."""
    template = Image.open(TEMPLATE_DIR / "MJ crying in disbelief.png")
    draw = ImageDraw.Draw(template)

    width, height = template.size
    font = get_font(36)

    # Top text
    wrapped_top = wrap_text(top_text, font, width - 40, draw)
    draw_outlined_text(draw, (20, 20), wrapped_top, font)

    # Bottom text
    wrapped_bottom = wrap_text(bottom_text, font, width - 40, draw)
    bbox = draw.textbbox((0, 0), wrapped_bottom, font=font)
    text_height = bbox[3] - bbox[1]
    draw_outlined_text(draw, (20, height - text_height - 30), wrapped_bottom, font)

    template.save(output_path)
    print(f"Created: {output_path}")


def create_wojak_mask_meme(text, output_path, category):
    """Create wojak mask (internally suffering) meme."""
    template = Image.open(TEMPLATE_DIR / "Internally suffering, outside smiling.png")
    draw = ImageDraw.Draw(template)

    width, height = template.size
    font = get_font(32)

    # Text at top
    wrapped = wrap_text(text, font, width - 40, draw)
    draw_outlined_text(draw, (20, 20), wrapped, font)

    template.save(output_path)
    print(f"Created: {output_path}")



def create_incognito_face_change_meme(character_text, shadow_text, output_path, category):
    """Create Incognito Face Change meme."""
    template = Image.open(TEMPLATE_DIR / "97c192bd-8657-4b3e-86f2-780a19f6e13e_Captura de pantalla 2026-02-15 a las 10.41.26.png")
    draw = ImageDraw.Draw(template)

    font = get_font(32)

    # Character text (top left)
    wrapped_character = wrap_text(character_text, font, 600, draw)
    draw_outlined_text(draw, (10, 10), wrapped_character, font, align="center")

    # Shadow text (bottom right)
    wrapped_shadow = wrap_text(shadow_text, font, 600, draw)
    draw_outlined_text(draw, (10, 650), wrapped_shadow, font, align="center")

    template.save(output_path)
    print(f"Created: {output_path}")



def create_mr_incredible_uncanny_meme(normal_text, distorted_text, output_path, category):
    """Create Mr. Incredible Uncanny meme."""
    template = Image.open(TEMPLATE_DIR / "81a13b5c-a96b-411c-beb2-039bcc4725c4_Captura de pantalla 2026-02-15 a las 10.41.26.png")
    draw = ImageDraw.Draw(template)

    font = get_font(32)

    # Normal text slot
    wrapped_normal = wrap_text(normal_text, font, 620, draw)
    draw_outlined_text(draw, (10, 640), wrapped_normal, font)

    # Distorted text slot
    wrapped_distorted = wrap_text(distorted_text, font, 620, draw)
    draw_outlined_text(draw, (654, 640), wrapped_distorted, font)

    template.save(output_path)
    print(f"Created: {output_path}")


def generate_all_memes():
    """Generate all 20 memes."""

    print("=" * 50)
    print("Generating Pro-OBAA Memes")
    print("=" * 50)

    # Pro-OBAA Memes (10)

    # 1. Drake - Generic vs OBAA
    create_drake_meme(
        "Generic Oscar bait",
        "One Battle After Another",
        OUTPUT_DIR / "pro_obaa" / "01_drake_obaa_vs_generic.png",
        "pro_obaa"
    )

    # 2. Strong Doge - OBAA vs Other movies
    create_doge_meme(
        "OBAA: PTA directing DiCaprio",
        "Other movies: sequel #47",
        OUTPUT_DIR / "pro_obaa" / "02_doge_obaa_strong.png",
        "pro_obaa"
    )

    # 3. Spongebob - Quality evolution
    create_spongebob_meme(
        "Regular drama",
        "Oscar contender",
        "One Battle After Another",
        OUTPUT_DIR / "pro_obaa" / "03_spongebob_obaa_evolution.png",
        "pro_obaa"
    )

    # 4. Chad vs Wojak - OBAA enjoyers
    create_chad_wojak_meme(
        "OBAA enjoyers: 'Cinema.'",
        "Critics: 'It's too long'",
        OUTPUT_DIR / "pro_obaa" / "04_chad_obaa_enjoyers.png",
        "pro_obaa"
    )

    # 5. Roll Safe - Best Picture logic
    create_rollsafe_meme(
        "Can't lose Best Picture",
        "If you make the best picture",
        OUTPUT_DIR / "pro_obaa" / "05_rollsafe_best_picture.png",
        "pro_obaa"
    )

    # 6. Happy → Concerned - OBAA won
    create_happy_concerned_meme(
        "OBAA won Best Picture!",
        "Now I need to find another movie this good",
        OUTPUT_DIR / "pro_obaa" / "06_happy_obaa_won.png",
        "pro_obaa"
    )

    # 7. Monkey Puppet - Crying in public
    create_monkey_puppet_meme(
        "When OBAA makes you cry in public",
        OUTPUT_DIR / "pro_obaa" / "07_monkey_obaa_crying.png",
        "pro_obaa"
    )

    # 8. Want vs Holding - Responsibilities
    create_want_holding_meme(
        "Watching OBAA again",
        "Responsibilities",
        OUTPUT_DIR / "pro_obaa" / "08_want_obaa_again.png",
        "pro_obaa"
    )

    # 9. Drake - Superhero vs PTA
    create_drake_meme(
        "Superhero movie #47",
        "PTA's vision with DiCaprio",
        OUTPUT_DIR / "pro_obaa" / "09_drake_pta_dicaprio.png",
        "pro_obaa"
    )

    # 10. Two Buttons - IMAX vs Home (both good)
    create_two_buttons_meme(
        "Watch OBAA in IMAX 70mm",
        "Watch OBAA at home",
        OUTPUT_DIR / "pro_obaa" / "10_buttons_imax_home.png",
        "pro_obaa"
    )

    print()
    print("=" * 50)
    print("Generating Anti-Sinners Memes")
    print("=" * 50)

    # Anti-Sinners Memes (10)

    # 1. Disbelief - 16 nominations
    create_disbelief_meme(
        "Sinners got 16 Oscar nominations",
        OUTPUT_DIR / "anti_sinners" / "01_disbelief_16_nominations.png",
        "anti_sinners"
    )

    # 2. MJ Crying - After watching
    create_mj_crying_meme(
        "Sinners fans after",
        "actually watching it",
        OUTPUT_DIR / "anti_sinners" / "02_mj_sinners_fans.png",
        "anti_sinners"
    )

    # 3. Drake - Sinners vs Interview with the Vampire
    create_drake_meme(
        "Sinners: 16 nominations",
        "Interview with the Vampire",
        OUTPUT_DIR / "anti_sinners" / "03_drake_sinners_vs_interview.png",
        "anti_sinners"
    )

    # 4. Wojak Mask - Defending nominations
    create_wojak_mask_meme(
        "Me saying Sinners deserved the nominations",
        OUTPUT_DIR / "anti_sinners" / "04_wojak_sinners_defense.png",
        "anti_sinners"
    )

    # 5. Chad vs Wojak - Classic cinema vs Sinners
    create_chad_wojak_meme(
        "Classic cinema enjoyers",
        "Sinners stans: 'It's deep bro'",
        OUTPUT_DIR / "anti_sinners" / "05_chad_classic_vs_sinners.png",
        "anti_sinners"
    )

    # 6. Happy → Concerned - New vampire movie
    create_happy_concerned_meme(
        "A new vampire movie!",
        "It's 3 hours of Oscar bait",
        OUTPUT_DIR / "anti_sinners" / "06_happy_vampire_movie.png",
        "anti_sinners"
    )

    # 7. Roll Safe - Can't be overrated
    create_rollsafe_meme(
        "Can't be called overrated",
        "If you nominate it 16 times",
        OUTPUT_DIR / "anti_sinners" / "07_rollsafe_overrated.png",
        "anti_sinners"
    )

    # 8. Two Buttons - Admit mid vs Defend
    create_two_buttons_meme(
        "Admit Sinners is mid",
        "Defend 16 nominations",
        OUTPUT_DIR / "anti_sinners" / "08_buttons_sinners_mid.png",
        "anti_sinners"
    )

    # 9. Strong Doge - Classic vampires vs Sinners
    create_doge_meme(
        "Blade, Interview with the Vampire",
        "Sinners",
        OUTPUT_DIR / "anti_sinners" / "09_doge_classic_vampires.png",
        "anti_sinners"
    )

    # 10. Monkey Puppet - 16 nominations?
    create_monkey_puppet_meme(
        "How does this get 16 Oscar nominations??",
        OUTPUT_DIR / "anti_sinners" / "10_monkey_16_nominations.png",
        "anti_sinners"
    )

    print()
    print("=" * 50)
    print("DONE! Generated 20 memes")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    generate_all_memes()
