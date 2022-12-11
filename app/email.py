from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel
from . import models
from .config import settings
from jinja2 import Environment, select_autoescape, PackageLoader


env = Environment(
    loader=PackageLoader('app', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


class EmailSchema(BaseModel):
    email: List[EmailStr]


class Email:
    def __init__(self, user: models.User, url: str, email: List[EmailStr]):
        self.name = user.name
        self.sender = 'Codevo <admin@admin.com>'
        self.email = email
        self.url = url

    async def sendMail(self, subject, template):
        # Define the config
        conf = ConnectionConfig(
            MAIL_USERNAME=settings.EMAIL_USERNAME,
            MAIL_PASSWORD=settings.EMAIL_PASSWORD,
            MAIL_FROM=settings.EMAIL_FROM,
            MAIL_PORT=settings.EMAIL_PORT,
            MAIL_SERVER=settings.EMAIL_HOST,
            MAIL_TLS=True,
            MAIL_SSL=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        # Generate the HTML template base on the template name
        template = env.get_template(f'{template}.html')

        html = template.render(
            url=self.url,
            first_name=self.name,
            subject=subject
        )

        # Define the message options
        message = MessageSchema(
            subject=subject,
            recipients=self.email,
            body=html,
            subtype="html"
        )

        # Send the email
        fm = FastMail(conf)
        await fm.send_message(message)

    async def sendVerificationCode(self):
        await self.sendMail('Your verification code (Valid for 10min)', 'verification')
