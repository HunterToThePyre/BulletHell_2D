from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from slides_part1 import SLIDES_PART_1
from slides_part2 import SLIDES_PART_2

ALL_SLIDES = SLIDES_PART_1 + SLIDES_PART_2

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

BG_DARK = RGBColor(10, 14, 24)
CARD_BG = RGBColor(18, 24, 40)
C_WHITE = RGBColor(255, 255, 255)
C_CYAN = RGBColor(40, 230, 255)
C_RED = RGBColor(255, 65, 65)
C_PURPLE = RGBColor(185, 85, 255)
C_GRAY = RGBColor(165, 180, 205)

blank_layout = prs.slide_layouts[6]

for idx, (title, subtitle, bullets, img_hint, notes) in enumerate(ALL_SLIDES, 1):
    slide = prs.slides.add_slide(blank_layout)
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_DARK

    bar = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.333), Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = C_RED if "босс" in title.lower() else C_CYAN
    bar.line.fill.background()

    tb = slide.shapes.add_textbox(Inches(0.6), Inches(0.35), Inches(12.1), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p_title = tf.paragraphs[0]
    p_title.text = f"{idx}. {title}" if idx > 1 else title
    p_title.font.size = Pt(32 if idx > 1 else 44)
    p_title.font.bold = True
    p_title.font.color.rgb = C_WHITE

    p_sub = tf.add_paragraph()
    p_sub.text = subtitle
    p_sub.font.size = Pt(18)
    p_sub.font.color.rgb = C_CYAN if "босс" not in title.lower() else C_RED

    content_w = Inches(7.4) if img_hint else Inches(12.1)
    card = slide.shapes.add_shape(1, Inches(0.6), Inches(1.75), content_w, Inches(4.9))
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = RGBColor(50, 70, 110)

    ctf = card.text_frame
    ctf.word_wrap = True
    ctf.margin_left = Inches(0.3)
    ctf.margin_right = Inches(0.3)
    ctf.margin_top = Inches(0.25)

    for b_idx, line in enumerate(bullets):
        p = ctf.paragraphs[0] if b_idx == 0 else ctf.add_paragraph()
        p.text = line
        p.font.size = Pt(19)
        p.font.color.rgb = C_WHITE
        p.space_after = Pt(14)

    if img_hint:
        ph = slide.shapes.add_shape(1, Inches(8.3), Inches(1.75), Inches(4.4), Inches(4.9))
        ph.fill.solid()
        ph.fill.fore_color.rgb = RGBColor(14, 18, 30)
        ph.line.color.rgb = C_PURPLE
        ptf = ph.text_frame
        ptf.word_wrap = True
        pp = ptf.paragraphs[0]
        pp.alignment = PP_ALIGN.CENTER
        pp.text = f"[ МЕСТО ДЛЯ СКРИНШОТА ]\n\n{img_hint}\n\n(Вставка -> Изображение)"
        pp.font.size = Pt(16)
        pp.font.color.rgb = C_GRAY

    ft = slide.shapes.add_textbox(Inches(11.8), Inches(6.95), Inches(1.1), Inches(0.4))
    fp = ft.text_frame.paragraphs[0]
    fp.alignment = PP_ALIGN.RIGHT
    fp.text = f"{idx} / {len(ALL_SLIDES)}"
    fp.font.size = Pt(14)
    fp.font.color.rgb = C_GRAY

    slide.notes_slide.notes_text_frame.text = notes

prs.save("BulletHell_Formacia_Presentation.pptx")
print(f"Готово! Создана презентация на {len(ALL_SLIDES)} слайдов: BulletHell_Formacia_Presentation.pptx")
