# -*- encoding: utf-8 -*-

import csv
import re
import unittest

import bdi.sources.uta1

import hgvs.variant
import hgvs.hgvsmapper as hgvsmapper
import hgvs.parser


def gcp_file_reader(fn):
    rdr = csv.DictReader(open(fn, 'r'), delimiter='\t')
    for rec in rdr:
        if rec['id'].startswith('#'):
            continue
        yield rec


class Test_HGVSMapper(unittest.TestCase):
    def setUp(self):
        self.bdi = bdi.sources.uta1.connect()
        self.hm = hgvs.hgvsmapper.HGVSMapper(self.bdi, cache_transcripts=True)
        self.hp = hgvs.parser.Parser()


    # ZCCHC3 -- one exon, + strand
    # reece@[local]/uta_dev=> select hgnc,alt_strand,n_exons,tx_ac,alt_ac,s_cigars,cds_start_i,cds_end_i from bermuda.bermuda_data_mv where tx_ac = 'NM_033089.6';
    # ┌────────┬────────────┬─────────┬─────────────┬──────────────┬─────────────┬─────────────┬───────────┐
    # │  hgnc  │ alt_strand │ n_exons │    tx_ac    │    alt_ac    │  s_cigars   │ cds_start_i │ cds_end_i │
    # ├────────┼────────────┼─────────┼─────────────┼──────────────┼─────────────┼─────────────┼───────────┤
    # │ ZCCHC3 │          1 │       1 │ NM_033089.6 │ NC_000020.10 │ 484=3I2275= │          24 │      1236 │
    # └────────┴────────────┴─────────┴─────────────┴──────────────┴─────────────┴─────────────┴───────────┘
    def test_ZCCHC3_dbSNP(self):
        for rec in gcp_file_reader('tests/data/ZCCHC3-dbSNP.tsv'):
            self._test_gcp_mapping(rec)


    # ORAI1 -- two exons, + strand
    # reece@[local]/uta_dev=> select hgnc,alt_strand,n_exons,tx_ac,alt_ac,s_cigars,cds_start_i,cds_end_i from bermuda.bermuda_data_mv where tx_ac = 'NM_032790.3';
    # ┌───────┬────────────┬─────────┬─────────────┬──────────────┬──────────────────┬─────────────┬───────────┐
    # │ hgnc  │ alt_strand │ n_exons │    tx_ac    │    alt_ac    │     s_cigars     │ cds_start_i │ cds_end_i │
    # ├───────┼────────────┼─────────┼─────────────┼──────────────┼──────────────────┼─────────────┼───────────┤
    # │ ORAI1 │          1 │       2 │ NM_032790.3 │ NC_000012.11 │ 319=6I177=;1000= │         193 │      1099 │
    # └───────┴────────────┴─────────┴─────────────┴──────────────┴──────────────────┴─────────────┴───────────┘
    def test_ORAI1_dbSNP(self):
        for rec in gcp_file_reader('tests/data/ORAI1-dbSNP.tsv'):
            self._test_gcp_mapping(rec)


    # FOLR3 -- multiple exons, + strand
    # reece@[local]/uta_dev=> select hgnc,alt_strand,n_exons,tx_ac,alt_ac,s_cigars,cds_start_i,cds_end_i from bermuda.bermuda_data_mv where tx_ac = 'NM_000804.2';
    # ┌───────┬────────────┬─────────┬─────────────┬─────────────┬──────────────────────────────┬─────────────┬───────────┐
    # │ hgnc  │ alt_strand │ n_exons │    tx_ac    │   alt_ac    │           s_cigars           │ cds_start_i │ cds_end_i │
    # ├───────┼────────────┼─────────┼─────────────┼─────────────┼──────────────────────────────┼─────────────┼───────────┤
    # │ FOLR3 │          1 │       5 │ NM_000804.2 │ NC_000011.9 │ 44=;174=;150=2D37=;136=;304= │          50 │       788 │
    # └───────┴────────────┴─────────┴─────────────┴─────────────┴──────────────────────────────┴─────────────┴───────────┘
    def test_FOLR3_dbSNP(self):
        # TODO: CORE-158: g-to-c mapped insertions have incorrect interval bounds
        for rec in gcp_file_reader('tests/data/FOLR3-dbSNP.tsv'):
            self._test_gcp_mapping(rec)


    # ADRA2B -- one exon, - strand
    # reece@[local]/uta_dev=> select hgnc,alt_strand,n_exons,tx_ac,alt_ac,s_cigars,cds_start_i,cds_end_i from bermuda.bermuda_data_mv where tx_ac = 'NM_000682.5';
    # ┌────────┬────────────┬─────────┬─────────────┬──────────────┬─────────────┬─────────────┬───────────┐
    # │  hgnc  │ alt_strand │ n_exons │    tx_ac    │    alt_ac    │  s_cigars   │ cds_start_i │ cds_end_i │
    # ├────────┼────────────┼─────────┼─────────────┼──────────────┼─────────────┼─────────────┼───────────┤
    # │ ADRA2B │         -1 │       1 │ NM_000682.5 │ NC_000002.11 │ 891=9D2375= │           0 │      1353 │
    # └────────┴────────────┴─────────┴─────────────┴──────────────┴─────────────┴─────────────┴───────────┘
    def test_ADRA2B_dbSNP(self):
        for rec in gcp_file_reader('tests/data/ADRA2B-dbSNP.tsv'):
            self._test_gcp_mapping(rec)


    # JRK -- multiple exons, - strand
    # reece@[local]/uta_dev=> select hgnc,alt_strand,n_exons,tx_ac,alt_ac,s_cigars,cds_start_i,cds_end_i from bermuda.bermuda_data_mv where tx_ac = 'NM_001077527.1';
    # ┌──────┬────────────┬─────────┬────────────────┬──────────────┬───────────────────────┬─────────────┬───────────┐
    # │ hgnc │ alt_strand │ n_exons │     tx_ac      │    alt_ac    │       s_cigars        │ cds_start_i │ cds_end_i │
    # ├──────┼────────────┼─────────┼────────────────┼──────────────┼───────────────────────┼─────────────┼───────────┤
    # │ JRK  │         -1 │       3 │ NM_001077527.1 │ NC_000008.10 │ 52=;1844=2I199=;1483= │         514 │      2185 │
    # └──────┴────────────┴─────────┴────────────────┴──────────────┴───────────────────────┴─────────────┴───────────┘
    def test_JRK_dbSNP(self):
        # TODO: CORE-157: del26 on -1 strands gets reverse complemented as del62
        for rec in gcp_file_reader('tests/data/JRK-dbSNP.tsv'):
            self._test_gcp_mapping(rec)


    def test_NEFL_dbSNP(self):
        for rec in gcp_file_reader('tests/data/NEFL-dbSNP.tsv'):
            self._test_gcp_mapping(rec)


    def test_DNAH11_hgmd(self):
        for rec in gcp_file_reader('tests/data/DNAH11-HGMD.tsv'):
            self._test_gcp_mapping(rec)

    def test_DNAH11_dbSNP_NM_003777(self):
        for rec in gcp_file_reader('tests/data/DNAH11-dbSNP-NM_003777.tsv'):
            self._test_gcp_mapping(rec)

    def test_DNAH11_dbSNP_NM_001277115(self):
        for rec in gcp_file_reader('tests/data/DNAH11-dbSNP-NM_001277115.tsv'):
            self._test_gcp_mapping(rec)


    def test_real(self):
        for rec in gcp_file_reader('tests/data/real_gcp.tsv'):
            self._test_gcp_mapping(rec)


    def _test_gcp_mapping(self, rec):
        var_g = self.hp.parse_hgvs_variant(rec['HGVSg'])
        var_c = self.hp.parse_hgvs_variant(rec['HGVSc'])
        var_p = self.hp.parse_hgvs_variant(rec['HGVSp']) if rec['HGVSp'] is not None and rec['HGVSp'] != '' else None

        # g -> c
        var_c_test = self.hm.hgvsg_to_hgvsc(var_g, var_c.ac)
        self.assertEquals(str(var_c_test), str(var_c),
                          msg="%s != %s (%s)" % (str(var_c_test),str(var_c),rec['id']))

        # c -> g
        var_g_test = self.hm.hgvsc_to_hgvsg(var_c, var_g.ac)
        self.assertEquals(str(var_g_test), str(var_g),
                          msg="%s != %s (%s)" % (str(var_g_test),str(var_g),rec['id']))

        if var_p is not None:
            # c -> p
            hgvs_p_exp = str(var_p)

            var_p_test = self.hm.hgvsc_to_hgvsp(var_c, var_p.ac)

            if not var_p.posedit.uncertain:
                # if expected value isn't uncertain, strip uncertain from test
                var_p_test.posedit.uncertain = False

            hgvs_p_test = str(var_p_test)

            if re.search('Ter$',hgvs_p_exp):
                # if expected value doesn't have a count, strip it from the test
                hgvs_p_test = re.sub('Ter\d+$','Ter',hgvs_p_test)
            
            self.assertEquals(hgvs_p_exp, hgvs_p_test,
                              msg="%s != %s (%s)" % (hgvs_p_exp,hgvs_p_test,rec['id']))


if __name__ == '__main__':
    unittest.main()

## <LICENSE>
## Copyright 2014 HGVS Contributors (https://bitbucket.org/invitae/hgvs)
## 
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
## 
##     http://www.apache.org/licenses/LICENSE-2.0
## 
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
## </LICENSE>
