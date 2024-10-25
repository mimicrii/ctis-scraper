import time
from datetime import datetime
from typing import TypeVar, cast, List, Final, Dict, Type

import yaml
from sqlalchemy import select, create_engine, MetaData, text, func
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.exc import OperationalError
from tqdm import tqdm

from src.schemas import (
    Base,
    Trial,
    Sponsor,
    ThirdParty,
    Duty,
    Product,
    Substance,
    AdministrationRoute,
    TherapeuticArea,
    Condition,
    Site,
    Location,
    SeriousBreach,
    Category,
    ImpactedArea,
    UpdateHistory,
)
from src.log import logger
from src.parse import TrialOverview, FullTrial
from src.helpers import timestamp_to_date, country_to_iso_codes, decode_third_party_duty
from src.api import (
    get_location_coordinates,
    get_total_trial_records,
    get_trial_overview,
    get_full_trial,
)


with open("decodings.yaml", "r") as file:
    DECODINGS = yaml.safe_load(file)

with open("config.yaml", "r") as file:
    CONFIG = yaml.safe_load(file)

THIRD_PARTY_DUTY_DECODINGS: Final[Dict] = DECODINGS["third_party_duty"]


def get_or_create(
    session: Session, model: Type[DeclarativeMeta], defaults=None, **kwargs
) -> Type[DeclarativeMeta]:
    """
    Get an instance of the model or create it and add it to session if it doesn't exist.

    Parameter:
        session (Session): SQLAlchemy session object.
        model (Base): SQLAlchemy model class.
        defaults (dict, optional): A dictionary of default values to use if creating a new instance.
        **kwargs: The criteria to search the existing record.

    Returns:
        instance: The instance of the model found or created.
    """
    instance = session.query(model).filter_by(**kwargs).first()

    if instance:
        return instance

    else:
        params = {**kwargs}
        if defaults:
            params.update(defaults)

        instance = model(**params)
        session.add(instance)
        return instance


def drop_tables(session: Session, tables_to_keep: list[str], dialect: str) -> None:
    """
    Drops all tables in the database except those specified in tables_to_keep.

    Parameter:
        session: The SQLAlchemy session to use.
        tables_to_keep: List of table names to keep.
    """

    inspector = inspect(session.bind)
    all_tables = inspector.get_table_names()

    for table in all_tables:
        if table not in tables_to_keep:
            if dialect == "postgresql":
                drop_statement = f"DROP TABLE IF EXISTS {table} CASCADE;"
                session.execute(text(drop_statement))
            else:
                drop_statement = f"DROP TABLE IF EXISTS {table};"
                session.execute(text(drop_statement))

    logger.info(f"Dropped {len(all_tables) - len(tables_to_keep)} tables.")


