#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of Efforia Open Source Initiative.
#
# Copyright (C) 2011-2014 William Oliveira de Lagos <william@efforia.com.br>
#
# Shipping is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shipping is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Shipping. If not, see <http://www.gnu.org/licenses/>.
#


from beautifulsoup import BeautifulSoup
import cookielib
import re
import urllib
import urllib2

URL_CORREIOS = 'http://www.buscacep.correios.com.br/servicos/dnec/'

class CorreiosCode():
    def __init__(self, proxy=None):
        cj = cookielib.LWPCookieJar()
        cookie_handler = urllib2.HTTPCookieProcessor(cj)
        if proxy:
            proxy_handler = urllib2.ProxyHandler({'http': proxy})
            opener = urllib2.build_opener(proxy_handler, cookie_handler)
        else:
            opener = urllib2.build_opener(cookie_handler)
        urllib2.install_opener(opener)

    def _url_open(self, url, data=None, headers=None):
        if headers == None:
            headers = {}

        headers['User-agent'] = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        encoded_data = urllib.urlencode(data) if data else None
        url = URL_CORREIOS + url

        req = urllib2.Request(url, encoded_data, headers)
        handle = urllib2.urlopen(req)

        return handle

    def _parse_detalhe(self, html):
        soup = BeautifulSoup(html.decode('ISO-8859-1'))

        value_cells = soup.findAll('td', attrs={'class': 'value'})
        values = [cell.firstText(text=True) for cell in value_cells]
        localidade, uf = values[2].split('/')
        values_dict = {
            'Logradouro': values[0],
            'Bairro': values[1],
            'Localidade': localidade,
            'UF': uf,
            'CEP': values[3]
        }
        return values_dict

    def _parse_linha_tabela(self, tr):
        values = [cell.firstText(text=True) for cell in tr.findAll('td')]
        keys = ['Logradouro', 'Bairro', 'Localidade', 'UF', 'CEP']
        return dict(zip(keys, values))

    def _parse_tabela(self, html):
        soup = BeautifulSoup(html)
        linhas = soup.findAll('tr', attrs={
            'onclick': re.compile(r"javascript:detalharCep\('\d+','\d+'\);")
        })
        return [self._parse_linha_tabela(linha) for linha in linhas]

    def _parse_faixa(self, html):
        if u"não está cadastrada" in html.decode('cp1252'):
            return None
        ceps = re.findall('\d{5}-\d{3}', html)
        if len(ceps) == 4 or len(ceps) == 6: #uf (+ uf) + cidade com range
            return tuple(ceps[-2:])
        elif len(ceps) == 3 or len(ceps) == 5: #uf (+ uf) + cidade com cep único
            return ceps[-1]
        else:
            raise ValueError("HTML recebido não é válido")

    def detalhe(self, posicao=0):
        """Retorna o detalhe de um CEP da última lista de resultados"""
        handle = self._url_open('detalheCEPAction.do', {'Metodo': 'detalhe',
                                                        'TipoCep': 2,
                                                        'Posicao': posicao + 1,
                                                        'CEP': ''})
        html = handle.read()
        return self._parse_detalhe(html)

    def consulta_faixa(self, localidade, uf):
        """Consulta site e retorna faixa para localidade"""
        url = 'consultaFaixaCepAction.do'
        data = {
            'UF': uf,
            'Localidade': localidade.encode('cp1252'),
            'cfm': '1',
            'Metodo': 'listaFaixaCEP',
            'TipoConsulta': 'faixaCep',
            'StartRow': '1',
            'EndRow': '10',
        }
        html = self._url_open(url, data).read()
        return self._parse_faixa(html)

    def consulta(self, endereco, primeiro=False,
                 uf=None, localidade=None, tipo=None, numero=None):
        """Consulta site e retorna lista de resultados"""

        if uf is None:
            url = 'consultaEnderecoAction.do'
            data = {
                'relaxation': endereco.encode('ISO-8859-1'),
                'TipoCep': 'ALL',
                'semelhante': 'N',
                'cfm': 1,
                'Metodo': 'listaLogradouro',
                'TipoConsulta': 'relaxation',
                'StartRow': '1',
                'EndRow': '10'
            }
        else:
            url = 'consultaLogradouroAction.do'
            data = {
                'Logradouro': endereco.encode('ISO-8859-1'),
                'UF': uf,
                'TIPO': tipo,
                'Localidade': localidade.encode('ISO-8859-1'),
                'Numero': numero,
                'cfm': 1,
                'Metodo': 'listaLogradouro',
                'TipoConsulta': 'logradouro',
                'StartRow': '1',
                'EndRow': '10'
            }

        h = self._url_open(url, data)
        html = h.read()

        if primeiro:
            return self.detalhe()
        else:
            return self._parse_tabela(html)
