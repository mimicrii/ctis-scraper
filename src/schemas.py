from datetime import date, datetime
from typing import List
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Column, Table
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase


# Base class that other classes inherit from
class Base(DeclarativeBase):
    pass


# junction tables
trialsponsor = Table(
    "trialsponsor",
    Base.metadata,
    Column(
        "trial_id",
        ForeignKey("trial.id"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "sponsor_id",
        ForeignKey("sponsor.id"),
        primary_key=True,
        nullable=False,
    ),
)

trialthirdparty = Table(
    "trialthirdparty",
    Base.metadata,
    Column(
        "trial_id",
        ForeignKey("trial.id"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "third_party_id",
        ForeignKey("third_party.id"),
        primary_key=True,
        nullable=False,
    ),
)

trialcondition = Table(
    "trialcondition",
    Base.metadata,
    Column(
        "trial_id",
        ForeignKey("trial.id"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "condition_id",
        ForeignKey("condition.id"),
        primary_key=True,
        nullable=False,
    ),
)


trialsite = Table(
    "trialsite",
    Base.metadata,
    Column(
        "trial_id",
        ForeignKey("trial.id"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "site_id",
        ForeignKey("site.id"),
        primary_key=True,
        nullable=False,
    ),
)


trialtherapeuticarea = Table(
    "trialarea",
    Base.metadata,
    Column("trial_id", ForeignKey("trial.id"), primary_key=True, nullable=False),
    Column(
        "therapeutic_area_id",
        ForeignKey("therapeutic_area.id"),
        primary_key=True,
        nullable=False,
    ),
)

trialproduct = Table(
    "trialproduct",
    Base.metadata,
    Column("trial_id", ForeignKey("trial.id"), primary_key=True, nullable=False),
    Column(
        "product_id",
        ForeignKey("product.id"),
        primary_key=True,
        nullable=False,
    ),
)


productadministrationroutes = Table(
    "productadministrationroutes",
    Base.metadata,
    Column("product_id", ForeignKey("product.id"), primary_key=True, nullable=False),
    Column(
        "administration_route_id",
        ForeignKey("administration_route.id"),
        primary_key=True,
        nullable=False,
    ),
)

productsubstance = Table(
    "productsubstance",
    Base.metadata,
    Column("product_id", ForeignKey("product.id"), primary_key=True, nullable=False),
    Column(
        "substance_id",
        ForeignKey("substance.id"),
        primary_key=True,
        nullable=False,
    ),
)

thirdpartyduty = Table(
    "thirdpartyduty",
    Base.metadata,
    Column(
        "third_party_id", ForeignKey("third_party.id"), primary_key=True, nullable=False
    ),
    Column(
        "duty_id",
        ForeignKey("duty.id"),
        primary_key=True,
        nullable=False,
    ),
)

seriousbreachimpactedarea = Table(
    "seriousbreachimpactedarea",
    Base.metadata,
    Column(
        "serious_breach_id",
        ForeignKey("serious_breach.id"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "impacted_area_id",
        ForeignKey("impacted_area.id"),
        primary_key=True,
        nullable=False,
    ),
)

seriousbreachcategory = Table(
    "seriousbreachcategory",
    Base.metadata,
    Column(
        "serious_breach_id",
        ForeignKey("serious_breach.id"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "category_id",
        ForeignKey("category.id"),
        primary_key=True,
        nullable=False,
    ),
)

seriousbreachsites = Table(
    "seriousbreachsites",
    Base.metadata,
    Column(
        "serious_breach_id",
        ForeignKey("serious_breach.id"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "site_id",
        ForeignKey("site.id"),
        primary_key=True,
        nullable=False,
    ),
)


# data tables
class Trial(Base):
    __tablename__ = "trial"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String, index=True)
    short_title: Mapped[Optional[str]]
    ct_number: Mapped[str] = mapped_column(
        String, nullable=False, unique=True, index=True
    )
    is_transitioned: Mapped[Optional[bool]]
    eudract_number: Mapped[Optional[str]]
    nct_number: Mapped[Optional[str]]
    status: Mapped[Optional[str]]
    public_status_code: Mapped[Optional[str]]  # TODO: Decode public status
    phase: Mapped[str]
    age_group: Mapped[Optional[str]]
    gender: Mapped[Optional[str]]
    trial_region: Mapped[Optional[str]]
    estimated_recruitment_start_date: Mapped[Optional[date]]
    decision_date: Mapped[Optional[date]]
    estimated_end_date: Mapped[Optional[date]]
    start_date_eu: Mapped[Optional[date]]
    end_date_eu: Mapped[Optional[date]]
    estimated_recruitment: Mapped[Optional[int]]
    last_updated_in_ctis: Mapped[date]
    ctis_url: Mapped[str]
    # n:1
    serious_breaches: Mapped[List["SeriousBreach"]] = relationship(
        back_populates="trial", cascade="all, delete"
    )
    # m:n
    sponsors: Mapped[List["Sponsor"]] = relationship(
        secondary=trialsponsor, back_populates="trials", cascade="all, delete"
    )
    third_parties: Mapped[List["ThirdParty"]] = relationship(
        secondary=trialthirdparty, back_populates="trials", cascade="all, delete"
    )
    conditions: Mapped[List["Condition"]] = relationship(
        secondary=trialcondition, back_populates="trials", cascade="all, delete"
    )
    sites: Mapped[List["Site"]] = relationship(
        secondary=trialsite, back_populates="trials", cascade="all, delete"
    )
    products: Mapped[List["Product"]] = relationship(
        secondary=trialproduct, back_populates="trials", cascade="all, delete"
    )
    therapeutic_areas: Mapped[List["TherapeuticArea"]] = relationship(
        secondary=trialtherapeuticarea,
        back_populates="trials",
        cascade="all, delete",
    )


class Product(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(index=True)
    active_substance: Mapped[Optional[str]]
    name_org: Mapped[Optional[str]]
    pharmaceutical_form_display: Mapped[Optional[str]]
    is_paediatric_formulation: Mapped[Optional[bool]]
    role_in_trial_code: Mapped[int]
    orphan_drug: Mapped[Optional[bool]]
    ev_code: Mapped[Optional[str]]
    eu_mp_number: Mapped[Optional[str]]
    sponsor_product_code: Mapped[Optional[str]]
    # m:n
    trials: Mapped[List["Trial"]] = relationship(
        secondary=trialproduct, back_populates="products"
    )
    substances: Mapped[List["Substance"]] = relationship(
        secondary=productsubstance,
        back_populates="products",
        cascade="all, delete",
    )
    administration_routes: Mapped[List["AdministrationRoute"]] = relationship(
        secondary=productadministrationroutes,
        back_populates="products",
        cascade="all, delete",
    )


class Substance(Base):
    __tablename__ = "substance"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(index=True)
    ev_code: Mapped[Optional[str]]
    substance_origin: Mapped[Optional[str]]
    act_substance_origin: Mapped[Optional[str]]
    product_pk: Mapped[Optional[str]]
    substance_pk: Mapped[Optional[str]]
    # m:n
    products: Mapped[List["Product"]] = relationship(
        secondary=productsubstance,
        back_populates="substances",
        cascade="all, delete",
    )


class AdministrationRoute(Base):
    __tablename__ = "administration_route"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str]
    # m:n
    products: Mapped[List["Product"]] = relationship(
        secondary=productadministrationroutes,
        back_populates="administration_routes",
    )


class Sponsor(Base):
    __tablename__ = "sponsor"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(index=True)
    type: Mapped[Optional[str]]
    is_primary: Mapped[bool]
    org_id: Mapped[str] = mapped_column(index=True)
    # m:n
    trials: Mapped[List["Trial"]] = relationship(
        secondary=trialsponsor, back_populates="sponsors"
    )


class ThirdParty(Base):
    __tablename__ = "third_party"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(index=True)
    type: Mapped[str]
    is_commercial: Mapped[bool]
    org_id: Mapped[Optional[str]]
    location_id = mapped_column(ForeignKey("location.id"), nullable=False)
    # 1:n
    location: Mapped["Location"] = relationship(
        back_populates="third_parties", cascade="all, delete"
    )
    # m:n
    trials: Mapped[List["Trial"]] = relationship(
        secondary=trialthirdparty,
        back_populates="third_parties",
    )
    duties: Mapped[List["Duty"]] = relationship(
        secondary=thirdpartyduty,
        back_populates="third_parties",
        cascade="all, delete",
    )


class Duty(Base):
    __tablename__ = "duty"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[Optional[str]]
    code: Mapped[int]
    # m:n
    third_parties: Mapped[List["ThirdParty"]] = relationship(
        secondary=thirdpartyduty,
        back_populates="duties",
    )


class TherapeuticArea(Base):
    __tablename__ = "therapeutic_area"
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str]
    # m:n
    trials: Mapped[List["Trial"]] = relationship(
        secondary=trialtherapeuticarea,
        back_populates="therapeutic_areas",
    )


class Condition(Base):
    __tablename__ = "condition"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, index=True)
    # m:n
    trials: Mapped[List["Trial"]] = relationship(
        secondary=trialcondition,
        back_populates="conditions",
    )


class Site(Base):
    __tablename__ = "site"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(index=True)
    type: Mapped[Optional[str]]
    commercial: Mapped[Optional[bool]]
    phone: Mapped[Optional[str]]
    email: Mapped[Optional[str]]
    org_id: Mapped[Optional[str]] = mapped_column(index=True)
    location_id = mapped_column(ForeignKey("location.id"), nullable=False)
    # 1:n
    location: Mapped["Location"] = relationship(
        back_populates="sites",
    )
    # m:n
    trials: Mapped[List["Trial"]] = relationship(
        secondary=trialsite,
    )
    serious_breaches: Mapped[List["SeriousBreach"]] = relationship(
        secondary=seriousbreachsites,
        back_populates="sites",
    )


class Location(Base):
    __tablename__ = "location"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    address: Mapped[str]
    city: Mapped[Optional[str]]
    postcode: Mapped[Optional[str]]
    country: Mapped[Optional[str]]
    country_iso2: Mapped[Optional[str]]
    country_iso3: Mapped[Optional[str]]
    location_one_line: Mapped[Optional[str]]
    latitude: Mapped[Optional[float]]
    longitude: Mapped[Optional[float]]
    geocodeable: Mapped[Optional[bool]]
    # 1:n
    sites: Mapped[List["Site"]] = relationship(back_populates="location")
    third_parties: Mapped[List["ThirdParty"]] = relationship(back_populates="location")


class ImpactedArea(Base):
    __tablename__ = "impacted_area"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str]
    # m:n
    serious_breaches: Mapped[List["SeriousBreach"]] = relationship(
        secondary=seriousbreachimpactedarea,
        back_populates="impacted_areas",
    )


class Category(Base):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str]
    # m:n
    serious_breaches: Mapped[List["SeriousBreach"]] = relationship(
        secondary=seriousbreachcategory,
        back_populates="categories",
    )


class SeriousBreach(Base):
    __tablename__ = "serious_breach"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    aware_date: Mapped[Optional[date]]
    breach_date: Mapped[Optional[date]]
    submission_date: Mapped[Optional[date]]
    updated_on: Mapped[Optional[date]]
    description: Mapped[Optional[str]]
    actions_taken: Mapped[Optional[str]]
    benefit_risk_balance_changed: Mapped[bool]
    trial_id = mapped_column(ForeignKey("trial.id"), nullable=False)
    # 1:n
    trial: Mapped["Trial"] = relationship(
        back_populates="serious_breaches", cascade="all, delete"
    )
    # m:n
    impacted_areas: Mapped[List["ImpactedArea"]] = relationship(
        secondary=seriousbreachimpactedarea,
        back_populates="serious_breaches",
        cascade="all, delete",
    )
    categories: Mapped[List["Category"]] = relationship(
        secondary=seriousbreachcategory,
        back_populates="serious_breaches",
        cascade="all, delete",
    )
    sites: Mapped[List["Site"]] = relationship(
        secondary=seriousbreachsites,
        back_populates="serious_breaches",
        cascade="all, delete",
    )


class UpdateHistory(Base):
    __tablename__ = "update_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    update_time: Mapped[datetime]
    status: Mapped[str]
