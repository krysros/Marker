import factory
import pytest
import transaction

from marker.models import association, company, project


class CompanyFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = company.Company
        sqlalchemy_session_persistence = "flush"
        sqlalchemy_session = None  # will be set in test

    name = factory.Sequence(lambda n: f"TestCo{n}")
    street = ""
    postcode = ""
    city = ""
    subdivision = ""
    country = "PL"
    website = ""
    color = ""
    NIP = ""
    REGON = ""
    KRS = ""
    # court removed


class ProjectFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = project.Project
        sqlalchemy_session_persistence = "flush"
        sqlalchemy_session = None  # will be set in test

    name = factory.Sequence(lambda n: f"TestProj{n}")
    street = ""
    postcode = ""
    city = ""
    subdivision = ""
    country = "PL"
    website = ""
    color = ""
    deadline = factory.LazyFunction(lambda: None)
    stage = ""
    delivery_method = ""


@pytest.mark.usefixtures("dbsession")
def test_company_project_activity_cascade(dbsession):
    CompanyFactory._meta.sqlalchemy_session = dbsession
    ProjectFactory._meta.sqlalchemy_session = dbsession
    comp = CompanyFactory()
    proj = ProjectFactory()
    dbsession.add_all([comp, proj])
    dbsession.flush()
    # create association
    act = association.Activity(company=comp, project=proj, stage="test", role="main")
    dbsession.add(act)
    transaction.commit()
