import time
from datetime import datetime
from typing import TypeVar, cast, List
from sqlalchemy import MetaData, select, text
from sqlalchemy.orm import Session
from schemas import (
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
    UpdateHistory,
)
from helper_functions import (
    timestamp_to_date,
    country_to_iso_codes,
)
from api import get_location_coordinates

Model = TypeVar("Model")


def get_or_create(session: Session, model: Model, defaults=None, **kwargs) -> Model:
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
        return cast(Model, instance)

    else:
        params = {**kwargs}
        if defaults:
            params.update(defaults)

        instance = model(**params)
        session.add(instance)
        return cast(Model, instance)


def delete_table_entries(
    session: Session, table_names: List[str], delete_all_except: bool = False
) -> None:
    """
    Drop tables with CASCADE from the specified tables or from all tables except the specified ones in the database.
    Committing changes has to be handled outside the function.

    Parameters:
    - session: SQLAlchemy database session.
    - table_names (list): List of table names to drop.
    - delete_all_except (bool): If True, drop all tables except those specified.
                                If False, drop only the specified tables.
    """
    metadata = MetaData()
    metadata.reflect(bind=session.bind)

    if delete_all_except:
        tables_to_delete = [
            table for table in metadata.tables.values() if table.name not in table_names
        ]
    else:
        tables_to_delete = [
            table for table in metadata.tables.values() if table.name in table_names
        ]

    for table in tables_to_delete:
        print(f"Dropping table '{table.name}' with CASCADE ...")
        session.execute(text(f"DROP TABLE {table.name} CASCADE"))

    if not tables_to_delete:
        print("No tables matched the given criteria.")


def insert_trial_data(
    session: Session, trial_overview: dict, trial_details: dict
) -> None:
    """
    Inserts scraped trial data into database.

    Parameters:
    - trial_overview: Overview of trial scraped from overview api endpoint.
    - trial_details: Trial details. Full response from the trial details api endpoint.
    """

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
        site_type = site.get("organisationAddressInfo").get("organisation").get("type")
        is_site_commercial = (
            site.get("organisationAddressInfo").get("organisation").get("false")
        )
        site_phone = site.get("organisationAddressInfo").get("phone")
        site_email = site.get("organisationAddressInfo").get("email")
        site_org_id = site.get("organisationAddressInfo").get("businessKey")
        site_address = (
            site.get("organisationAddressInfo").get("address").get("addressLine1")
        )
        site_city = site.get("organisationAddressInfo").get("address").get("city")
        site_postcode = (
            site.get("organisationAddressInfo").get("address").get("postcode")
        )
        site_country = (
            site.get("organisationAddressInfo").get("address").get("countryName")
        )

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

        third_parties = sponsor.get("thirdParties")
        if third_parties:
            for third_party in third_parties:
                tp_name = (
                    third_party.get("organisationAddress")
                    .get("organisation")
                    .get("name")
                )
                tp_type = (
                    third_party.get("organisationAddress")
                    .get("organisation")
                    .get("type")
                )
                tp_is_commercial = (
                    third_party.get("organisationAddress")
                    .get("organisation")
                    .get("commercial")
                )
                tp_org_id = (
                    third_party.get("organisationAddress")
                    .get("organisation")
                    .get("businessKey")
                )
                tp_address = (
                    third_party.get("organisationAddress")
                    .get("address")
                    .get("addressLine1")
                )
                tp_city = (
                    third_party.get("organisationAddress").get("address").get("city")
                )
                tp_country = (
                    third_party.get("organisationAddress")
                    .get("address")
                    .get("countryName")
                )
                tp_postcode = (
                    third_party.get("organisationAddress")
                    .get("address")
                    .get("postcode")
                )

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

                tp_duties = third_party.get("sponsorDuties")
                if tp_duties:
                    for duty in tp_duties:
                        duty_row = get_or_create(session, Duty, code=duty.get("code"))
                        if duty_row not in third_party_row.duties:
                            third_party_row.duties.append(duty_row)

    products = (
        trial_details.get("authorizedApplication")
        .get("authorizedPartI")
        .get("products")
    )
    if products:
        for product in products:
            p_name = product.get("prodName")
            p_active_substance = product.get("productDictionaryInfo").get(
                "activeSubstanceName"
            )
            p_name_org = product.get("productDictionaryInfo").get("nameOrg")
            p_pharmaceutical_form_display = product.get("pharmaceuticalFormDisplay")
            p_is_paediatric_formulation = product.get("isPaediatricFormulation")
            p_role_in_trial_code = product.get("mpRoleInTrial")
            p_orphan_drug = product.get("orphanDrugEdit")
            p_ev_code = product.get("evCode")
            p_eu_mp_number = product.get("euMpNumber")
            p_sponsor_product_code = product.get("productDictionaryInfo").get(
                "sponsorProductCode"
            )

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

            substances = product.get("productSubstances")
            if substances:
                for substance in substances:
                    s_name = substance.get("actSubstName")
                    s_ev_code = substance.get("substanceEvCode")
                    s_origin = substance.get("substanceOrigin")
                    s_act_substance_origin = substance.get("actSubstOrigin")
                    s_product_pk = substance.get("productPk")
                    s_pk = substance.get("substancePk")

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

                    administration_routes = product.get("routes")
                    if administration_routes:
                        for route in administration_routes:
                            route_row = get_or_create(
                                session, AdministrationRoute, name=route
                            )
                            if route_row not in product_row.administration_routes:
                                product_row.administration_routes.append(route_row)


def update_location_coordinates(session) -> None:
    """
    Gets lat and lon for all entries in location table that are empty in lat and lon column and updates the table respectivly

    Parameter:
    - session: SQLAlchemy database session
    """
    stmt = select(Location).where(Location.latitude == None)
    result = session.execute(stmt)
    for loc in result.scalars():
        lat, lon = get_location_coordinates(
            street=loc.address,
            city=loc.city,
            country=loc.country,
            postalcode=loc.postcode,
        )
        loc.latitude = lat
        loc.longitude = lon
        session.commit()
        time.sleep(1)


def insert_update_status(session: Session, update_status: str) -> None:
    row = UpdateHistory(update_time=datetime.now(), status=update_status)
    session.add(row)
    session.commit()
