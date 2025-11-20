from enum import Enum


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    EMPTY = ""


class FilterGenderEnum(str, Enum):
    ANY = "any"
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    EMPTY = ""


class DegreeLevelEnum(str, Enum):
    BSC = "B.Sc."
    BA = "B.A."
    MSC = "M.Sc."
    MA = "M.A."
    PHD = "Ph.D."
    ASSOCIATE = "Associate"
    DIPLOMA = "Diploma"
    EMPTY = ""


class FilterEducationLevelEnum(str, Enum):
    ANY = "any"
    BSC = "B.Sc."
    BA = "B.A."
    MSC = "M.Sc."
    MA = "M.A."
    PHD = "Ph.D."
    ASSOCIATE = "Associate"
    DIPLOMA = "Diploma"
    EMPTY = ""


class LanguageLevelEnum(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    FLUENT = "Fluent"
    NATIVE = "Native"
    EMPTY = ""


class JobTypeEnum(str, Enum):
    ANY = "any"
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    REMOTE = "remote"
    EMPTY = ""


class WorkModeEnum(str, Enum):
    ANY = "any"
    ON_SITE = "on_site"
    HYBRID = "hybrid"
    REMOTE = "remote"
    EMPTY = ""


class ProjectTypeEnum(str, Enum):
    PERSONAL = "Personal"
    ACADEMIC = "Academic"
    PROFESSIONAL = "Professional"
    OPEN_SOURCE = "Open Source"
    TEAM = "Team"
    SOLO = "Solo"
    EMPTY = ""


class AwardLevelEnum(str, Enum):
    INTERNATIONAL = "International"
    NATIONAL = "National"
    REGIONAL = "Regional"
    UNIVERSITY = "University"
    DEPARTMENT = "Department"
    LOCAL = "Local"
    EMPTY = ""


class AwardCategoryEnum(str, Enum):
    ACADEMIC = "Academic Excellence"
    SCHOLARSHIP = "Scholarship"
    RESEARCH = "Research"
    LEADERSHIP = "Leadership"
    COMMUNITY = "Community Service"
    ATHLETIC = "Athletic"
    PROFESSIONAL = "Professional"
    COMPETITION = "Competition"
    EMPTY = ""

class EmploymentTypeEnum(str, Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    TEMPORARY = "Temporary"
    INTERN = "Intern"
    VOLUNTEER = "Volunteer"
    FREELANCE = "Freelance"
    EMPTY = ""
