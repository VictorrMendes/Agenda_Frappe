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
