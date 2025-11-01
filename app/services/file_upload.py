import os
import pathlib
import uuid

import aiofiles
from fastapi import HTTPException

from app.utils.config import FILE_CHUNK_SIZE, FILE_MAX_UPLOAD_SIZE, FILE_UPLOAD_TEMP_DIR


async def upload_file(file):
    filename = pathlib.Path(file.filename or "unnamed").name
    stored_name = f"{uuid.uuid4().hex}_{filename}"
    output_path = os.path.join(FILE_UPLOAD_TEMP_DIR.name, stored_name)

    total_read = 0
    try:
        async with aiofiles.open(output_path, "wb") as output_file:
            while True:
                chunk = await file.read(FILE_CHUNK_SIZE)
                if not chunk:
                    break
                total_read += len(chunk)
                if total_read > FILE_MAX_UPLOAD_SIZE:
                    # remove partial file
                    await output_file.close()
                    try:
                        os.remove(output_path)
                    except Exception:
                        pass
                    raise HTTPException(
                        status_code=413, detail="File too large. Max 5 MB."
                    )
                await output_file.write(chunk)
    finally:
        await file.close()

    return {
        "content_type": file.content_type,
        "filename": stored_name,
        "original_filename": filename,
        "path": output_path,
        "size": total_read,
    }
