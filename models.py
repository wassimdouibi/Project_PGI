# -*- coding: utf-8 -*-
from odoo import models, fields, api


# ------------------------------ Réclamation ------------------------------
class Reclamation(models.Model):
    # Hérite de crm.lead
    _inherit = "crm.lead"

    # Champs 
    objet = fields.Char(string="Objet de la Réclamation", required=True)  #
    # Catégorisation des réclamations
    type_reclamation = fields.Selection(
        [
            ("technique", "Technique"),
            ("commerciale", "Commerciale")
        ],
        string="Type de Réclamation",
        required=True
    )
    # Origine de la réclamation
    origine_reclamation = fields.Selection(
        [
            ("citoyen", "Citoyen"), 
            ("entreprise", "Entreprise"), 
            ("cellule_veille", "Cellule de Veille")
        ],
        string="Origine de la Réclamation",
        required=True
    )
 
    # Informations sur le reclamant
    # Champs many2one vers reclamant 
    # Champs many2one vers agentClientele(id user)

    # champs many2one vers equipe technique
    equipe_technique_id = fields.Many2one(
        "crm.team",
        string="Equipe Technique",
        required=True,
        ondelete="restrict"
    )
    equipe_commercial_id = fields.Many2one(
        "crm.team",
        string="Equipe Commerciale",
        required=True,
        ondelete="restrict"
    )
    # Traitement
    urgente = fields.Boolean(string="Est Urgente ?", default=False)
    etat = fields.Selection(
        [("nouveau", "Nouveau"), ("en_cours", "En Cours"), ("resolu", "Résolu"), ("archive", "Archivé")],
        string="État",
        default="nouveau"
    )

    # def generate_accuse(self):
    #     """Action pour générer un accusé de réclamation en PDF"""
    #     return self.env.ref("gestion_de_reclamation.action_accuse_reclamation").report_action(self)


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
    ) # le prenom de l"appelant
    numeroAppelant = fields.Char(
        string="Numero de l'appelant",
        required=True
    )  # le numero de l"appelant

    idAgentClientele = fields.Many2one(
        "gestion_de_reclamation.agent_clientele",
        string="Agent clientele",
        required= True,
    )  # id de l"agent qui a répondu à l"appel

    # ------------------------------ Equipe technique ------------------------------
    class EquipeTechnique(models.Model):
        _inherit = "crm.team"


    # ------------------------------ Commission de redressement ------------------------------
    class CommissionDeRedressement(models.Model):
        _inherit = "crm.team"

    # ------------------------------ Agent Clientèle ------------------------------
    class AgentClientele(models.Model):
        _name = "gestion_de_reclamation.agent_clientele"
        _description = "Agent clientèle en charge de la préoccupation des besoins de réclamation"
        #Champs
        label = fields.Char(
            string="IdAgentClientele",
            required=True
        )