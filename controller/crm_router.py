from fastapi import APIRouter, Form, UploadFile, Body, File
from pydantic import BaseModel
from typing import Optional, List


from import_services.csv_import import process_csv_file
from repository.company_table_operation import get_all_companies, get_company_by_id, create_company, update_company, \
    delete_multiple_companies, delete_company
from repository.contacts_table_operation import delete_contact, delete_multiple_contacts, update_contact, \
    create_contact, get_contact_by_id, get_all_contacts

router = APIRouter(prefix="/api")


@router.get("/test")
def test_repositories():
    return {"message": "Welcome to the world of Harry Brown"}

# Import routers

@router.post("/upload-csv")
def upload_csv_file(file: UploadFile = File(...), type: str = None):
    return process_csv_file(file, type)

# company


class CompanyCreate(BaseModel):
    name: str
    domain: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    address: Optional[str] = None
    zip: Optional[str] = None
    industry: Optional[str] = None
    numberofemployees: Optional[int] = None
    annualrevenue: Optional[float] = None
    linkedin_company_page: Optional[str] = None
    technology_category: Optional[str] = None
    software_category: Optional[str] = None
    area_of_work: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    address: Optional[str] = None
    zip: Optional[str] = None
    industry: Optional[str] = None
    numberofemployees: Optional[int] = None
    annualrevenue: Optional[float] = None
    linkedin_company_page: Optional[str] = None
    technology_category: Optional[str] = None
    software_category: Optional[str] = None
    area_of_work: Optional[str] = None


class DeleteMultipleRequest(BaseModel):
    ids: List[int]


@router.get("/")
def get_companies(search: str = None, page: int = 1, limit: int = 10):
    return get_all_companies(search=search, page=page, limit=limit)


@router.get("/{company_id}")
def get_company(company_id: int):
    return get_company_by_id(company_id)


@router.post("/")
def create_new_company(data: CompanyCreate):
    return create_company(data.model_dump())


@router.put("/{company_id}")
def update_existing_company(company_id: int, data: CompanyUpdate):
    return update_company(company_id, data.model_dump(exclude_none=True))


@router.delete("/delete-multiple")
def delete_many_companies(data: DeleteMultipleRequest):
    return delete_multiple_companies(data.ids)


@router.delete("/{company_id}")
def delete_single_company(company_id: int):
    return delete_company(company_id)


# Contacts

class ContactCreate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    jobtitle: Optional[str] = None
    job_function: Optional[str] = None
    seniority: Optional[str] = None
    email: str
    mobilephone: Optional[str] = None
    phone: Optional[str] = None
    hs_linkedin_url: Optional[str] = None
    followercount: Optional[int] = None
    linkedinconnections: Optional[int] = None
    country: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    start_date: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    lifecycle_stage: Optional[str] = "NEW"


class ContactUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    jobtitle: Optional[str] = None
    job_function: Optional[str] = None
    seniority: Optional[str] = None
    email: Optional[str] = None
    mobilephone: Optional[str] = None
    phone: Optional[str] = None
    hs_linkedin_url: Optional[str] = None
    followercount: Optional[int] = None
    linkedinconnections: Optional[int] = None
    country: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    start_date: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    lifecycle_stage: Optional[str] = None


class DeleteMultipleRequest(BaseModel):
    ids: List[int]


@router.get("/")
def get_contacts(search: str = None, page: int = 1, limit: int = 10):
    return get_all_contacts(search=search, page=page, limit=limit)


@router.get("/{contact_id}")
def get_contact(contact_id: int):
    return get_contact_by_id(contact_id)


@router.post("/")
def create_new_contact(data: ContactCreate):
    return create_contact(data.model_dump())


@router.put("/{contact_id}")
def update_existing_contact(contact_id: int, data: ContactUpdate):
    return update_contact(contact_id, data.model_dump(exclude_none=True))


@router.delete("/delete-multiple")
def delete_many_contacts(data: DeleteMultipleRequest):
    return delete_multiple_contacts(data.ids)


@router.delete("/{contact_id}")
def delete_single_contact(contact_id: int):
    return delete_contact(contact_id)




