from domain.entities.db.models.user import User


def to_domain_user(model: User) -> User:
    return User(
        id=model.id,
        name=model.name,
        telegram=model.telegram,
        collection_songs_photo_file_id=model.collection_songs_photo_file_id,
        collection_songs_photo_file_unique_id=model.collection_songs_photo_file_unique_id,
    )
