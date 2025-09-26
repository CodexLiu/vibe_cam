import os
import struct


async def convert_cad_file_to_string(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()

    if ext in [
        ".step",
        ".stp",
        ".iges",
        ".igs",
        ".dxf",
        ".obj",
        ".ifc",
        ".brep",
        ".gltf",
    ]:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    if ext == ".stl":
        with open(filepath, "rb") as f:
            header = f.read(80)
            count_bytes = f.read(4)
            if len(count_bytes) == 4:
                header_text = header.decode("utf-8", errors="replace").strip()
                f.seek(0)
                sniff = f.read(512)
                if sniff.startswith(b"solid") and b"facet" in sniff:
                    with open(filepath, "r", encoding="utf-8", errors="replace") as tf:
                        return tf.read()
                triangles = struct.unpack("<I", count_bytes)[0]
                return f"STL_BINARY header={header_text} triangles={triangles}"
            else:
                with open(filepath, "r", encoding="utf-8", errors="replace") as tf:
                    return tf.read()

    if ext == ".glb":
        with open(filepath, "rb") as f:
            data = f.read()
        if len(data) < 12:
            return ""
        offset = 12
        if len(data) < offset + 8:
            return ""
        json_chunk_length = struct.unpack("<I", data[offset : offset + 4])[0]
        json_chunk_type = struct.unpack("<I", data[offset + 4 : offset + 8])[0]
        if json_chunk_type == 0x4E4F534A and len(data) >= offset + 8 + json_chunk_length:
            json_bytes = data[offset + 8 : offset + 8 + json_chunk_length]
            return json_bytes.decode("utf-8", errors="replace")
        return ""

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


