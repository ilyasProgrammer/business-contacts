# -*- coding: utf-8 -*-

from odoo import fields, models
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
    main = fields.Char()
    process = fields.Char()
    unprocessed = fields.Char()

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
                      "main",
                      "process",
                      "unprocessed",
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
                                 'main': rec.main,
                                 'process': rec.process,
                                 'unprocessed': rec.unprocessed,
                                 'catagery': rec.catagery,
                                 })
            except:
                _logger.error('WRONG %s.' % rec.business_name)
            _logger.info('Export %s from %s.' % (cnt, l))
            cnt += 1
        csvfile.close()
