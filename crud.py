import time
from datetime import datetime
from sqlalchemy import MetaData, Table, select
from schemas import (
    Trial,
    Sponsor,
    TherapeuticArea,
    Country,
    Condition,
    Site,
    Location,
    UpdateHistory,
)
from helper_functions import (
    timestamp_to_date,
    country_to_iso_codes,
)
from api import get_location_coordinates


def get_or_create(session, model, defaults=None, **kwargs):
    """
    Get an instance of the model or create it and add it to session if it doesn't exist.

    Parameters:
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


def delete_table_entries(session, *table_names):
    """
    Delete all entries from the specified tables in the database. Commiting changes has to be handled outside the function.

    Parameters:
    - session: SqlAlchemy database session.
    - table_names (str): Variable length argument list of table names to delete entries from.
    """
    metadata = MetaData()
    metadata.reflect(bind=session.bind)

    for table_name in table_names:
        if table_name in metadata.tables:
            table = Table(table_name, metadata, autoload_with=session.bind)
            # Delete all entries in the table
            session.execute(table.delete())
            print(f"All entries deleted from table '{table_name}'")
        else:
            print(f"Table '{table_name}' does not exist in the database.")


def insert_trial_data(session, trial_overview: dict, trial_details: dict) -> None:
    trial_info = (
        trial_details.get("authorizedApplication")
        .get("authorizedPartI")
        .get("trialDetails")
    )

    trial_title = trial_overview.get("ctTitle")
    trial_short_title = trial_info.get("clinicalTrialIdentifiers").get("shortTitle")
    trial_ct_number = trial_overview.get("ctNumber")
    is_trial_transitioned = (
        trial_details.get("authorizedApplication")
        .get("eudraCt", {})
        .get("isTransitioned")
    )
    trial_eudract = (
        trial_details.get("authorizedApplication").get("eudraCt", {}).get("eudraCtCode")
    )
    trial_nct = (
        trial_info.get("clinicalTrialIdentifiers")
        .get("secondaryIdentifyingNumbers")
        .get("nctNumber", {})
        .get("number")
    )
    trial_status = trial_details.get("ctPublicStatus")
    trial_phase = trial_overview.get("trialPhase")
    trial_age_group = trial_overview.get("ageGroup")
    trial_gender = trial_overview.get("gender")
    trial_region = trial_overview.get("trialRegion")
    trial_recruitment_start_date = (
        trial_info.get("trialInformation")
        .get("trialDuration")
        .get("estimatedRecruitmentStartDate")
    )
    trial_decision_date = timestamp_to_date(trial_details.get("decisionDate"))
    trial_estimated_end_date = (
        trial_info.get("trialInformation").get("trialDuration").get("estimatedEndDate")
    )
    trial_estimated_recruitment = trial_overview.get("totalNumbersEnrolled")
    trial_last_update = trial_overview.get("lastUpdated")

    trial = Trial(
        title=trial_title,
        short_title=trial_short_title,
        ct_number=trial_ct_number,
        is_transitioned=is_trial_transitioned,
        eudract_number=trial_eudract,
        nct_number=trial_nct,
        status=trial_status,
        phase=trial_phase,
        age_group=trial_age_group,
        gender=trial_gender,
        trial_region=trial_region,
        estimated_recruitment_start_date=trial_recruitment_start_date,
        decision_date=trial_decision_date,
        estimated_end_date=trial_estimated_end_date,
        estimated_recruitment=trial_estimated_recruitment,
        last_updated_in_ctis=trial_last_update,
        ctis_url=f"https://euclinicaltrials.eu/search-for-clinical-trials/?lang=en&EUCT={trial_overview.get('ctNumber')}",
    )
    session.add(trial)
    session.flush()

    trial_sites = []
    authorized_parts_2 = trial_details.get("authorizedApplication").get(
        "authorizedPartsII"
    )
    for part in authorized_parts_2:
        sites = part.get("trialSites")
        trial_sites = trial_sites + sites

    for site in trial_sites:
        site_name = site.get("organisationAddressInfo").get("organisation").get("name")
        site_department = site.get("departmentName")
        site_type = site.get("organisationAddressInfo").get("organisation").get("type")
        is_site_commercial = (
            site.get("organisationAddressInfo").get("organisation").get("false")
        )
        site_phone = site.get("organisationAddressInfo").get("phone")
        site_email = site.get("organisationAddressInfo").get("email")
        org_id = site.get("organisationAddressInfo").get("businessKey")
        address = site.get("organisationAddressInfo").get("address").get("addressLine1")
        city = site.get("organisationAddressInfo").get("address").get("city")
        postcode = site.get("organisationAddressInfo").get("address").get("postcode")
        country = site.get("organisationAddressInfo").get("address").get("countryName")

        location_row = get_or_create(
            session,
            Location,
            address=address,
            city=city,
            postcode=postcode,
            country=country,
            country_iso2=country_to_iso_codes(country)[0],
            country_iso3=country_to_iso_codes(country)[1],
            location_one_line=f"{address}, {city}, {country}",
        )

        site_row = get_or_create(
            session,
            Site,
            defaults={
                "name": site_name,
                "department": site_department,
                "type": site_type,
                "commercial": is_site_commercial,
                "phone": site_phone,
                "email": site_email,
            },
            org_id=org_id,
            location=location_row,
        )
        if site_row not in trial.sites:
            trial.sites.append(site_row)

    therapeutic_areas = (
        trial_details.get("authorizedApplication")
        .get("authorizedPartI")
        .get("therapeuticAreas")
    )
    for ta in therapeutic_areas:
        ta_row = get_or_create(session, TherapeuticArea, name=ta.get("name"))
        if ta_row not in trial.therapeutic_areas:
            trial.therapeutic_areas.append(ta_row)

    medical_conditions = (
        trial_details.get("authorizedApplication")
        .get("authorizedPartI")
        .get("trialDetails")
        .get("trialInformation")
        .get("medicalCondition")
        .get("partIMedicalConditions")
    )
    for cond in medical_conditions:
        cond_row = get_or_create(
            session,
            Condition,
            name=cond.get("medicalCondition"),
        )
        if cond_row not in trial.conditions:
            trial.conditions.append(cond_row)

    sponsors = (
        trial_details.get("authorizedApplication")
        .get("authorizedPartI")
        .get("sponsors")
    )
    for sponsor in sponsors:
        sponsor_row = get_or_create(
            session,
            Sponsor,
            defaults={
                "name": sponsor.get("organisation").get("name"),
                "type": sponsor.get("organisation").get("type"),
                "is_primary": sponsor.get("primary"),
            },
            org_id=sponsor.get("organisation").get("businessKey"),
        )
        if sponsor_row not in trial.sponsors:
            trial.sponsors.append(sponsor_row)

    countries = trial_details.get("authorizedApplication").get("memberStatesConcerned")
    for country in countries:
        country_row = get_or_create(
            session,
            Country,
            name=country.get("mscName"),
        )
        if country_row not in trial.countries:
            trial.countries.append(country_row)


def update_location_coordinates(session):
    stmt = select(Location).where(Location.latitude == None)
    result = session.execute(stmt)
    for loc in result.scalars():
        lat, lon = get_location_coordinates(
            street=loc.address,
            city=loc.city,
            country=loc.country,
            postalcode=loc.postcode,
        )
        print(f"lat: {lat}, lon: {lon}")
        loc.latitude = lat
        loc.longitude = lon
        session.commit()
        time.sleep(1)


def insert_update_status(session, update_status: str):
    row = UpdateHistory(update_time=datetime.now(), status=update_status)
    session.add(row)
    session.commit()
