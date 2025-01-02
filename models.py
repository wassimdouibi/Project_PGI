# -*- coding: utf-8 -*-
from odoo import models, fields, api

#  Reclamation / Equipe / Appel / Reclamant

class Reclamation(models.Model):
    _name = 'gestion_de_reclation.reclamation'

    _description = "La liste des Réclamations"

    date_reclamation = fields.Date(string="Date de Réclamation", required=True)
    
    objet = fields.Char(string="Objet de la Réclamation", required=True)
    
    description = fields.Text(string="Description")
     
    # Catégorisation
    type_reclamation = fields.Selection(
        [('technique', 'Technique'), ('commerciale', 'Commerciale')],
        string="Type de Réclamation",
        required=True
    )
    
















class Appel(models.Model):
    # meta-données
    _name = 'gestion_de_reclation.appel'
    _description = "Appel modèle à des fins de réclamation"
    #champs
    objetAppel = fields.Char(
        string = 'Objet de l\'appel',
        required = True
    ) # l'objet de l'appel en general
    
    dateAppel = models.Date() # la date de creation de l'appel
    
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
    
    