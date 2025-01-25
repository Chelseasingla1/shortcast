from enum import Enum, auto


class Providers(Enum):
    TWITCH = auto()
    GITHUB = auto()


class Roles(Enum):
    ADMIN = auto()
    USER = auto()


class Categories(Enum):
    ARTS_AND_CULTURE = auto()
    BUSINESS = auto()
    COMEDY = auto()
    EDUCATION = auto()
    FICTION = auto()
    HEALTH_AND_FITNESS = auto()
    KIDS_AND_FAMILY = auto()
    LEISURE = auto()
    NEWS_AND_POLITICS = auto()
    RELIGION = auto()
    SCIENCE = auto()
    SOCIETY = auto()
    SPORTS = auto()
    CRIME = auto()
    TV_AND_FILM = auto()

category_details = {
    Categories.ARTS_AND_CULTURE: {'icon': 'bi-palette', 'description': 'Art and culture-related content'},
    Categories.BUSINESS: {'icon': 'bi-briefcase', 'description': 'Business and finance-related content'},
    Categories.COMEDY: {'icon': 'bi-emoji-smile', 'description': 'Comedy and entertainment content'},
    Categories.EDUCATION: {'icon': 'bi-book', 'description': 'Educational and learning content'},
    Categories.FICTION: {'icon': 'bi-bookmark', 'description': 'Fictional stories and books'},
    Categories.HEALTH_AND_FITNESS: {'icon': 'bi-heart', 'description': 'Health and fitness content'},
    Categories.KIDS_AND_FAMILY: {'icon': 'bi-house-door', 'description': 'Family and children-related content'},
    Categories.LEISURE: {'icon': 'bi-house', 'description': 'Leisure and hobbies content'},
    Categories.NEWS_AND_POLITICS: {'icon': 'bi-newspaper', 'description': 'News and political content'},
    Categories.RELIGION: {'icon': 'bi-cloud-sun', 'description': 'Religious content'},
    Categories.SCIENCE: {'icon': 'bi-lightbulb', 'description': 'Scientific content'},
    Categories.SOCIETY: {'icon': 'bi-people', 'description': 'Social and societal topics'},
    Categories.SPORTS: {'icon': 'bi-trophy', 'description': 'Sports and athletics content'},
    Categories.CRIME: {'icon': 'bi-shield-lock', 'description': 'Crime and investigative content'},
    Categories.TV_AND_FILM: {'icon': 'bi-tv', 'description': 'Movies and TV-related content'},
}

categories_details = [
    {
        'name': category.name.replace('_', ' ').title(),
        'icon': category_details[category]['icon'],
        'description': category_details[category]['description']
    }
    for category in Categories
]


class Shared(Enum):
    MODERATOR = auto()
    CONSUMERS = auto()


def role_check(role: str):
    if role == "ADMIN":
        return Roles.ADMIN
    elif role == "USER":
        return Roles.USER


def provider_check(provider: str):
    if provider == 'GITHUB':
        return Providers.GITHUB
    elif provider == 'TWITCH':
        return Providers.TWITCH


class FakeClient:
    def __init__(self, user_id):
        self.id = user_id
        self.username = 'Jerry George'
        self.is_authenticated = True
