# -*- coding: utf-8 -*-
from odoo import models, fields, api


# ------------------------------ Réclamation ------------------------------
class Reclamation(models.Model):
    # meta-données
    _name = "gestion_de_reclamation.reclamation"
    _description = "le modèle qui nous permet de gérer (creer/supprimer/modifier) une réclamation"

    # Champs 
    objet = fields.Char(
        string="Objet de la réclamation",
        required=True
    )
    description = fields.Text(
        string="Description de la réclamation",
        required=False
    )
    date_creation = fields.Date(
        string="Date de création",
        default=fields.Date.context_today,
        readOnly=True
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

    urgente = fields.Boolean(string="urgente", default=False)

    etat = fields.Selection(
        [("nouveau", "Nouveau"), ("en_cours", "En Cours"), ("resolu", "Résolu"), ("archive", "Archivé")],
        string="État",
        default="nouveau"
    )

    # Informations sur le reclamant
    # Champs many2one vers reclamant 
    # Champs many2one vers agentClientele(id user)

    # champs many2one vers equipe technique
    equipe_technique_id = fields.Many2one(
        "gestion_de_reclamation.equipe_technique",
        string="Equipe Technique",
        required=True,
        ondelete="restrict"
    )
    equipe_commercial_id = fields.Many2one(
        "gestion_de_reclamation.commission_de_redressement",
        string="Equipe Commerciale",
        required=True,
        ondelete="restrict"
    )

    @api.model
    def create(self, vals):
        # Ensure date_creation is always set to the current date when creating a record
        vals['date_creation'] = fields.Date.context_today(self)
        return super(Reclamation, self).create(vals)

    @api.onchange('date_creation')
    def _onchange_date_creation(self):
        if self.date_creation:
            self.date_creation = self.create_date

    def generate_accuse(self):
        """Action pour générer un accusé de réclamation en PDF"""
        return self.env.ref("gestion_de_reclamation.action_accuse_reclamation").report_action(self)


# ------------------------------ Appel ------------------------------
class Appel(models.Model):
    # meta-données
    _name = "gestion_de_reclamation.appel"
    _description = "Appel modèle à des fins de réclamation"

    # champs
    label = fields.Char(
        string="IdAppel",
        required=True
    )  # identifiant de l'appel
    objetAppel = fields.Char(
        string="Objet de l'appel",
        required=True
    )  # l"objet de l"appel en general
    descriptionAppel = fields.Text(
        string="Les points abordés dans l'appel",
        required=False
    )
    dateAppel = fields.Date(
        string="Date de l'appel"
    )  # la date de creation de l"appel

    nomAppelant = fields.Char(
        string="Nom de l'appelant",
        required=True
    )  # le nom de l"appelant
    prenomAppelant = fields.Char(
        string="Prenom de l'appelant",
        required=True
    )  # le prenom de l"appelant
    numeroAppelant = fields.Char(
        string="Numero de l'appelant",
        required=True
    )  # le numero de l"appelant

    idAgentClientele = fields.Many2one(
        "gestion_de_reclamation.agent_clientele",
        string="Agent clientele",
        required=True,
    )  # id de l"agent qui a répondu à l"appel


# ------------------------------ Equipe technique ------------------------------
class EquipeTechnique(models.Model):
    _name = "gestion_de_reclamation.equipe_technique"
    _description = "Equipe technique qui est responsable de la résolution d'une réclamation technique"


# ------------------------------ Commission de redressement ------------------------------
class CommissionDeRedressement(models.Model):
    _name = "gestion_de_reclamation.commission_de_redressement"
    _description = "Commission de redressement qui est responsable de la résolution d'une reclamation commerciale"


# ------------------------------ Agent Clientèle ------------------------------
class AgentClientele(models.Model):
    _name = "gestion_de_reclamation.agent_clientele"
    _description = "Agent clientèle en charge de la préoccupation des besoins de réclamation"
    # Champs
    label = fields.Char(
        string="IdAgentClientele",
        required=True
    )
