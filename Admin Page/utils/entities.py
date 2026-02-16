from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ForeignKeyConfig:
    table: str
    id_column: str
    label_column: str
    limit: int = 5000


@dataclass
class EntityConfig:
    key: str
    label: str
    table: str
    pk: str = "id"
    display_columns: List[str] = field(default_factory=list)
    read_only_columns: List[str] = field(default_factory=list)
    enum_columns: Dict[str, List[str]] = field(default_factory=dict)
    foreign_keys: Dict[str, ForeignKeyConfig] = field(default_factory=dict)
    required_columns: List[str] = field(default_factory=list)


def get_entity_configs() -> Dict[str, EntityConfig]:
    return {
        "courses": EntityConfig(
            key="courses",
            label="코스",
            table="courses",
            display_columns=[
                "id",
                "title",
                "region_id",
                "author_id",
                "source_video_id",
                "travel_days",
                "is_customized",
                "is_rep",
                "deleted_at",
                "created_at",
            ],
            read_only_columns=["id", "created_at", "updated_at"],
            foreign_keys={
                "region_id": ForeignKeyConfig("regions", "id", "region_name"),
                "author_id": ForeignKeyConfig("members", "id", "email"),
                "source_video_id": ForeignKeyConfig("videos", "id", "title"),
                "original_course_id": ForeignKeyConfig("courses", "id", "title"),
            },
            required_columns=[
                "source_video_id",
                "region_id",
                "author_id",
                "title",
                "travel_days",
                "is_customized",
                "is_rep",
            ],
        ),
        "course_places": EntityConfig(
            key="course_places",
            label="코스-장소",
            table="course_place",
            display_columns=[
                "id",
                "course_id",
                "place_id",
                "visit_day",
                "visit_order",
                "deleted_at",
                "created_at",
            ],
            read_only_columns=["id", "created_at", "updated_at"],
            foreign_keys={
                "course_id": ForeignKeyConfig("courses", "id", "title"),
                "place_id": ForeignKeyConfig("places", "id", "place_name"),
            },
            required_columns=["course_id", "place_id"],
        ),
        "members": EntityConfig(
            key="members",
            label="멤버",
            table="members",
            display_columns=[
                "id",
                "email",
                "nickname",
                "gender",
                "age_range",
                "status",
                "role",
                "deleted_at",
                "created_at",
            ],
            read_only_columns=["id", "created_at", "updated_at"],
            enum_columns={
                "gender": ["MALE", "FEMALE", "OTHER"],
                "age_range": ["AGE_10S", "AGE_20S", "AGE_30S", "AGE_40S", "AGE_50S", "AGE_60S_OVER", "UNKNOWN"],
                "status": ["ACTIVE", "INACTIVE", "SUSPENDED", "DELETED"],
                "role": ["USER", "ADMIN"],
            },
            required_columns=["email", "password", "nickname", "gender", "age_range", "status", "role"],
        ),
        "regions": EntityConfig(
            key="regions",
            label="지역",
            table="regions",
            display_columns=[
                "id",
                "region_name",
                "search_keyword",
                "image_url",
                "order_index",
                "is_active",
                "created_at",
            ],
            read_only_columns=["id", "created_at", "updated_at"],
            required_columns=["region_name", "image_url", "is_active"],
        ),
        "images": EntityConfig(
            key="images",
            label="이미지",
            table="images",
            display_columns=[
                "id",
                "image_url",
                "original_name",
                "stored_name",
                "file_size",
                "deleted_at",
                "created_at",
            ],
            read_only_columns=["id", "created_at", "updated_at"],
            required_columns=["image_url", "original_name", "stored_name", "file_size"],
        ),
        "image_place": EntityConfig(
            key="image_place",
            label="이미지-장소",
            table="image_place",
            display_columns=[
                "id",
                "image_id",
                "place_id",
                "image_type",
                "sequence",
                "description",
                "created_at",
            ],
            read_only_columns=["id", "created_at", "updated_at"],
            enum_columns={
                "image_type": ["REPRESENTATIVE", "MENU", "INTERIOR", "EXTERIOR"],
            },
            foreign_keys={
                "image_id": ForeignKeyConfig("images", "id", "original_name"),
                "place_id": ForeignKeyConfig("places", "id", "place_name"),
            },
            required_columns=["image_id", "place_id", "image_type"],
        ),
        "image_course": EntityConfig(
            key="image_course",
            label="이미지-코스",
            table="image_course",
            display_columns=[
                "id",
                "image_id",
                "course_id",
                "image_type",
                "sequence",
                "description",
                "created_at",
            ],
            read_only_columns=["id", "created_at", "updated_at"],
            enum_columns={
                "image_type": ["REPRESENTATIVE", "MENU", "INTERIOR", "EXTERIOR"],
            },
            foreign_keys={
                "image_id": ForeignKeyConfig("images", "id", "original_name"),
                "course_id": ForeignKeyConfig("courses", "id", "title"),
            },
            required_columns=["image_id", "course_id", "image_type"],
        ),
        "places": EntityConfig(
            key="places",
            label="장소",
            table="places",
            display_columns=[
                "id",
                "place_name",
                "region_id",
                "place_category",
                "ai_tag",
                "address",
                "lat",
                "lng",
                "external_id",
                "external_link",
                "deleted_at",
                "created_at",
            ],
            read_only_columns=["id", "created_at", "updated_at"],
            enum_columns={
                "place_category": ["맛집", "카페", "숙소", "관광지", "기타"],
            },
            foreign_keys={
                "region_id": ForeignKeyConfig("regions", "id", "region_name"),
            },
            required_columns=["region_id", "place_name", "place_category", "lat", "lng"],
        ),
    }
