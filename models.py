# -*- coding: utf-8 -*-
from odoo import models, fields, api

#  Reclamation / Equipe / Appel / Reclamant / Agent clientele(nom + reclamations)

class Reclamation(models.Model):
    _inherit = 'crm.lead'  # Hérite de crm.lead
    
    _name = 'gestion_de_reclation.Reclamation'
    # Description spécifique pour les réclamations
    _description = "La liste des Réclamations"

    # Champs personnalisés pour les réclamations
    date_reclamation = fields.Date(string="Date de Réclamation", required=True)
    
    objet = fields.Char(string="Objet de la Réclamation", required=True)
    
    description = fields.Text(string="Description")
     
    # Catégorisation des réclamations
    type_reclamation = fields.Selection(
        [('technique', 'Technique'), ('commerciale', 'Commerciale')],
        string="Type de Réclamation",
        required=True
    )
    
    # Origine de la réclamation
    origine_reclamation = fields.Selection(
        [('citoyen', 'Citoyen'), ('entreprise', 'Entreprise'), ('cellule_veille', 'Cellule de Veille')],
        string="Origine de la Réclamation",
        required=True
    )

    # Informations sur le reclamant
    # Champs many2one vers reclamant 
    #Champs many2one vers agentClientele(id user)
    
   # champs many2one vers equipe technique
    equipe_technique_id = fields.Many2one(
        'gestion_de_reclation.equipe_technique', 
        string="Equipe Technique", 
        required=True,
        ondelete='restrict')
    
    
    equipe_commercial_id = fields.Many2one(
        'gestion_de_reclation.equipe_commercial', 
        string="Equipe Commerciale", 
        required=True,
        ondelete='restrict')

    # Traitement
    urgente = fields.Boolean(string="Est Urgente ?", default=False)
    
    etat = fields.Selection(
        [('nouveau', 'Nouveau'), ('en_cours', 'En Cours'), ('resolu', 'Résolu'), ('archive', 'Archivé')],
        string="État",
        default='nouveau'
    )

    def generate_accuse(self):
        """Action pour générer un accusé de réclamation en PDF"""
        return self.env.ref('gestion_de_reclamation.action_accuse_reclamation').report_action(self)      
    
    

    
















class Appel(models.Model):
    # meta-données
    _name = 'gestion_de_reclation.appel'
    _description = "Appel modèle à des fins de réclamation"
    #champs
    objetAppel = fields.Char(
        string = 'Objet de l\'appel',
        required = True
    ) # l'objet de l'appel en general
    
    dateAppel = fields.Date(
        string="Date de l'appel"
    ) # la date de creation de l'appel


    
    nomAppelant = fields.Char(
        string = 'Nom de l\'appelant',
        required = True
    ) # le nom de l'appelant
    
    prenomAppelant = fields.Char(
        string = 'Prenom de l\'appelant',
        required = True
    ) # le prenom de l'appelant
    
    numeroAppelant = fields.Char(
        string = 'Numero de l\'appelant',
        required = True
    ) # le numero de l'appelant
    
    
    


    class EquipeTechnique(models.Model):
        _inherit = 'crm.team'
        
        _name = 'gestion_de_reclation.equipe_technique'
        _description = "Equipe technique qui gere une reclamation technique"




    class EquipeCommercial(models.Model):
        _inherit = 'crm.team'

        _name = 'gestion_de_reclation.equipe_commerciale'
        _description = "Equipe commerciale qui gere une reclamation commerciale"
    
    
