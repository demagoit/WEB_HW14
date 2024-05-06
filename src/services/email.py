from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from src.conf.config import config
from src.services.auth import auth_service

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME=config.MAIL_FROM_NAME,
    MAIL_STARTTLS=config.MAIL_STARTTLS,
    MAIL_SSL_TLS=config.MAIL_SSL_TLS,
    USE_CREDENTIALS=config.USE_CREDENTIALS,
    VALIDATE_CERTS=config.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

async def send_email(email: str, username:str, host:str) -> None:
    '''
    Constructs and send e-mail confirmation letter

    Args:
        email: user's e-mail
        username: user name
        host: domain adress where application deployed. Example: http://example.com:80
    Returns:
        None
    Raises:
        ConnectionErrors: If connection fails
    '''
    try:
        email_token = await auth_service.create_email_token({'sub':email})
        message = MessageSchema(
            recipients=[email], 
            subject='Confirm your e-mail', 
            template_body={'fullname': username, 'host': host, 'token': email_token}, subtype=MessageType.html
            )
        
        fm = FastMail(conf)
        await fm.send_message(message, template_name='email_confirmation.html')
    except ConnectionErrors as err:
        print(err)

