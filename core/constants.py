"""Application constants"""

# Gender choices
GENDER_CHOICES = [
    ("M", "Male"),
    ("F", "Female"),
    ("NB", "Non-binary"),
    ("O", "Other"),
]

# Swipe actions
SWIPE_LIKE = "like"
SWIPE_DISLIKE = "dislike"

SWIPE_CHOICES = [
    (SWIPE_LIKE, "Like"),
    (SWIPE_DISLIKE, "Dislike"),
]

# Match status
MATCH_PENDING = "pending"
MATCH_ACTIVE = "active"
MATCH_BLOCKED = "blocked"

MATCH_STATUS_CHOICES = [
    (MATCH_PENDING, "Pending"),
    (MATCH_ACTIVE, "Active"),
    (MATCH_BLOCKED, "Blocked"),
]

# Chat types
CHAT_PRIVATE = "private"
CHAT_ROOM = "room"

CHAT_TYPE_CHOICES = [
    (CHAT_PRIVATE, "Private"),
    (CHAT_ROOM, "Room"),
]

# Report reasons
REPORT_REASONS = [
    ("fake_profile", "Fake Profile"),
    ("inappropriate_content", "Inappropriate Content"),
    ("harassment", "Harassment"),
    ("spam", "Spam"),
    ("other", "Other"),
]

# Image verification settings
SIMILARITY_THRESHOLD = 0.8
MAX_PROFILE_PHOTOS = 5
REQUIRED_LOGIN_PHOTOS = 3
