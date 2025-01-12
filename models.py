# -*- coding: utf-8 -*-
from odoo  import models, fields, api

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

        )
    
    appel_ids = fields.One2many(
        comodel_name="gestion_de_reclamation.appel",  # Target model
        inverse_name="reclamation_id",               # Field in the target model
        string="Appels",                             # Field label
        help="List of appels linked to this reclamation"
    )

    agent_id = fields.Many2one(
        comodel_name="gestion_de_reclamation.agent_clientele",
        string="Agent Clientèle",
       # required=True,
        ondelete="restrict",
        help="L'agent clientèle en charge de cette réclamation"
    )

    reclamant_id = fields.Many2one(
        comodel_name="gestion_de_reclamation.reclamant",
        string="Réclamant",
        required=True,
        ondelete="restrict",
        help="Le réclamant ayant émis cette réclamation"
    )
    
    agence_id = fields.Char(string="Identifiant de l'Agence", readonly=True)

    attachment_ids = fields.Many2many(
        comodel_name="ir.attachment",
        string="Attachments",
        help="Attachments related to this reclamation"
    )
    

    @api.model
    def default_get(self, fields_list):
        res = super(Reclamation, self).default_get(fields_list)
        company = self.env.user.company_id
        if 'agence_id' in fields_list and company.company_registry:
            res['agence_id'] = company.company_registry
        return res




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
        domain="[('type_reclamation', '=', type)]"  # Example filter condition
    )

    

    
# ------------------------------ Agent Clientèle ------------------------------
class AgentClientele(models.Model):
    _name = "gestion_de_reclamation.agent_clientele"
    _description = "Agent clientèle en charge de la préoccupation des besoins de réclamation"

    label = fields.Char(
        string="IdAgentClientele",
        required=True
    )

    reclamation_ids = fields.One2many(
        comodel_name="gestion_de_reclamation.reclamation",
        inverse_name="agent_id",
        string="Réclamations",
        help="Les réclamations prises en charge par cet agent"
    )

# ------------------------------ Appel ------------------------------

class Appel(models.Model):
    _name = "gestion_de_reclamation.appel"
    _description = "Appel"

    name = fields.Char(string="Appel Name", required=True)
    date = fields.Datetime(string="Call Date", required=True)
    notes = fields.Text(string="Notes")

    reclamation_id = fields.Many2one(
        comodel_name="gestion_de_reclamation.reclamation",  # Target model
        string="Reclamation",                              # Field label
        ondelete="cascade",                                # Delete appels if the linked reclamation is deleted
        help="The reclamation linked to this appel"
    ) 

    #------------------Reclamant-------------------------
    class Reclamant(models.Model):
        _name = "gestion_de_reclamation.reclamant"
        _description = "Modèle représentant un réclamant"

        # Champs du réclamant
        nom = fields.Char(
            string="Nom du réclamant",
            required=True
        )
        prenom = fields.Char(
            string="Prenom du réclamant",
            required=True
        )
        email = fields.Char(
            string="Email",
            help="Email du réclamant"
        )
        telephone = fields.Char(
            string="Téléphone",
            help="Numéro de téléphone du réclamant"
        )
        Adresse = Commune = fields.Text(
            string="Adresse",
            help="Adresse du réclamant"
        )
        Commune = fields.Text(
            string="Commune",
            help="Commune du réclamant"
        )
        origine_reclamation = fields.Selection(
        [("citoyen", "Citoyen"), ("entreprise", "Entreprise"), ("cellule_veille", "Cellule de Veille")],
        string="Origine",
        required=True
    )
        raison_sociale = fields.Text(
            string="Raison Sociale",
            help="Raison Sociale en cas entreprise "
        )

        # Relation One2many avec les réclamations
        reclamation_ids = fields.One2many(
            comodel_name="gestion_de_reclamation.reclamation",
            inverse_name="reclamant_id",
            string="Réclamations",
            help="Liste des réclamations liées à ce réclamant"
        )
        

class EquipeCommerciale(models.Model):
    _name = "gestion_de_reclamation.equipe_commerciale"
    _description = "desc"
