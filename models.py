# -*- coding: utf-8 -*-
from odoo import models, fields, api

# ------------------------------ Réclamation ------------------------------
class Reclamation(models.Model):
    # meta-données
    _name = "gestion_de_reclamation.reclamation"
    _description = "Le modèle qui nous permet de gérer (créer/supprimer/modifier) une réclamation"

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

    urgente = fields.Boolean(string="Urgente", default=False)

    etat = fields.Selection(
        [("nouveau", "Nouveau"), ("en_cours", "En Cours"), ("resolu", "Résolu"), ("archive", "Archivé")],
        string="État",
        default="nouveau"
    )

    # Informations sur le réclamant
    # Champs many2one vers réclamant 
    # Champs many2one vers agentClientele (id user)

    # Champs many2one vers équipe technique ou commerciale
    equipe_designation_id = fields.Many2one(
        "gestion_de_reclamation.equipe_designation",
        string="Équipe Désignée",
        required=True,
        ondelete="restrict"
    )

    @api.model
    def create(self, vals):
        # Assurer que la date de création est toujours définie à la date actuelle lors de la création d'un enregistrement
        vals['date_creation'] = fields.Date.context_today(self)
        return super(Reclamation, self).create(vals)

    @api.onchange('date_creation')
    def _onchange_date_creation(self):
        if self.date_creation:
            self.date_creation = self.create_date

    def generate_accuse(self):
        """Action pour générer un accusé de réclamation en PDF"""
        return self.env.ref("gestion_de_reclamation.action_accuse_reclamation").report_action(self)


# ------------------------------ Equipe Désignation ------------------------------
class EquipeDesignation(models.Model):
    _name = "gestion_de_reclamation.equipe_designation"
    _description = "Modèle permettant de gérer les équipes désignées pour une réclamation selon son type"

    # Champs
    nom = fields.Char(
        string="Nom de l'équipe",
        required=True
    )
    type = fields.Selection(
        [("technique", "Technique"), ("commerciale", "Commerciale")],
        string="Type d'équipe",
        required=True
    )
    # Réclamation liée à l'équipe
    reclamation_ids = fields.One2many(
        "gestion_de_reclamation.reclamation",
        "equipe_designation_id",  # Correspond au champ Many2one dans Reclamation
        string="Réclamations"
    )

    # Membres de l'équipe (utilisateurs Odoo)
    membres_ids = fields.Many2many(
        "res.users",  # Lien vers les utilisateurs Odoo
        string="Membres de l'équipe"
    )

    # Association à une équipe technique ou commerciale
    equipe_technique_id = fields.Many2one(
        "gestion_de_reclamation.equipe_technique",
        string="Équipe Technique"
    )
    equipe_commercial_id = fields.Many2one(
        "gestion_de_reclamation.commission_de_redressement",
        string="Équipe Commerciale"
    )

    @api.onchange('reclamation_id')
    def _onchange_reclamation(self):
        # Lors de la sélection d'une réclamation, on peut lier les membres à cette réclamation
        if self.reclamation_id:
            self.membres_ids = self.reclamation_id.equipe_designation_id.membres_ids


# ------------------------------ Equipe technique ------------------------------
class EquipeTechnique(EquipeDesignation):
    _name = "gestion_de_reclamation.equipe_technique"
    _description = "Équipe technique qui est responsable de la résolution d'une réclamation technique"
    
    # Personnalisation spécifique à l'équipe technique
    # Ces champs sont optionnels, car ils sont déjà hérités de EquipeDesignation


# ------------------------------ Commission de redressement ------------------------------
class CommissionDeRedressement(EquipeDesignation):
    _name = "gestion_de_reclamation.commission_de_redressement"
    _description = "Commission de redressement qui est responsable de la résolution d'une réclamation commerciale"
    
    # Personnalisation spécifique à la commission de redressement
    # Ces champs sont optionnels, car ils sont déjà hérités de EquipeDesignation


# ------------------------------ Agent Clientèle ------------------------------
class AgentClientele(models.Model):
    _name = "gestion_de_reclamation.agent_clientele"
    _description = "Agent clientèle en charge de la préoccupation des besoins de réclamation"

    # Champs
    label = fields.Char(
        string="IdAgentClientele",
        required=True
    )
