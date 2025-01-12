# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class ReclamationController(http.Controller):

    @http.route('/reclamation/form', auth='public', website=True)
    def reclamation_form(self, **kw):
        print("Reclamation form route hit!")
        return request.render('gestion_de_reclamation.reclamation_form', {})


    @http.route('/website/submit_reclamation', type='http', auth="public", methods=['POST'], csrf=False)
    def submit_reclamation(self, **post):
        # Retrieve form data
        reclamant_name = post.get('reclamant_name')
        reclamant_email = post.get('reclamant_email')
        reclamant_phone = post.get('reclamant_phone')
        reclamant_prenom = post.get('reclamant_prenom')
        reclamant_adresse = post.get('reclamant_adresse')
        reclamant_commune = post.get('reclamant_commune')
        reclamant_origine = post.get('reclamant_origine')
        reclamant_resSociale = post.get('reclamant_resSociale')
        
        objet = post.get('objet')
        description = post.get('description')
        file = request.httprequest.files.get('file_attachments')
        attachment_ids = None
        if file:
            attachment_ids = request.env['ir.attachment'].sudo().create({
            'name': file.filename,
            'type': 'binary',
            'datas': file.read().encode('base64'),
            'datas_fname': file.filename,
            'res_model': 'reclamation',
               }).id
        
        # Check if reclamant exists, if not, create them
        reclamant = request.env['gestion_de_reclamation.reclamant'].sudo().search([
            ('nom', '=', reclamant_name),
            ('email', '=', reclamant_email),
            ('prenom', '=', reclamant_prenom),
            ('Adresse', '=', reclamant_adresse),
        ], limit=1)
        
        if not reclamant:
            reclamant = request.env['gestion_de_reclamation.reclamant'].sudo().create({
                'nom': reclamant_name,
                'prenom': reclamant_prenom,
                'email': reclamant_email,
                'telephone': reclamant_phone,
                'Adresse': reclamant_adresse,
                'Commune': reclamant_commune,
                'origine_reclamation': reclamant_origine,
                'raison_sociale': reclamant_resSociale,
    
            })
        
        # Create the reclamation
        reclamation = request.env['gestion_de_reclamation.reclamation'].sudo().create({
            'reclamant_id': reclamant.id,
            'objet': objet,
            'description': description,
            'attachment_ids': attachment_ids
        })
        
        
        if reclamation:
            reclamation.print_accuse_reception()

            # Redirect to a success page or show a success message
            return request.render('gestion_de_reclamation.success_page')
        else:
            # Handle the case where the reclamation creation failed
            return request.render('gestion_de_reclamation.error_page', {'error_message': 'Failed to create the reclamation.'})
