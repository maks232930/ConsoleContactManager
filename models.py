from pydantic import BaseModel


class ContactModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: str
    organization: str
    work_phone: str
    personal_phone: str

    def model_dump_table(self) -> list:
        return [self.id, self.first_name, self.last_name, self.middle_name,
                self.organization, self.work_phone, self.personal_phone]
