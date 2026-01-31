from PIL import Image
import os

# Daftar gambar yang mau di-crop
images = [
    "img/Gambar png.jpg",
    "img/b097d3d520be028d40386cf3121360d6.jpg",
    "img/06fbaa15b937d9f1780d59fde5e2711a.jpg",
]


def crop_center_50(image_path):
    """Crop gambar ke center dengan ukuran 50% dari original"""
    try:
        # Buka gambar
        img = Image.open(image_path)
        width, height = img.size

        # Hitung ukuran baru (50% dari original)
        new_width = width // 2
        new_height = height // 2

        # Hitung koordinat untuk crop center
        left = (width - new_width) // 2
        top = (height - new_height) // 2
        right = left + new_width
        bottom = top + new_height

        # Crop gambar
        cropped = img.crop((left, top, right, bottom))

        # Save dengan nama baru
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        output_path = f"img/{name}_cropped{ext}"

        cropped.save(output_path, quality=95)
        print(f"✅ Cropped: {image_path} → {output_path}")
        print(f"   Original: {width}x{height} → New: {new_width}x{new_height}")

        return output_path

    except Exception as e:
        print(f"❌ Error cropping {image_path}: {e}")
        return None


if __name__ == "__main__":
    print("🔄 Starting image cropping...\n")

    # Cek folder img exist
    if not os.path.exists("img"):
        print("❌ Folder 'img' tidak ditemukan!")
        exit(1)

    cropped_files = []

    # Crop semua gambar
    for img_path in images:
        if os.path.exists(img_path):
            result = crop_center_50(img_path)
            if result:
                cropped_files.append(result)
        else:
            print(f"⚠️  File tidak ditemukan: {img_path}")

    print(f"\n✅ Done! {len(cropped_files)} gambar berhasil di-crop")
    print("\n📝 Markdown code untuk gambar yang sudah di-crop:")
    print("\n```markdown")
    for file in cropped_files:
        print(f'<img src="{file}" alt="Cropped Image" width="50%" />')
    print("```")
