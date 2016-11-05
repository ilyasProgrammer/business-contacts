# -*- coding: utf-8 -*-

from odoo import fields, models, api
import csv
import os
import logging
import time
_logger = logging.getLogger(__name__)


class BusinessData(models.Model):
    _name = "data.order"
    _description = "Business Data"

    business_name = fields.Char()
    telephone = fields.Char()
    address = fields.Char()
    state = fields.Char()
    post_code = fields.Char()
    manta_url = fields.Char()
    source_url = fields.Char()
    comment = fields.Char()
    catagery = fields.Char()

    _sql_constraints = [
        ('business_name', 'unique(business_name)', 'business_name already exists!')
    ]

    def load_from_csv(self):
        path = os.path.dirname(os.path.abspath(__file__)) + '/to_load.csv'
        with open(path) as csvfile:
            reader = csv.DictReader(csvfile)
            length = sum(1 for line in open(path))
            for vals in reader:
                try:
                    old_order = self.env['data.order'].search([('business_name', '=', vals['business_name'])])
                    if len(old_order) > 0:
                        old_order.telephone = vals['telephone'] if vals['telephone'] else old_order.telephone
                        old_order.address = vals['address'] if vals['address'] else old_order.address
                        old_order.state = vals['state'] if vals['state'] else old_order.state
                        old_order.post_code = vals['post_code'] if vals['post_code'] else old_order.post_code
                        old_order.manta_url = vals['manta_url'] if vals['manta_url'] else old_order.manta_url
                        old_order.source_url = vals['source_url'] if vals['source_url'] else old_order.source_url
                        old_order.catagery = vals['catagery'] if vals['catagery'] else old_order.catagery
                        old_order.comment = 'unposted'
                        _logger.info('Updated %s from %s. Old record: %s' % (reader.line_num, length, old_order.business_name))
                    else:
                        new_order = self.env['data.order'].create(vals)
                        self._cr.commit()
                        _logger.info('Loaded %s from %s. New record: %s' % (reader.line_num, length, new_order.business_name))
                except Exception as e:
                    self._cr.rollback()
                    _logger.error('WRONG %s. %s' % (vals,e))

    def export_to_csv(self):
        path = os.path.dirname(os.path.abspath(__file__)) + '/export' + time.strftime("%Y%m%d-%H%M%S") + '.csv'
        open(path, 'a').close()
        fieldnames = ["id",
                      "business_name",
                      "telephone",
                      "address",
                      "state",
                      "post_code",
                      "manta_url",
                      "source_url",
                      "comment",
                      "catagery"]
        csvfile = open(path, 'a')
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        recs = self.env['data.order'].search([('comment', '=', 'unposted')])
        l = len(recs)
        cnt = 1
        for rec in recs:
            try:
                writer.writerow({'id': rec.id,
                                 'business_name': rec.business_name,
                                 'telephone': rec.telephone,
                                 'address': rec.address,
                                 'state': rec.state,
                                 'post_code': rec.post_code,
                                 'manta_url': rec.manta_url,
                                 'source_url': rec.source_url,
                                 'comment': rec.comment,
                                 'catagery': rec.catagery,
                                 })
                rec.comment = 'posted'
                _logger.info('Export %s from %s.' % (cnt, l))
            except Exception as e:
                _logger.error('WRONG %s.%s' % (rec.business_name, e))
            cnt += 1
        csvfile.close()


class OrderURL(models.Model):
    _name = "data.url"

    main = fields.Char()
    process = fields.Char()
    unprocessed = fields.Char(compute='_methods_compute', store=True)

    @api.multi
    @api.depends('main', 'process')
    def _methods_compute(self):
        for rec in self:
            try:
                rec.unprocessed = '|'.join(set(rec.main.split("|")) - set(rec.process.split("|")))
            except Exception as e:
                _logger.warning(e)
