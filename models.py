# -*- coding: utf-8 -*-
from odoo import models, fields, api

# ------------------------------ Réclamation -----------------------------   # ------------------------------ Agent Clientèle ------------------------------
class AgentClientele(models.Model):
    _name = "gestion_de_reclamation.agent_clientele"
    _description = "Agent clientèle en charge de la préoccupation des besoins de réclamation"
        #Champs
    label = fields.Char(
            string="IdAgentClientele",
            required=True
        )