def delete_all_except(session, tables_to_keep):
    """
    Delete all rows from all tables in the database except the specified tables.

    Parameter:
        session: The SQLAlchemy session to use.
        tables_to_keep: List of table names to keep.
    """

    try:
        metadata = MetaData()
        metadata.reflect(bind=session.bind)

        tables_to_keep_set = set(tables_to_keep)

        for table_name in metadata.tables.keys():
            if table_name not in tables_to_keep_set:
                table = metadata.tables[table_name]

                session.execute(table.delete())
                logger.info(f"Deleted all rows from table: {table_name}")

        session.commit()
        logger.info("All rows deleted except from the specified tables.")

    except Exception as e:
        logger.info(f"An error occurred: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def insert_trial_data(
    session: Session, trial_overview: TrialOverview, full_trial: FullTrial
) -> None:
    """
    Inserts scraped trial data into database.

    Parameter:
    - trial_overview: Instance of TrialOverview dataclass. Overview of trial scraped from overview api endpoint.
    - full_trial: Instance of FullTrial dataclass. Detailed information scraped from the trial details api endpoint.
    """

    trial_details = full_trial.authorizedApplication.authorizedPartI.trialDetails

    trial_title = trial_overview.ctTitle
    trial_short_title = trial_details.clinicalTrialIdentifiers.shortTitle
    trial_ct_number = trial_overview.ctNumber
    is_trial_transitioned = full_trial.authorizedApplication.eudraCt.isTransitioned
    trial_eudract = full_trial.authorizedApplication.eudraCt.eudraCtCode
    trial_nct = (
        trial_details.clinicalTrialIdentifiers.secondaryIdentifyingNumbers.nctNumber.number
    )
    trial_status = full_trial.ctStatus
    trial_public_status_code = full_trial.ctPublicStatusCode
    trial_phase = trial_overview.trialPhase
    trial_age_group = trial_overview.ageGroup
    trial_gender = trial_overview.gender
    trial_region = trial_overview.trialRegion
    trial_recruitment_start_date = (
        trial_details.trialInformation.trialDuration.estimatedRecruitmentStartDate
    )
    trial_recruitment_start_date = datetime.strptime(
        trial_recruitment_start_date, "%Y-%m-%d"
    ).date()
    trial_decision_date = timestamp_to_date(full_trial.decisionDate)
    trial_estimated_end_date = (
        trial_details.trialInformation.trialDuration.estimatedEndDate
    )
    trial_end_date_eu = full_trial.endDateEU
    if trial_end_date_eu:
        trial_end_date_eu = datetime.strptime(trial_end_date_eu, "%Y-%m-%d").date()
    trial_start_date_eu = full_trial.startDateEU
    if trial_start_date_eu:
        trial_start_date_eu = datetime.strptime(trial_start_date_eu, "%Y-%m-%d").date()
    trial_estimated_end_date = datetime.strptime(
        trial_estimated_end_date, "%Y-%m-%d"
    ).date()
    trial_estimated_recruitment = trial_overview.totalNumberEnrolled
    trial_last_update = trial_overview.lastUpdated
    trial_last_update = datetime.strptime(trial_last_update, "%d/%m/%Y").date()

    trial = Trial(
        title=trial_title,
        short_title=trial_short_title,
        ct_number=trial_ct_number,
        is_transitioned=is_trial_transitioned,
        eudract_number=trial_eudract,
        nct_number=trial_nct,
        status=trial_status,
        public_status_code=trial_public_status_code,
        phase=trial_phase,
        age_group=trial_age_group,
        gender=trial_gender,
        trial_region=trial_region,
        estimated_recruitment_start_date=trial_recruitment_start_date,
        decision_date=trial_decision_date,
        estimated_end_date=trial_estimated_end_date,
        start_date_eu=trial_start_date_eu,
        end_date_eu=trial_end_date_eu,
        estimated_recruitment=trial_estimated_recruitment,
        last_updated_in_ctis=trial_last_update,
        ctis_url=f"https://euclinicaltrials.eu/search-for-clinical-trials/?lang=en&EUCT={trial_overview.ctNumber}",
    )
    session.add(trial)
    session.flush()

    trial_sites = []
    authorized_parts_2 = full_trial.authorizedApplication.authorizedPartsII

    for part in authorized_parts_2:
        sites = part.trialSites
        trial_sites = trial_sites + sites

    for site in trial_sites:
        site_name = site.organisationAddressInfo.organisation.name
        site_type = site.organisationAddressInfo.organisation.type
        is_site_commercial = site.organisationAddressInfo.organisation.commercial
        site_phone = site.organisationAddressInfo.phone
        site_email = site.organisationAddressInfo.email
        site_org_id = site.organisationAddressInfo.organisation.businessKey
        site_address = site.organisationAddressInfo.address.addressLine1
        site_city = site.organisationAddressInfo.address.city
        site_postcode = site.organisationAddressInfo.address.postcode
        site_country = site.organisationAddressInfo.address.countryName

        site_location_row = get_or_create(
            session,
            Location,
            address=site_address,
            city=site_city,
            postcode=site_postcode,
            country=site_country,
            country_iso2=country_to_iso_codes(site_country)[0],
            country_iso3=country_to_iso_codes(site_country)[1],
            location_one_line=f"{site_address}, {site_city}, {site_country}",
        )

        site_row = get_or_create(
            session,
            Site,
            defaults={
                "name": site_name,
                "type": site_type,
                "commercial": is_site_commercial,
                "phone": site_phone,
                "email": site_email,
            },
            org_id=site_org_id,
            location=site_location_row,
        )
        if site_row not in trial.sites:
            trial.sites.append(site_row)

    therapeutic_areas = (
        full_trial.authorizedApplication.authorizedPartI.therapeuticAreas
    )

    for ta in therapeutic_areas:
        ta_row = get_or_create(session, TherapeuticArea, name=ta.name)
        if ta_row not in trial.therapeutic_areas:
            trial.therapeutic_areas.append(ta_row)

    medical_conditions = (
        trial_details.trialInformation.medicalCondition.partIMedicalConditions
    )
    for cond in medical_conditions:
        cond_row = get_or_create(
            session,
            Condition,
            name=cond.medicalCondition,
        )
        if cond_row not in trial.conditions:
            trial.conditions.append(cond_row)

    sponsors = full_trial.authorizedApplication.authorizedPartI.sponsors
    for sponsor in sponsors:
        sponsor_row = get_or_create(
            session,
            Sponsor,
            defaults={
                "name": sponsor.organisation.name,
                "type": sponsor.organisation.type,
            },
            is_primary=sponsor.primary,
            org_id=sponsor.organisation.businessKey,
        )
        if sponsor_row not in trial.sponsors:
            trial.sponsors.append(sponsor_row)

        third_parties = sponsor.thirdParties
        if third_parties:
            for third_party in third_parties:
                tp_name = third_party.organisationAddress.organisation.name
                tp_type = third_party.organisationAddress.organisation.type
                tp_is_commercial = (
                    third_party.organisationAddress.organisation.commercial
                )
                tp_org_id = third_party.organisationAddress.organisation.businessKey
                tp_address = third_party.organisationAddress.address.addressLine1
                tp_city = third_party.organisationAddress.address.city
                tp_country = third_party.organisationAddress.address.countryName
                tp_postcode = third_party.organisationAddress.address.postcode

                tp_location_row = get_or_create(
                    session,
                    Location,
                    address=tp_address,
                    city=tp_city,
                    postcode=tp_postcode,
                    country=tp_country,
                    country_iso2=country_to_iso_codes(tp_country)[0],
                    country_iso3=country_to_iso_codes(tp_country)[1],
                    location_one_line=f"{tp_address}, {tp_city}, {tp_country}",
                )
                third_party_row = get_or_create(
                    session,
                    ThirdParty,
                    name=tp_name,
                    type=tp_type,
                    is_commercial=tp_is_commercial,
                    org_id=tp_org_id,
                    location=tp_location_row,
                )
                if third_party_row not in trial.third_parties:
                    trial.third_parties.append(third_party_row)

                tp_duties = third_party.sponsorDuties
                if tp_duties:
                    for duty in tp_duties:
                        duty_code = duty.code
                        duty_value = decode_third_party_duty(
                            duty, THIRD_PARTY_DUTY_DECODINGS
                        )
                        duty_row = get_or_create(
                            session, Duty, code=duty_code, name=duty_value
                        )
                        if duty_row not in third_party_row.duties:
                            third_party_row.duties.append(duty_row)

    products = full_trial.authorizedApplication.authorizedPartI.products
    if products:
        for product in products:
            p_name = product.productName
            p_active_substance = product.productDictionaryInfo.activeSubstanceName
            p_name_org = product.productDictionaryInfo.nameOrg
            p_pharmaceutical_form_display = product.pharmaceuticalFormDisplay
            p_is_paediatric_formulation = product.isPaediatricFormulation
            p_role_in_trial_code = product.mpRoleInTrial  # TODO: Decode role code
            p_orphan_drug = product.orphanDrugEdit
            p_ev_code = product.evCode
            p_eu_mp_number = product.productDictionaryInfo.euMpNumber
            p_sponsor_product_code = product.productDictionaryInfo.sponsorProductCode

            product_row = get_or_create(
                session,
                Product,
                name=p_name,
                active_substance=p_active_substance,
                name_org=p_name_org,
                pharmaceutical_form_display=p_pharmaceutical_form_display,
                is_paediatric_formulation=p_is_paediatric_formulation,
                role_in_trial_code=p_role_in_trial_code,
                orphan_drug=p_orphan_drug,
                ev_code=p_ev_code,
                eu_mp_number=p_eu_mp_number,
                sponsor_product_code=p_sponsor_product_code,
            )
            if product_row not in trial.products:
                trial.products.append(product_row)

            substances = product.productDictionaryInfo.productSubstances
            if substances:
                for substance in substances:
                    s_name = substance.actSubstName
                    s_ev_code = substance.substanceEvCode
                    s_origin = substance.substanceOrigin
                    s_act_substance_origin = substance.actSubstOrigin
                    s_product_pk = substance.productPk
                    s_pk = substance.substancePk

                    substance_row = get_or_create(
                        session,
                        Substance,
                        name=s_name,
                        ev_code=s_ev_code,
                        substance_origin=s_origin,
                        act_substance_origin=s_act_substance_origin,
                        product_pk=s_product_pk,
                        substance_pk=s_pk,
                    )
                    if substance_row not in product_row.substances:
                        product_row.substances.append(substance_row)

            administration_routes = product.routes
            if administration_routes:
                for route in administration_routes:
                    route_row = get_or_create(session, AdministrationRoute, name=route)
                    if route_row not in product_row.administration_routes:
                        product_row.administration_routes.append(route_row)

    serious_breaches = full_trial.events.seriousBreaches
    if serious_breaches:
        for sb in serious_breaches:
            sb_aware_date = (
                datetime.strptime(sb.awareDate, "%Y-%m-%d").date()
                if sb.awareDate
                else None
            )
            sb_breach_date = (
                datetime.strptime(sb.breachDate, "%Y-%m-%d").date()
                if sb.breachDate
                else None
            )
            sb_subm_date = (
                datetime.strptime(sb.submissionDate, "%Y-%m-%d").date()
                if sb.submissionDate
                else None
            )
            sb_updated_on = (
                datetime.strptime(sb.updatedOn, "%Y-%m-%d").date()
                if sb.updatedOn
                else None
            )
            sb_description = sb.description
            sb_actions_taken = sb.actionsTaken
            sb_benefit_risk_balanced_changed = sb.isBenefitRiskBalanceChanged
            sb_impacted_areas = sb.impactedAreaList
            sb_categories = sb.categories
            sb_sites = sb.seriousBreachSites

            sb_row = get_or_create(
                session,
                SeriousBreach,
                aware_date=sb_aware_date,
                breach_date=sb_breach_date,
                submission_date=sb_subm_date,
                updated_on=sb_updated_on,
                description=sb_description,
                actions_taken=sb_actions_taken,
                benefit_risk_balance_changed=sb_benefit_risk_balanced_changed,
                trial=trial,
            )
            if sb_row not in trial.serious_breaches:
                trial.serious_breaches.append(sb_row)

            if sb_impacted_areas:
                for area in sb_impacted_areas:
                    impacted_area_row = get_or_create(session, ImpactedArea, name=area)
                    if impacted_area_row not in sb_row.impacted_areas:
                        sb_row.impacted_areas.append(impacted_area_row)

            if sb_categories:
                for category in sb_categories:
                    category_row = get_or_create(session, Category, name=category.name)
                    if category_row not in sb_row.categories:
                        sb_row.categories.append(category_row)

            if sb_sites:
                for sb_site in sb_sites:
                    corresponding_site = (
                        session.query(Site)
                        .filter(
                            Site.org_id == sb_site.organisationAddressInfo.businessKey
                        )
                        .first()
                    )
                    if corresponding_site and corresponding_site not in sb_row.sites:
                        sb_row.sites.append(corresponding_site)


