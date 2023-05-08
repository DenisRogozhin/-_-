from enum import Enum


class Gender(str, Enum):
    MALE = 'Мужской'
    FEMALE = 'Женский'


class Person(str, Enum):
    FAMILY = 'Член семьи'
    FRIEND = 'Друг'
    FELLOW = 'Приятель'
    TEACHER = 'Учитель'
    COLLEAGUE = 'Коллега'


class Activities(str, Enum):
    CULTURE = 'культурные мероприятия'
    HOME = 'домосед'
    SPORT = 'активный образ жизни и спорт'
    ANIMALS = 'животные'
    READ = 'чтение'
    NEW = 'любит узнавать новое'
    PHOTO = 'увлекается фотографией'
    QUEST = 'игры, квесты, головоломки'
    COOK = 'любит вкусно поесть'
    UNKNOWN = 'мы мало знакомы'
    UNIVERSAL = 'universal'


class Presents(dict, Enum):
    THEATRE = {
        'name': 'Билет в театр',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND, Person.TEACHER, Person.COLLEAGUE],
        'age': [15, 100],
        'activities': {Activities.CULTURE}
    }
    CINEMA = {
        'name': 'Билет в кино',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND, Person.FELLOW],
        'age': [12, 100],
        'activities': {Activities.CULTURE}
    }
    EXHIBITION = {
        'name': 'Билет на выставку',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND, Person.FELLOW, Person.TEACHER, Person.COLLEAGUE],
        'age': [15, 100],
        'activities': {Activities.CULTURE}
    }
    BOOK = {
        'name': 'Книга',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [pers for pers in Person],
        'age': [5, 100],
        'activities': {Activities.CULTURE, Activities.READ, Activities.HOME}
    }
    BOARD_GAME = {
        'name': 'Настольные игры',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND, Person.FELLOW],
        'age': [5, 100],
        'activities': {Activities.HOME, Activities.QUEST}
    }
    VIDEO_GAME = {
        'name': 'Компьютерные игры (и дополнения к ним)',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND, Person.FELLOW],
        'age': [10, 60],
        'activities': {Activities.HOME, Activities.QUEST}
    }
    BOOK_CERT = {
        'name': 'Сертификат в книжный магазин',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [pers for pers in Person],
        'age': [10, 100],
        'activities': {Activities.READ}
    }
    CRAFT_CERT = {
        'name': 'Сертификат на мастер-класс по изготовлению чего-нибудь своими руками (гончарная мастерская, свечи, панно, картины и пр.)',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND, Person.COLLEAGUE],
        'age': [15, 60],
        'activities': {Activities.NEW}
    }
    COOK_CERT = {
        'name': 'Сертификат на кулинарный мастер-класс',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND, Person.COLLEAGUE],
        'age': [15, 60],
        'activities': {Activities.NEW, Activities.COOK}
    }
    DEGUSTATION = {
        'name': 'Билет на дегустацию (сыров, вина, шоколада, закусок и пр.)',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND, Person.TEACHER, Person.COLLEAGUE],
        'age': [18, 100],
        'activities': {Activities.NEW, Activities.COOK}
    }
    PHOTO_SHOOT = {
        'name': 'Фотосессия',
        'gender': [Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND],
        'age': [18, 50],
        'activities': {Activities.PHOTO, Activities.NEW}
    }
    PHOTO_CERT = {
        'name': 'Сертификат на мастер-класс по фотографии',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND, Person.TEACHER, Person.COLLEAGUE],
        'age': [18, 100],
        'activities': {Activities.PHOTO}
    }
    COSM_SHOP = {
        'name': 'Сертификат в магазин косметики',
        'gender': [Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND, Person.TEACHER, Person.COLLEAGUE],
        'age': [18, 100],
        'activities': {Activities.UNIVERSAL}
    }
    COSM_CERT = {
        'name': 'Сертификат на мастер-класс по изготовлению косметики/духов',
        'gender': [Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND, Person.COLLEAGUE],
        'age': [18, 100],
        'activities': {Activities.NEW}
    }
    FASHION_CERT = {
        'name': 'Сертификат в магазин одежды',
        'gender': [Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND],
        'age': [18, 100],
        'activities': {Activities.UNIVERSAL}
    }
    SPORT_CERT = {
        'name': 'Сертификат на занятие спортом (скалолазание, серфинг, сплав на байдарках, аэротруба, командные игры и пр.)',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND, Person.TEACHER, Person.COLLEAGUE],
        'age': [18, 50],
        'activities': {Activities.SPORT}
    }
    FIGHT_CERT = {
        'name': 'Сертификат на мастер-класс по стрельбе/борьбе',
        'gender': [Gender.MALE],
        'person': [Person.FAMILY, Person.FRIEND, Person.TEACHER, Person.COLLEAGUE],
        'age': [18, 50],
        'activities': {Activities.SPORT}
    }
    QUEST = {
        'name': 'Квест',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND, Person.COLLEAGUE],
        'age': [18, 50],
        'activities': {Activities.QUEST, Activities.NEW}
    }
    VR = {
        'name': 'VR-квест',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND, Person.COLLEAGUE],
        'age': [18, 50],
        'activities': {Activities.NEW, Activities.QUEST}
    }
    ANIMALS = {
        'name': 'Билет в контактный зоопарк',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND, Person.TEACHER, Person.COLLEAGUE],
        'age': [10, 100],
        'activities': {Activities.ANIMALS}
    }
    HORSES = {
        'name': 'Конная прогулка',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [Person.FAMILY, Person.FRIEND, ],
        'age': [12, 60],
        'activities': {Activities.SPORT}
    }
    FLOWERS = {
        'name': 'Букет цветов',
        'gender': [Gender.FEMALE],
        'person': [pers for pers in Person],
        'age': [0, 100],
        'activities': {Activities.UNIVERSAL}
    }
    SWEETS = {
        'name': 'Конфеты',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [pers for pers in Person],
        'age': [0, 100],
        'activities': {Activities.UNIVERSAL}
    }
    CAKE = {
        'name': 'Торт',
        'gender': [Gender.MALE, Gender.FEMALE],
        'person': [pers for pers in Person],
        'age': [0, 100],
        'activities': {Activities.UNIVERSAL}
    }


