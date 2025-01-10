# -*- coding: utf-8 -*-
from odoo import models, fields, api

# ------------------------------ Réclamation ------------------------------
class Reclamation(models.Model):
    _name = "gestion_de_reclamation.reclamation"
    _description = "Le modèle qui permet de gérer (créer/supprimer/modifier) une réclamation"

    # Champs
    objet = fields.Char(
        string="Objet de la réclamation",
        required=True
    )
    description = fields.Text(
        string="Description de la réclamation"
    )
    date_creation = fields.Date(
        string="Date de création",
        default=fields.Date.context_today,
        readonly=True
    )
    type_reclamation = fields.Selection(
        [("technique", "Technique"), ("commerciale", "Commerciale")],
        string="Type",
        required=True
    )
    origine_reclamation = fields.Selection(
        [("citoyen", "Citoyen"), ("entreprise", "Entreprise"), ("cellule_veille", "Cellule de Veille")],
        string="Origine",
        required=True
    )
    urgente = fields.Boolean(string="Urgente", default=False)
    etat = fields.Selection(
        [("nouveau", "Nouveau"), ("en_cours", "En Cours"), ("resolu", "Résolu"), ("archive", "Archivé")],
        string="État",
        default="nouveau"
    )
    equipe_designation_id = fields.Many2one(
        comodel_name="gestion_de_reclamation.equipe_designation",
        string="Équipe Désignée",
        domain="[('type', '=', type_reclamation)]", # Filter based on type_reclamation
        required=False,
        ondelete="restrict",
        display_name="nom"  # Ensure it uses the 'name' field for display

        )
    @api.model
    def create(self, vals):
        vals['date_creation'] = fields.Date.context_today(self)
        return super(Reclamation, self).create(vals)



# ------------------------------ Equipe Désignation ------------------------------
class EquipeDesignation(models.Model):
    _name = "gestion_de_reclamation.equipe_designation"
    _description = "Modèle de base pour les équipes désignées"
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Optional for chatter and tracking

    nom = fields.Char(
        string="Nom de l'équipe",
        required=True
    )
    type = fields.Selection(
        [("technique", "Technique"), ("commerciale", "Commerciale")],
        string="Type d'équipe",
        required=True
    )
    membres_ids = fields.Many2many(
        "res.users",
        string="Membres de l'équipe"
    )
    reclamation_ids = fields.One2many(
        "gestion_de_reclamation.reclamation",
        "equipe_designation_id",
        string="Réclamations liées",
        domain="[('type', '=', type_reclamation)]"  # Example filter condition
    )

    
# ------------------------------ Agent Clientèle ------------------------------
class AgentClientele(models.Model):
    _name = "gestion_de_reclamation.agent_clientele"
    _description = "Agent clientèle en charge de la préoccupation des besoins de réclamation"

    label = fields.Char(
        string="IdAgentClientele",
        required=True
    )
