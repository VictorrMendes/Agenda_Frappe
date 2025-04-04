# Agenda Frappe

![GitHub repo size](https://img.shields.io/github/repo-size/VictorrMendes/Agenda_Frappe)
![GitHub last commit](https://img.shields.io/github/last-commit/VictorrMendes/Agenda_Frappe)

## Sobre o Projeto

**Agenda Frappe** é um projeto desenvolvido utilizando o **Frappe Framework**, com o objetivo de criar uma aplicação de agenda. Este projeto está sendo desenvolvido para um case na **Nexforce**, seguindo os requisitos estabelecidos.

## Tecnologias Utilizadas
- [Frappe Framework](https://frappeframework.com/)
- Python
- MariaDB / MySQL
- Redis
- Node.js

## Requisitos
Antes de instalar o projeto, certifique-se de ter os seguintes requisitos atendidos:
- Python 3.10+
- Node.js 16+
- Redis
- Banco de Dados (MariaDB ou MySQL)
- Yarn 

## Instalação

1. Clone o repositório:
   ```sh
   git clone https://github.com/VictorrMendes/Agenda_Frappe.git
   cd Agenda_Frappe
   ```
2. Instale as dependências do Frappe:
   ```sh
   pip install frappe-bench
   pip install -r requirements.txt
   ```
3. Crie um novo ambiente do Frappe e instale o aplicativo:
   ```sh
   bench init my-bench --frappe-branch version-14
   cd my-bench
   bench new-site mysite.local
   bench get-app https://github.com/VictorrMendes/Agenda_Frappe.git
   bench install-app agenda_frappe
   ```
4. Ative o modo desenvolvedor:
   ```sh
   bench set-config -g developer_mode true
   ```
5. Execute o servidor:
   ```sh
   bench start
   ```
6. Acesse a interface web em `http://localhost:8000`

## Funcionalidades Implementadas

### Doctype "Appointment"
O sistema tem um **Doctype** chamado `agenda`, que contém os seguintes campos:
- **Client Name** *(Data)* - Nome do cliente.
- **Start date** *(Datetime)* - Data e hora de início do compromisso.
- **End date** *(Datetime - Read-only)* 
- **Duration** *(Time)* - Tempo de duração do compromisso.
- **Description** *(Small Text)* - Descrição do compromisso.
- **Seller** *(Link)* - Vendedor associado ao compromisso.
- **Status** *(Select)* - Opções: `Scheduled`, `Finished`, `Canceled`.

### Validações e Regras de Negócio
- Implementação de **validação de conflitos de agendamento**: 
  - O vendedor não pode estar em dois compromissos ao mesmo tempo.
  - Se um novo compromisso conflitar com um já existente, o sistema exibirá uma mensagem de erro.

Código de validação de agendamentos:
```python
import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime, timedelta

class Agenda(Document):
    def validate(self):
        self.validate_seller_availability()     

    def validate_seller_availability(self):
        """
        Verificação se o vendedor já possui um compromisso no mesmo horário e período.
        """


        # Validação e conversão de start_date e duration

        #start_date para datetime 
        start_datetime = datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")

        
        try:
            if ":" in self.duration:
                duration_parts = [int(x) for x in self.duration.split(":")]
            else:
                duration_parts = [int(float(self.duration)), 0, 0]

            duration_timedelta = timedelta(hours=duration_parts[0], minutes=duration_parts[1], seconds=duration_parts[2])

        except ValueError:
            frappe.throw(_("Erro no formato da duração. Certifique-se de que está no formato HH:MM:SS."))

        end_datetime = start_datetime + duration_timedelta


        #Verificação de compromissos existentes para evitar conflitos de horário
        existing_appointments = frappe.get_all(
            "Agenda",
            filters={
                "seller": self.seller,
                "name": ("!=", self.name),  
                "start_date": ("<", end_datetime.strftime("%Y-%m-%d %H:%M:%S")),
                "end_date": (">", start_datetime.strftime("%Y-%m-%d %H:%M:%S"))
            },
            fields=["name", "start_date", "end_date"]
        )

        #Em caso de ter compromissos existentes, exibir mensagem de erro relatando o conflito
        if existing_appointments:
            frappe.throw(_(f"Horário indisponível. O {self.seller} já possui um compromisso neste horário."))


        #Garantir que  o end_date seja preenchido corretamente com base no start_date e duration
    def before_save(self):
        if self.start_date and self.duration:

            # Convertendo start_date para datetime
            start_datetime = datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")
            
            # Convertendo duração de "HH:MM:SS" para timedelta
            duration_parts = [int(x) for x in self.duration.split(":")]
            duration_timedelta = timedelta(hours=duration_parts[0], minutes=duration_parts[1], seconds=duration_parts[2])

            self.end_date = (start_datetime + duration_timedelta).strftime("%Y-%m-%d %H:%M:%S")
```


## Licença

Este projeto é licenciado sob a [MIT License](LICENSE).

---

