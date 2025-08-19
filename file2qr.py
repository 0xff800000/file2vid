import argparse
import base64
import math
import zlib
import os

import cv2
import imageio
import numpy as np
import qrcode
from qrcode.constants import ERROR_CORRECT_H
import pyzbar.pyzbar

import logging
logging.basicConfig(level=logging.DEBUG)

def _qr_frame_from_text(text: str, side_px: int = 1080, border: int = 4, version: int | None = None) -> np.ndarray:
    """
    Build a high-contrast QR as a fixed-size BGR image for video.
    Resizing uses NEAREST to keep QR modules crisp.
    """
    qr = qrcode.QRCode(
        version=version,  # keep None to auto-fit; we will normalize frame size by resizing
        error_correction=ERROR_CORRECT_H,  # most robust against compression
        box_size=10,
        border=border,
    )
    qr.add_data(text)
    qr.make(fit=(version is None))
    pil_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    arr_rgb = np.array(pil_img)  # (h, w, 3), uint8

    # Resize to fixed square frame
    arr_rgb = cv2.resize(arr_rgb, (side_px, side_px), interpolation=cv2.INTER_NEAREST)
    frame_bgr = cv2.cvtColor(arr_rgb, cv2.COLOR_RGB2BGR)
    return frame_bgr


def file_to_qr_video(
    input_file: str,
    output_video: str,
    fps: int = 1,
    chunk_size: int = 1000,
    side_px: int = 1080,
    version: int | None = None,
):
    """
    Encode any file into a video of QR frames. Each frame is the same size.
    - Uses base64 payload + CRC32 for each chunk.
    - ERROR_CORRECT_H for robustness after YouTube re-encode.
    """
    with open(input_file, "rb") as f:
        data = f.read()

    # handle empty files by sending one empty chunk
    total_chunks = max(1, math.ceil(len(data) / chunk_size))

    # Prepare writer (1080 is divisible by 16; good for H.264 macroblocks)
    writer = imageio.get_writer(
        output_video,
        fps=fps,
        codec="libx264",
        quality=4,
        macro_block_size=None,  # let writer use the exact size provided
    )

    for idx in range(total_chunks):
        chunk = data[idx * chunk_size : (idx + 1) * chunk_size]
        b64 = base64.b64encode(chunk).decode("ascii")
        crc = zlib.crc32(chunk) & 0xFFFFFFFF
        # Packet format: QRV1|index|total|crc32|payload_b64
        packet = f"QR1|{idx}|{total_chunks}|{hex(crc)}|{b64}"
        print(packet)

        frame = _qr_frame_from_text(packet, side_px=side_px, version=version)
        # imageio expects RGB
        writer.append_data(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    writer.close()
    print(f"✅ Encoded '{input_file}' into '{output_video}' with {total_chunks} QR frames.")


def qr_video_to_file(input_video: str, output_file: str):
    """
    Decode a video of QR frames back into the original file.
    Uses OpenCV QRCodeDetector (no external zbar needed).
    Verifies CRC per chunk and reassembles in order.
    """
    cap = cv2.VideoCapture(input_video)

    chunks: dict[int, bytes] = {}
    total = None
    frames_read = 0
    frames_decoded = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames_read += 1

        data = pyzbar.pyzbar.decode(frame)
        if not data:
            print(f"{frames_read} no data")
            continue
        
        print(data)
        print(data[0].data)
        data = data[0].data.decode("utf-8")

        parts = data.split("|", 4)
        if len(parts) != 5:
            print("Invalid data format")
            continue

        if parts[0] != "QR1":
            print("Invalid header")
            continue

        try:
            idx = int(parts[1])
            tot = int(parts[2])
            crc = int(parts[3], 0)
            payload = base64.b64decode(parts[4])
        except Exception:
            print("Could not parse packet")
            continue

        # CRC check
        if (zlib.crc32(payload) & 0xFFFFFFFF) != crc:
            print("Invalid CRC")
            continue

        chunks[idx] = payload
        total = tot
        frames_decoded += 1

    cap.release()

    if total is None:
        raise RuntimeError("No valid QR packets found.")

    missing = [i for i in range(total) if i not in chunks]
    if missing:
        raise RuntimeError(
            f"Incomplete recovery. Missing {len(missing)} chunks (e.g., {missing[:10]}...)."
        )

    with open(output_file, "wb") as f:
        for i in range(total):
            f.write(chunks[i])

    print(
        f"✅ Reconstructed '{output_file}' from '{input_video}'. "
        f"Frames read: {frames_read}, decoded: {frames_decoded}, chunks: {total}."
    )


def main():
    parser = argparse.ArgumentParser(description="Store arbitrary data in a QR video (YouTube-survivable).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    enc = sub.add_parser("encode", help="Encode a file into a QR video.")
    enc.add_argument("input_file", help="Path to the input file.")
    enc.add_argument("output_video", help="Output video path, e.g., out.mp4")
    enc.add_argument("--fps", type=int, default=1)
    enc.add_argument("--chunk-size", type=int, default=1000)
    enc.add_argument("--side", type=int, default=1080, help="Square frame side in pixels.")
    enc.add_argument("--version", type=int, default=None, help="Fixed QR 'version' (1..40). Leave empty for auto.")

    dec = sub.add_parser("decode", help="Decode a QR video back into a file.")
    dec.add_argument("input_video", help="Path to the QR video, e.g., out.mp4")
    dec.add_argument("output_file", help="Where to write the reconstructed file.")

    args = parser.parse_args()

    if args.cmd == "encode":
        file_to_qr_video(
            args.input_file,
            args.output_video,
            fps=args.fps,
            chunk_size=args.chunk_size,
            side_px=args.side,
            version=args.version,
        )
    else:
        qr_video_to_file(args.input_video, args.output_file)


if __name__ == "__main__":
    main()