def update_location_coordinates(database_uri: str) -> None:
    """
    Gets lat and lon for all entries in location table that are empty in lat and lon column and have not been used for an api call. Updates the table respectivly

    Parameter:
    - database_uri: SQLAlchemy database connection string in the format: postgresql+psycopg2://username:password@db_ip:db_port/db_name
    """
    engine = create_engine(database_uri)
    Session = sessionmaker(engine)
    logger.info("Updating Location coordinates...")
    with Session() as session:
        count_stmt = select(func.count()).where(
            Location.latitude == None, Location.geocodeable == None
        )
        total_count = session.execute(count_stmt).scalar()

        stmt = select(Location).where(
            Location.latitude == None, Location.geocodeable == None
        )
        result = session.execute(stmt)
        for loc in tqdm(result.scalars(), total=total_count):
            lat, lon = get_location_coordinates(
                street=loc.address,
                city=loc.city,
                country=loc.country,
                postalcode=loc.postcode,
            )
            if not lat and not lon:
                loc.latitude = None
                loc.latitude = None
                loc.geocodeable = False
                session.commit()
                time.sleep(2)
            else:
                loc.latitude = lat
                loc.longitude = lon
                loc.geocodeable = True
                session.commit()
                time.sleep(2)


def insert_update_status(session: Session, update_status: str) -> None:
    row = UpdateHistory(update_time=datetime.now(), status=update_status)
    session.add(row)
    session.commit()


