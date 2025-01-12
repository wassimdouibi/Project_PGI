# -*- coding: utf-8 -*-
from xml.dom import ValidationErr
from odoo  import models, fields, api
from odoo.exceptions import UserError

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
    _sql_constraints = [('unique_user', 'unique(chef)', 'Un chef doit etre un seul utilisateur.')]

    

    
# ------------------------------ Agent Clientèle ------------------------------
class AgentClientele(models.Model):
    _name = "gestion_de_reclamation.agent_clientele"
    _description = "Agent clientèle en charge de la préoccupation des besoins de réclamation"

    label = fields.Char(
        string="Role",
        required=True
    )
    agent = fields.Many2one(
        "res.users",
        string="Agent Clientèle"
    )
    reclamation_ids = fields.One2many(
        comodel_name="gestion_de_reclamation.reclamation",
        inverse_name="agent_id",
        string="Réclamations",
        help="Les réclamations prises en charge par cet agent"
    )
    _sql_constraints = [('unique_user', 'unique(agent)', 'Un agent doit etre un seul utilisateur.')]

# ---------------------------------------------- Appel ----------------------------------------------

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

#------------------------------------ Reclamant --------------------------------------------------
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
        ondelete="cascade",
    )
    date_creation = fields.Date(
        string="Date de création",
        default=fields.Date.context_today,
        readonly=True,
    )
    # Pour les afficher
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
            
    def action_imprimer_pv(self):
        # Vérifier si un PV est lié au projet commercial
        if self.pv_id:
            # Générer le PDF pour le PV associé
            return self.pv_id[0].action_imprimer_pv()  # Appel de la méthode dans le modèle PV
        else:
            raise UserError("Aucun procès-verbal associé à ce projet commercial.")
    _sql_constraints = [('unique_reclamation_id', 'unique(reclamation_id)', 'Un projet commercial ne peut etre associe qu\'a une seule reclamation.')]


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
    # Pour les afficher
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
    )
    date_pv = fields.Date(
        string="Date du PV",
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
    signatures = fields.One2many(
        comodel_name="gestion_de_reclamation.signature",
        string="Signatures",
        inverse_name="pv_id",
    )
    @api.model
    def create(self, vals):
        # Créer d'abord le PV
        pv = super(PV, self).create(vals)
        
        # Récupérer l'équipe désignée liée à la réclamation du projet commercial
        reclamation = pv.projet_commercial_id.reclamation_id
        equipe_designation = reclamation.equipe_designation_id

        # Ajouter automatiquement les membres de l'équipe à la liste des signatures
        if equipe_designation:
            signatures = []
            for membre in equipe_designation.membres_ids:
                signatures.append((0, 0, {
                    'user_id': membre.id,
                    'signature': False  # Signature non cochée au départ
                }))
            pv.write({'signatures': signatures})
        
        return pv
    
    def action_imprimer_pv(self):
        non_signes = self.signatures.filtered(lambda s: not s.signature)
        if non_signes:
            raise UserError("Tous les membres de l'équipe doivent signer avant d'imprimer le PV.")
        return self.env.ref('gestion_de_reclamation.action_report_pv').report_action(self)

    _sql_constraints = [('unique_projet_commercial', 'unique(projet_commercial_id)', 'Un projet commercial ne peut avoir qu\'un seul procès-verbal.')]


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

    

# ------------------------------ Signature -----------------------------
class Signature(models.Model):
    _name = "gestion_de_reclamation.signature"
    _description = "Signature des membres de l'équipe pour le PV"

    # Champs
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Utilisateur",
        required=True,
        help="Sélectionnez l'utilisateur qui doit signer.",
    )
    signature = fields.Boolean(
        string="Signé",
        default=False,
    )
    pv_id = fields.Many2one(
        comodel_name="gestion_de_reclamation.pv",
        string="Procès-Verbal",
        ondelete="cascade",
    )

    
