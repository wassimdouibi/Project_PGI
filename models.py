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
        required=True,
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
    
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def default_get(self, fields_list):
        res = super(Reclamation, self).default_get(fields_list)
        company = self.env.user.company_id
        if 'agence_id' in fields_list and company.company_registry:
            res['agence_id'] = company.company_registry
        return res

    def print_accuse_reception(self):
        """Génère un accusé de réception en PDF"""
        return self.env.ref('gestion_de_reclamation.action_report_accuse_reception').report_action(self)
    
    @api.onchange('etat')
    def _onchange_etat(self):
        if self.etat == 'archive':
            self.archive_reclamation()

    def archive_reclamation(self):
        # Crée un enregistrement dans le modèle 'ReclamationArchive' basé sur cette réclamation
        reclamation_archive = self.env['gestion_de_reclamation.reclamation_archive'].create({
            'objet': self.objet,
            'description': self.description,
            'date_creation': self.date_creation,
            'type_reclamation': self.type_reclamation,
            'urgente': self.urgente,
            'equipe_designation_id': self.equipe_designation_id.id,
            'agent_id': self.agent_id.id,
            'reclamant_id': self.reclamant_id.id,
            'agence_id': self.agence_id
        })
        
        self.write({'etat': 'archive', 'active': False})

        



#--------------------------------Reclamations archivees---------------------------

class ReclamationArchive(models.Model):
    _name = "gestion_de_reclamation.reclamation_archive"
    _description = "Réclamations Archivées"

    # Champs copiés de Reclamation
    objet = fields.Char(string="Objet de la réclamation", required=True)
    description = fields.Text(string="Description de la réclamation")
    date_creation = fields.Date(string="Date de création", readonly=True)
    type_reclamation = fields.Selection(
        [("technique", "Technique"), ("commerciale", "Commerciale")],
        string="Type",
        required=True
    )
    urgente = fields.Boolean(string="Urgente", default=False)
    equipe_designation_id = fields.Many2one(
        comodel_name="gestion_de_reclamation.equipe_designation",
        string="Équipe Désignée"
    )
    agent_id = fields.Many2one(
        comodel_name="gestion_de_reclamation.agent_clientele",
        string="Agent Clientèle"
    )
    reclamant_id = fields.Many2one(
        comodel_name="gestion_de_reclamation.reclamant",
        string="Réclamant"
    )
    agence_id = fields.Char(string="Identifiant de l'Agence", readonly=True)

# ------------------------------ Equipe Désignation ------------------------------

class EquipeDesignation(models.Model):
    _name = "gestion_de_reclamation.equipe_designation"
    _description = "Modèle de base pour les équipes désignées"
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Optional for chatter and tracking

    nom = fields.Char(
        string="Nom de l'équipe",
        required=True
    )
    chef = fields.Many2one(
        "res.users",
        string="Chef de l'équipe"
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
    


# ------------------------------ Projet Commercial ------------------------------
class ProjetCommercial(models.Model):
    _name = "gestion_de_reclamation.projet_commercial"
    _description = "Projet Commercial lié à une réclamation"

    # Champs
    reclamation_id = fields.Many2one(
        comodel_name="gestion_de_reclamation.reclamation",
        string="Réclamation",
        domain="[('type_reclamation', '=', 'commerciale')]",
        required=True,
        ondelete="cascade",
    )
    pv_id = fields.One2many(
        comodel_name="gestion_de_reclamation.pv",
        string="Procès Verbal",
        inverse_name="projet_commercial_id",
    )
    date_creation = fields.Date(
        string="Date de création",
        default=fields.Date.context_today,
        readonly=True,
    )
    # Related fields for accessing Reclamation fields
    reclamation_objet = fields.Char(
        related="reclamation_id.objet", string="Objet de la Réclamation", store=True
    )
    reclamation_description = fields.Text(
        related="reclamation_id.description", string="Description de la Réclamation", store=True
    )
    reclamation_urgente = fields.Boolean(
        related="reclamation_id.urgente", string="Réclamation Urgente", store=True
    )
    reclamation_etat = fields.Selection(
        related="reclamation_id.etat", string="État de la Réclamation", store=True
    )

    #_sql_constraints = [('unique_pv', 'unique(pv_id)', 'Un projet commercial ne peut avoir qu\'un seul procès-verbal.')]


# ------------------------------ Projet Technique ------------------------------
class ProjetTechnique(models.Model):
    _name = "gestion_de_reclamation.projet_technique"
    _description = "Projet Technique lié à une réclamation"

    # Champs
    reclamation_id = fields.Many2one(
        comodel_name="gestion_de_reclamation.reclamation",
        string="Réclamation",
        domain="[('type_reclamation', '=', 'technique')]",
        required=True,
        ondelete="cascade",
    )
    deplacement_ids = fields.One2many(
        comodel_name="gestion_de_reclamation.deplacement",
        inverse_name="projet_technique_id",
        string="Déplacements",
    )
    date_creation = fields.Date(
        string="Date de création",
        default=fields.Date.context_today,
        readonly=True,
    )
    complexite = fields.Selection(
        [
            ("faible", "Faible"),
            ("moyenne", "Moyenne"),
            ("elevee", "Élevée"),
        ],
        string="Complexité",
        required=True,
    )
    gravite = fields.Selection(
        [
            ("mineure", "Mineure"),
            ("majeure", "Majeure"),
            ("critique", "Critique"),
        ],
        string="Gravité",
        required=True,
    )
    # Related fields for accessing Reclamation fields
    reclamation_objet = fields.Char(
        related="reclamation_id.objet", string="Objet de la Réclamation", store=True
    )
    reclamation_description = fields.Text(
        related="reclamation_id.description", string="Description de la Réclamation", store=True
    )
    reclamation_urgente = fields.Boolean(
        related="reclamation_id.urgente", string="Réclamation Urgente", store=True
    )
    reclamation_etat = fields.Selection(
        related="reclamation_id.etat", string="État de la Réclamation", store=True
    )

    
# ------------------------------ Procès Verbal ------------------------------
class PV(models.Model):
    _name = "gestion_de_reclamation.pv"
    _description = "Procès Verbal pour un projet commercial"

    # Champs
    projet_commercial_id = fields.Many2one(
        comodel_name="gestion_de_reclamation.projet_commercial",
        string="Projet Commercial",
        required=True,
        ondelete="cascade",
    )
    date_pv = fields.Date(
        string="Date du Procès-Verbal",
        default=fields.Date.context_today,
        required=True,
    )
    objet = fields.Text(
        string="Objet du PV",
        required=True,
    )
    contenu = fields.Text(
        string="Contenu du PV",
        required=True,
    )



# ------------------------------ Déplacement ------------------------------
class Deplacement(models.Model):
    _name = "gestion_de_reclamation.deplacement"
    _description = "Modèle pour enregistrer les déplacements de l'équipe technique"

    # Champs
    projet_technique_id = fields.Many2one(
        comodel_name="gestion_de_reclamation.projet_technique",  # Lien avec le projet technique
        string="Projet Technique",
        required=True,
        ondelete="cascade",
    )
    date_deplacement = fields.Date(
        string="Date du Déplacement",
        required=True,
        default=fields.Date.context_today,
    )
    lieu_deplacement = fields.Char(
        string="Lieu du Déplacement",
        required=True,
    )
    actions_realisees = fields.Text(
        string="Actions réalisées",
        required=True,
        help="Détail des actions effectuées durant ce déplacement"
    )
    commentaires = fields.Text(
        string="Commentaires",
        help="Commentaires supplémentaires ou observations concernant le déplacement"
    )

    