def get_age_str(age: int):
    """
    Function returns the correct form for number of years.
    """
    if age % 10 == 1:
        if age % 100 == 11:
            year = 'лет'
        else:
            year = 'год'
    elif age % 10 in (2, 3, 4):
        if age % 100 in (12, 13, 14):
            year = 'лет'
        else:
            year = 'года'
    else:
        year = 'лет'
    return year


def get_person_type_with_gender(person_type: str, gender: str):
    """
    Function returns receiver depending on his/her gender.
    """
    person = ''
    if person_type == Person.COLLEAGUE:
        person = 'коллеги'
    elif person_type in (Person.TEACHER, Person.FELLOW):
        if gender == Gender.MALE:
            person = person_type[:-1].lower() + 'я'
        else:
            person = person_type.lower() + 'ницы'
    elif person_type == Person.FAMILY:
        if gender == Gender.MALE:
            person = 'именинника'
        else:
            person = 'именинницы'
    elif person_type == Person.FRIEND:
        if gender == Gender.MALE:
            person = 'друга'
        else:
            person = 'подруги'
    return person


def generate_recommendation(person_info: dict):
    """
    Function generates a list of birthday presents that can be suitable.
    """
    person = get_person_type_with_gender(
        person_type=person_info['type'],
        gender=person_info['gender']
    )
    year = get_age_str(
        age=person_info['age']
    )
    template = f"Варианты подарка для {person} на {person_info['age']} {year}:\n"
    cnt = 1
    presents = ""
    if 'activities' in person_info:
        person_info['activities'].add(Activities.UNIVERSAL)
    else:
        person_info['activities'] = {Activities.UNIVERSAL}
    for present in list(Presents):
        if person_info['type'] in present['person'] and person_info['gender'] in present['gender']:
            if present['age'][0] <= person_info['age'] <= present['age'][1]:
                if person_info['activities'] & present['activities']:
                    presents += f"{cnt}. {present['name']}\n"
                    cnt += 1
    return template + presents
