"""Pydantic models for API request/response schemas."""
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class BlemishType(StrEnum):
    """Types of blemishes that can be detected."""
    SCRATCH = "scratch"
    DUST = "dust"
    SCUFF = "scuff"
    PRINT_ARTIFACT = "print_artifact"
    BORDER_DAMAGE = "border_damage"
    HOLOGRAPHIC_DAMAGE = "holographic_damage"


class EnhancementType(StrEnum):
    """Available enhancement types."""
    BLEMISH_REMOVAL = "blemish_removal"
    SHARPENING = "sharpening"
    COLOR_CORRECTION = "color_correction"
    CONTRAST_ENHANCEMENT = "contrast_enhancement"
    NOISE_REDUCTION = "noise_reduction"
    UPSCALING = "upscaling"


class JobStatus(StrEnum):
    """Job processing statuses."""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BlemishDetection(BaseModel):
    """Detected blemish information."""
    type: BlemishType
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: list[int] = Field(..., description="[x, y, width, height]")
    severity: str = Field(..., description="low, medium, high")


class SRModelChoice(StrEnum):
    """Super-resolution model choices for upscaling."""
    REAL_ESRGAN_X4PLUS = "real_esrgan_x4plus"  # Best general purpose
    REAL_ESRNET_X4PLUS = "real_esrnet_x4plus"  # Conservative, less artifacts
    REAL_ESRGAN_ANIME = "real_esrgan_anime_6b"  # Anime/illustrations
    REAL_ESRGAN_X2PLUS = "real_esrgan_x2plus"  # 2x faster upscaling
    ANIME_VIDEO_V3 = "anime_video_v3"  # Lightweight for video
    GENERAL_X4V3 = "general_x4v3"  # General with denoise control


class EnhancementSettings(BaseModel):
    """User-configurable enhancement settings."""
    blemish_removal: bool = True
    blemish_sensitivity: float = Field(0.7, ge=0.0, le=1.0)

    sharpening: bool = True
    sharpening_amount: float = Field(0.5, ge=0.0, le=1.0)

    color_correction: bool = True
    color_temperature: float = Field(0.0, ge=-1.0, le=1.0)
    saturation: float = Field(1.0, ge=0.0, le=2.0)

    contrast_enhancement: bool = True
    contrast_amount: float = Field(0.3, ge=0.0, le=1.0)

    noise_reduction: bool = True
    noise_reduction_strength: float = Field(0.5, ge=0.0, le=1.0)

    upscaling: bool = False
    upscale_factor: int = Field(2, ge=1, le=4)
    sr_model: SRModelChoice = Field(
        SRModelChoice.REAL_ESRGAN_X4PLUS,
        description="Super-resolution model to use for upscaling"
    )

    preserve_holographic: bool = True
    output_format: str = Field("png", pattern="^(png|jpg|webp|tiff)$")
    output_quality: int = Field(95, ge=50, le=100)
    output_dpi: int = Field(300, ge=72, le=1200)


class CardImage(BaseModel):
    """Individual card image information."""
    id: str
    filename: str
    original_path: str
    processed_path: str | None = None
    width: int
    height: int
    format: str
    size_bytes: int
    status: JobStatus = JobStatus.PENDING
    progress: float = Field(0.0, ge=0.0, le=100.0)
    detected_blemishes: list[BlemishDetection] = []
    error_message: str | None = None
    processing_time_ms: int | None = None


class BatchJob(BaseModel):
    """Batch job information."""
    id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    total_images: int
    completed_images: int
    failed_images: int
    settings: EnhancementSettings
    images: list[CardImage]
    output_zip_path: str | None = None
    total_processing_time_ms: int | None = None
    error_message: str | None = None


class UploadResponse(BaseModel):
    """Response for upload endpoint."""
    job_id: str
    status: JobStatus
    message: str
    total_files: int
    accepted_files: int
    rejected_files: int
    rejected_reasons: list[str] = []


class EnhancementResponse(BaseModel):
    """Response for enhancement endpoint."""
    job_id: str
    status: JobStatus
    message: str
    estimated_time_seconds: int


class JobStatusResponse(BaseModel):
    """Response for job status endpoint."""
    job_id: str
    status: JobStatus
    progress: float
    total_images: int
    completed_images: int
    failed_images: int
    images: list[CardImage]
    created_at: datetime
    updated_at: datetime


class PreviewResponse(BaseModel):
    """Response for preview endpoint."""
    image_id: str
    original_url: str
    preview_url: str
    detected_blemishes: list[BlemishDetection]
    settings_applied: EnhancementSettings


class DownloadResponse(BaseModel):
    """Response for download endpoint."""
    job_id: str
    download_url: str
    expires_at: datetime
    total_size_bytes: int
    file_count: int


class WebSocketProgressMessage(BaseModel):
    """WebSocket progress update message."""
    job_id: str
    image_id: str | None
    status: JobStatus
    progress: float
    message: str
    timestamp: datetime
