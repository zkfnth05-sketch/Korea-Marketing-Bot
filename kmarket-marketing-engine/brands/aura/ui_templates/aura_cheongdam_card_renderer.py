"""
Aura Lookbook Moodboard (Paper Frame) Before & After Simulation Video Renderer
- 8-Second High-End Studio Lookbook Simulation (4 Diverse Models)
- Warm Sand/Taupe Plaster Wall + Sunlight Shaft + Organic Leaf Shadows
- Staggered Fine Art Matte Paper Frames with Realistic 3D Multi-Layer Drop Shadows
- Champagne Gold Typography & Badges (— BEFORE — / — AFTER —)
- 1080x1920 30fps MP4
"""

import os
import sys
import shutil
import tempfile
import subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

class AuraCheongdamMoodboardRenderer:
    def __init__(self):
        self.w = 1080
        self.h = 1920
        self.artifact_dir = Path(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\9d989a93-cf2f-49a0-94dd-4e770271805c")
        
        self.models = [
            {
                "num": "01",
                "name": "서연",
                "age": 23,
                "style": "화사한 파스텔 핑크 트위드 재킷 (Lovely Spring)",
                "before_img": "woman1_before_seoyeon_1790299355914.jpg",
                "after_img": "woman1_after_seoyeon_v2_1790299815639.jpg",
            },
            {
                "num": "02",
                "name": "지우",
                "age": 25,
                "style": "세련된 네이비 테일러드 블레이저 (Modern Chic)",
                "before_img": "woman2_before_jiwoo_1790299419816.jpg",
                "after_img": "woman2_after_jiwoo_v2_1790299878253.jpg",
            },
            {
                "num": "03",
                "name": "수아",
                "age": 22,
                "style": "실크 캐미솔 + 가디건 레이어드 (Pure Elegance)",
                "before_img": "woman3_before_suah_1790299697602.jpg",
                "after_img": "woman3_after_suah_1790299719616.jpg",
            },
            {
                "num": "04",
                "name": "유진",
                "age": 24,
                "style": "모던 소프트 브이넥 니트 (Soft Minimal)",
                "before_img": "woman4_before_yujin_1790299743008.jpg",
                "after_img": "woman4_after_yujin_1790299766621.jpg",
            },
        ]
        
        # Pre-render static studio background once for max performance
        self._bg = self._create_studio_background()

    def _get_font(self, size: int, bold: bool = True):
        candidates = [
            r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        ]
        for p in candidates:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    def _create_studio_background(self) -> Image.Image:
        """Create warm sand/taupe plaster wall with sunlight beam and organic leaf shadows"""
        arr = np.zeros((self.h, self.w, 3), dtype=np.float32)
        for y in range(self.h):
            ratio = y / self.h
            arr[y, :, 0] = 216.0 - ratio * 18.0
            arr[y, :, 1] = 202.0 - ratio * 20.0
            arr[y, :, 2] = 188.0 - ratio * 22.0

        np.random.seed(42)
        noise = np.random.normal(0, 3.5, (self.h, self.w, 3))
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        bg = Image.fromarray(arr, mode="RGB")

        # 1. Sunlight beam from top-left
        sun_layer = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(sun_layer)
        sun_poly = [(-200, -100), (750, -100), (450, 2100), (-300, 2100)]
        s_draw.polygon(sun_poly, fill=(255, 250, 235, 35))
        sun_layer = sun_layer.filter(ImageFilter.GaussianBlur(80))
        bg = Image.alpha_composite(bg.convert("RGBA"), sun_layer)

        # 2. Organic leaf shadows on right side
        leaf_layer = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        l_draw = ImageDraw.Draw(leaf_layer)
        shadow_col = (70, 55, 45, 55)

        stems = [
            [(1150, 400), (950, 600), (820, 850), (750, 1100), (800, 1450), (900, 1800)],
            [(1150, 900), (980, 1100), (860, 1350), (820, 1650)]
        ]
        for stem in stems:
            l_draw.line(stem, fill=shadow_col, width=18)

        leaf_centers = [
            (920, 550, 70, 130, -35),
            (860, 700, 80, 150, -50),
            (800, 920, 85, 160, -25),
            (730, 1080, 90, 170, 10),
            (760, 1250, 85, 160, 35),
            (820, 1400, 90, 170, 45),
            (880, 1580, 80, 150, 55),
            (950, 1050, 75, 140, -40),
            (890, 1220, 80, 150, -15),
            (850, 1420, 75, 140, 20),
            (1020, 300, 90, 160, -60),
            (1050, 480, 85, 150, -45)
        ]
        for lx, ly, lw, lh, rot in leaf_centers:
            leaf_mask = Image.new("RGBA", (lh * 2, lh * 2), (0, 0, 0, 0))
            lm_draw = ImageDraw.Draw(leaf_mask)
            cx, cy = lh, lh
            lm_draw.ellipse([cx - lw // 2, cy - lh // 2, cx + lw // 2, cy + lh // 2], fill=shadow_col)
            rotated = leaf_mask.rotate(rot, resample=Image.Resampling.BICUBIC)
            leaf_layer.paste(rotated, (lx - lh, ly - lh), rotated)

        leaf_layer = leaf_layer.filter(ImageFilter.GaussianBlur(32))
        bg = Image.alpha_composite(bg, leaf_layer)
        return bg.convert("RGB")

    def _render_paper_frame(self, photo_path: Path, frame_w: int, frame_h: int, border_size: int = 22, is_gold_border: bool = False) -> Image.Image:
        """Render single fine art photo print with paper texture and border"""
        frame = Image.new("RGBA", (frame_w, frame_h), (252, 250, 246, 255))
        f_draw = ImageDraw.Draw(frame)
        f_draw.rectangle([(0, 0), (frame_w - 1, frame_h - 1)], outline=(225, 220, 210, 255), width=1)

        pw = frame_w - border_size * 2
        ph = frame_h - border_size * 2

        if photo_path.exists():
            p_img = Image.open(photo_path).convert("RGB")
            img_w, img_h = p_img.size
            tr = pw / ph
            cr = img_w / img_h
            if cr > tr:
                nw = int(img_h * tr)
                p_img = p_img.crop(((img_w - nw) // 2, 0, (img_w + nw) // 2, img_h))
            else:
                nh = int(img_w / tr)
                p_img = p_img.crop((0, (img_h - nh) // 2, img_w, (img_h + nh) // 2))
            p_img = p_img.resize((pw, ph), Image.Resampling.LANCZOS)
            frame.paste(p_img.convert("RGBA"), (border_size, border_size))
            f_draw.rectangle([(border_size, border_size), (border_size + pw - 1, border_size + ph - 1)], outline=(200, 195, 185, 150), width=1)
            
            if is_gold_border:
                f_draw.rectangle([(border_size - 3, border_size - 3), (border_size + pw + 2, border_size + ph + 2)], outline=(212, 175, 55, 220), width=2)
                f_draw.rectangle([(0, 0), (frame_w - 1, frame_h - 1)], outline=(212, 175, 55, 240), width=2)

        return frame

    def _apply_drop_shadow(self, canvas: Image.Image, frame: Image.Image, x: int, y: int, blur_rad: int = 35, offset=(18, 28), shadow_alpha: int = 120):
        """Apply realistic multi-layered soft drop shadow under frame"""
        w, h = canvas.size
        fw, fh = frame.size
        pad = blur_rad * 3
        
        full_shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        
        s_img = Image.new("RGBA", (fw + pad * 2, fh + pad * 2), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(s_img)
        s_draw.rectangle([(pad + offset[0], pad + offset[1]), (pad + fw + offset[0], pad + fh + offset[1])], fill=(40, 30, 20, shadow_alpha))
        s_blurred = s_img.filter(ImageFilter.GaussianBlur(blur_rad))
        full_shadow.paste(s_blurred, (x - pad, y - pad), s_blurred)

        c_img = Image.new("RGBA", (fw + pad * 2, fh + pad * 2), (0, 0, 0, 0))
        c_draw = ImageDraw.Draw(c_img)
        c_draw.rectangle([(pad + 4, pad + 8), (pad + fw + 4, pad + fh + 8)], fill=(30, 20, 15, int(shadow_alpha * 0.8)))
        c_blurred = c_img.filter(ImageFilter.GaussianBlur(8))
        full_shadow.paste(c_blurred, (x - pad, y - pad), c_blurred)

        canvas_rgba = canvas.convert("RGBA")
        canvas_rgba = Image.alpha_composite(canvas_rgba, full_shadow)
        canvas_rgba.paste(frame, (x, y), frame)

        return canvas_rgba.convert("RGB")

    def render_model_frame(self, model_idx: int, t_prog: float) -> Image.Image:
        """
        Render a single frame for the model at t_prog (0.0 to 1.0 within the 2.0s window)
        - 0.0 ~ 0.4s (t_prog 0.0 ~ 0.2): Left BEFORE frame is active, Right AFTER is emerging
        - 0.4 ~ 0.6s (t_prog 0.2 ~ 0.3): Flash beam sweep across
        - 0.6 ~ 2.0s (t_prog 0.3 ~ 1.0): Full AFTER bloom + gold badge radiance
        """
        m = self.models[model_idx]
        b_path = self.artifact_dir / m["before_img"]
        a_path = self.artifact_dir / m["after_img"]

        fw, fh = 450, 650
        border = 22

        left_x = 65
        left_y = 660

        right_x = 565
        right_y = 480

        # Render base cards
        f_before = self._render_paper_frame(b_path, fw, fh, border_size=border, is_gold_border=False)
        f_after = self._render_paper_frame(a_path, fw, fh, border_size=border, is_gold_border=True)

        img = self._bg.copy()
        img = self._apply_drop_shadow(img, f_before, left_x, left_y, blur_rad=32, offset=(14, 24), shadow_alpha=110)
        img = self._apply_drop_shadow(img, f_after, right_x, right_y, blur_rad=36, offset=(18, 28), shadow_alpha=125)

        draw = ImageDraw.Draw(img)

        # 1. TOP EDITORIAL HEADER
        f_brand = self._get_font(26, bold=True)
        draw.text((self.w // 2, 130), "A U R A   S T U D I O   L O O K B O O K", font=f_brand, fill=(160, 125, 45), anchor="mm")

        f_title = self._get_font(44, bold=True)
        draw.text((self.w // 2, 195), "청담동 스냅 화보급 AI 보정", font=f_title, fill=(35, 30, 25), anchor="mm")

        f_sub = self._get_font(24, bold=False)
        draw.text((self.w // 2, 255), "자연스러운 본판 100% 보존 • 고급스러운 음영 조명", font=f_sub, fill=(115, 100, 90), anchor="mm")

        draw.line([(self.w // 2 - 120, 305), (self.w // 2 + 120, 305)], fill=(200, 165, 75), width=2)

        # 2. LABELS UNDER FRAMES
        b_label_y = left_y + fh + 35
        f_badge_en = self._get_font(30, bold=True)
        f_badge_kr = self._get_font(22, bold=False)

        # Left: — BEFORE —
        draw.text((left_x + fw // 2, b_label_y), "—  B E F O R E  —", font=f_badge_en, fill=(130, 100, 45), anchor="mm")
        draw.text((left_x + fw // 2, b_label_y + 40), "[ 형광등 일상 셀카 ]", font=f_badge_kr, fill=(100, 85, 75), anchor="mm")

        # Right: — AFTER —
        a_label_y = right_y + fh + 35
        pill_w = 320
        pill_h = 56
        pill_x1 = right_x + fw // 2 - pill_w // 2
        pill_y1 = a_label_y - pill_h // 2
        
        # Glow modulation
        is_after_active = t_prog >= 0.25
        glow_pulse = max(0.0, 1.0 - (t_prog - 0.25) * 3.0) if 0.25 <= t_prog <= 0.6 else 0.0
        
        bg_col = (55, 42, 22) if is_after_active else (35, 28, 18)
        border_col = (255, 235, 150) if glow_pulse > 0 else (212, 175, 55)
        
        draw.rounded_rectangle([(pill_x1, pill_y1), (pill_x1 + pill_w, pill_y1 + pill_h)], radius=18, fill=bg_col, outline=border_col, width=3 if glow_pulse > 0 else 2)
        draw.text((right_x + fw // 2, a_label_y - 2), "—  A F T E R  —", font=f_badge_en, fill=(255, 230, 140) if is_after_active else (220, 190, 100), anchor="mm")
        draw.text((right_x + fw // 2, a_label_y + 45), "[ 본판 보존 • 청담동 화보 ]", font=f_badge_kr, fill=(140, 105, 45), anchor="mm")

        # 3. BOTTOM FLOATING INFO CARD
        card_box_y = 1470
        card_w = 950
        card_h = 240
        card_x1 = (self.w - card_w) // 2
        card_y1 = card_box_y

        glass = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glass)
        g_draw.rounded_rectangle([(card_x1, card_y1), (card_x1 + card_w, card_y1 + card_h)], radius=32, fill=(25, 20, 18, 225), outline=(200, 165, 75, 200), width=2)
        img_rgba = Image.alpha_composite(img.convert("RGBA"), glass)
        img = img_rgba.convert("RGB")
        draw = ImageDraw.Draw(img)

        f_model_name = self._get_font(38, bold=True)
        draw.text((card_x1 + 50, card_y1 + 45), f"LOOK #{m['num']}   {m['name']} ({m['age']})", font=f_model_name, fill=(245, 215, 120))

        f_tag = self._get_font(26, bold=False)
        draw.text((card_x1 + 50, card_y1 + 105), f"스타일링: {m['style']}", font=f_tag, fill=(225, 220, 215))

        f_desc = self._get_font(24, bold=False)
        draw.text((card_x1 + 50, card_y1 + 155), "• 본래 이목구비 100% 보존 • 청담동 스튜디오 조명 & 텍스처", font=f_desc, fill=(180, 165, 150))

        # 4. Optional Light Sweep during transition (0.2 ~ 0.35)
        if 0.2 <= t_prog <= 0.35:
            sweep_prog = (t_prog - 0.2) / 0.15
            flare = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
            fl_draw = ImageDraw.Draw(flare)
            sweep_x = int(right_x + fw * sweep_prog)
            fl_draw.line([(sweep_x - 30, right_y), (sweep_x + 30, right_y + fh)], fill=(255, 245, 210, 140), width=20)
            flare = flare.filter(ImageFilter.GaussianBlur(15))
            img = Image.alpha_composite(img.convert("RGBA"), flare).convert("RGB")

        return img

    def render_video(self, output_mp4_path: str, duration_sec: float = 8.0) -> str:
        """Render full 8-second 1080x1920 30fps MP4 video"""
        out_p = Path(output_mp4_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        
        fps = 30
        total_frames = int(duration_sec * fps)
        time_per_model = duration_sec / len(self.models) # 2.0s per woman
        
        temp_dir = Path(tempfile.mkdtemp(prefix="aura_moodboard_sim_"))
        print(f"[Aura Lookboard Simulation] 8s ({total_frames} frames) rendering start...")

        try:
            for frame_idx in range(total_frames):
                curr_t = frame_idx / fps
                model_idx = min(int(curr_t / time_per_model), len(self.models) - 1)
                t_in_model = curr_t - model_idx * time_per_model # 0.0 ~ 2.0s
                t_prog = t_in_model / time_per_model # 0.0 ~ 1.0

                frame_img = self.render_model_frame(model_idx, t_prog)
                frame_path = temp_dir / f"frame_{frame_idx:05d}.jpg"
                frame_img.save(frame_path, quality=95)

            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

            cmd = [
                ffmpeg_exe,
                "-y",
                "-framerate", str(fps),
                "-i", str(temp_dir / "frame_%05d.jpg"),
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                str(out_p)
            ]
            print(f"[FFmpeg Encoding] {out_p.name} creating...")
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"FFmpeg error: {res.stderr}")

            print(f"[Success] 8s lookboard simulation finished: {out_p}")
            return str(out_p)

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    renderer = AuraCheongdamMoodboardRenderer()
    out_file = Path(r"C:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine\brands\aura\ui_templates\presets\aura_cheongdam_before_after_sim.mp4")
    renderer.render_video(str(out_file), duration_sec=8.0)