def scrape_ctis(database_uri: str) -> None:
    """
    Wraps the entire data scraping, parsing and insertion process into a single function.

    Parameter:
    - database_uri: SQLAlchemy database connection string in the format: postgresql+psycopg2://username:password@db_ip:db_port/db_name
    """

    total_trial_records = get_total_trial_records()
    environment = CONFIG["environment"]
    if environment == "dev":
        sql_dialect = "sqlite"
    elif environment == "prod":
        sql_dialect = "postgresql"
    else:
        raise ValueError(
            f"Wrong environment configuration ({environment}). Choose either 'dev' or 'prod'"
        )

    engine = create_engine(database_uri)
    Session = sessionmaker(engine)
    session = Session()
    try:
        drop_tables(
            session=session,
            tables_to_keep=["location", "update_history"],
            dialect=sql_dialect,
        )
        session.commit()

        Base.metadata.create_all(engine)

        for trial_overview in tqdm(get_trial_overview(), total=total_trial_records):
            full_trial = get_full_trial(trial_overview.ctNumber)
            insert_trial_data(
                session=session,
                trial_overview=trial_overview,
                full_trial=full_trial,
            )
            session.commit()
        session.commit()
        insert_update_status(session, "Update successful")

    except Exception as e:
        insert_update_status(session, f"Update failed - {type(e).__name__}")
        raise

    finally:
        session.close()
