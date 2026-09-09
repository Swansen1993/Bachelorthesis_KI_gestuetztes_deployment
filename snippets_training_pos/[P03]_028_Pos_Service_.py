# Project: P03_mailer
# Layer: Business Logic
# Source: mailer/mailer.py

import dataclasses
from typing import Any
from pgpy import PGPKey

@dataclasses.dataclass
class Mailer:
    sender_email: str
    to_email: str
    to_name: str
    smtp_host: dataclasses.InitVar[str]
    smtp_port: dataclasses.InitVar[int]
    smtp_tls: dataclasses.InitVar[bool]
    smtp_ssl: dataclasses.InitVar[bool]
    smtp_user: dataclasses.InitVar[str]
    smtp_password: dataclasses.InitVar[str]
    smtp_config: dict[str, Any] = dataclasses.field(init=False)
    pgp_public_key: PGPKey | None

    def send_email(
        self,
        from_email: str,
        from_name: str,
        subject: str,
        message: str,
        public_key: str | None,
    ) -> None:
        if self.pgp_public_key:
            return self._send_encrypted_email(
                from_email, from_name, subject, message, public_key, self.pgp_public_key
            )
        else:
            return self._send_plain_email(from_email, from_name, subject, message)