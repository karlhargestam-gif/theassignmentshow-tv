"""Read reviewed video evidence; no network calls or fallback dates in builds."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit


def valid_timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})", value
    ):
        return False
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return stamp.utcoffset() is not None and stamp <= datetime.now(timezone.utc)
    except ValueError:
        return False


def load_video_metadata(root):
    path = Path(root) / ".github/data/video-metadata.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1 or not isinstance(data.get("videos"), dict):
        raise ValueError("invalid video metadata manifest")
    records = data["videos"]
    for video_id, record in records.items():
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            raise ValueError(f"invalid video ID: {video_id}")
        if record.get("sourceUrl") != f"https://www.youtube.com/watch?v={video_id}":
            raise ValueError(f"{video_id}: evidence URL must identify the exact video")
        if not isinstance(record.get("episode"), int) or not 1 <= record["episode"] <= 13:
            raise ValueError(f"{video_id}: missing episode identity")
        thumbnail = urlsplit(record.get("thumbnailUrl", ""))
        if thumbnail.scheme != "https" or not thumbnail.hostname or not record.get("thumbnailSource"):
            raise ValueError(f"{video_id}: thumbnail needs an absolute URL and source")
        if record.get("status") == "verified":
            value = record.get("uploadDate")
            if not valid_timestamp(value):
                raise ValueError(f"{video_id}: invalid or future uploadDate")
            # Accept only corroborated fields read from the exact YouTube watch page.
            fields = record.get("sourceFields", {})
            if fields.get("meta[itemprop=datePublished]") != value:
                raise ValueError(f"{video_id}: publication meta tag does not corroborate the date")
            if record.get("evidenceType") == "youtube-watch-page-dom":
                if fields.get("meta[itemprop=uploadDate]") != value:
                    raise ValueError(f"{video_id}: upload meta tag does not corroborate the date")
                if record.get("channelUrl") != "https://www.youtube.com/@missiononeeleven2447":
                    raise ValueError(f"{video_id}: unexpected source channel")
            elif record.get("evidenceType") == "youtube-watch-page-response":
                if any(fields.get(key) != value for key in (
                    "playerMicroformatRenderer.publishDate", "playerMicroformatRenderer.uploadDate"
                )):
                    raise ValueError(f"{video_id}: uploadDate disagrees with verified publication")
                if record.get("channelId") != "UCpp2TgO-EiiiPnXgAFa4J5g":
                    raise ValueError(f"{video_id}: unexpected source channel")
            else:
                raise ValueError(f"{video_id}: unsupported source evidence")
            if record.get("sourceTitle") != f"The Assignment Episode {record['episode']}":
                raise ValueError(f"{video_id}: source title does not identify this episode")
            if not all(record.get(key) for key in ("retrievedAt", "sourceSha256", "sourceHashScope")):
                raise ValueError(f"{video_id}: incomplete source evidence")
        elif record.get("status") == "unverified":
            if "uploadDate" in record or not record.get("reason"):
                raise ValueError(f"{video_id}: unverified dates must remain absent with a reason")
        else:
            raise ValueError(f"{video_id}: invalid verification status")
    return records
