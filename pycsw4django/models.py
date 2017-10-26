from django.db import models
from lxml import etree
from django.conf import settings
from django.template.defaultfilters import slugify
from shapely.wkt import loads


class Resource(models.Model):
    # CSW specific properties
    name = models.CharField(max_length=255)
    wkt_geometry = models.TextField(blank=True)
    csw_typename = models.CharField(
        max_length=200, default="csw:Record")
    csw_schema = models.CharField(
        max_length=200,
        default="http://www.opengis.net/cat/csw/2.0.2")
    csw_mdsource = models.CharField(
        max_length=100, default="local")
    csw_xml = models.TextField(blank=True)
    csw_anytext = models.TextField(blank=True)

    # CSW specific properties
    @property
    def csw_identifier(self):
        if not settings.SITEHOST:
            raise RuntimeError('settings.SITEHOST is not set')
        fqrhn = '.'.join((reversed(settings.SITEHOST.split('.'))))
        return 'urn:x-odc:resource:%s::%d' % (fqrhn, self.id)

    @property
    def csw_type(self):
        data_types = self.data_types.values()
        if len(data_types) > 0:
            return data_types[0]['data_type']
        return None

    @property
    def csw_crs(self):
        crs = self.coord_sys.values()
        if len(crs) > 0:
            return crs[0]['name']
        return None

    @property
    def csw_links(self):
        links = []
        for url in self.url_set.all():
            tmp = '%s,%s,%s,%s' % (
                url.url_label, url.url_type.url_type,
                'WWW:DOWNLOAD-1.0-http--download', url.url)
            links.append(tmp)

        abs_url = '%s%s' % (gen_website_url(),
                            self.get_absolute_url())
        link = '%s,%s,%s,%s' % (self.name, self.name,
                                'WWW:LINK-1.0-http--link', abs_url)
        links.append(link)
        return '^'.join(links)

    @property
    def csw_keywords(self):
        keywords = []
        for keyword in self.tags.values():
            keywords.append(keyword['tag_name'])
        return ','.join(keywords)

    @property
    def csw_creator(self):
        # creator = User.objects.filter(username=self.created_by)[0]
        creator = "the Kaos"
        return '%s %s' % (creator.first_name, creator.last_name)

    def gen_csw_xml(self):

        def nspath(ns, element):
            return '{%s}%s' % (ns, element)

        nsmap = {
            'csw': 'http://www.opengis.net/cat/csw/2.0.2',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'dct': 'http://purl.org/dc/terms/',
            'ows': 'http://www.opengis.net/ows',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        }

        record = etree.Element(nspath(nsmap['csw'], 'Record'),
                               nsmap=nsmap)
        etree.SubElement(record, nspath(
            nsmap['dc'], 'identifier')).text = self.csw_identifier
        etree.SubElement(
            record, nspath(nsmap['dc'], 'title')).text = self.name

        if self.csw_type is not None:
            etree.SubElement(
                record, nspath(nsmap['dc'], 'type')).text = self.csw_type

        for tag in self.tags.all():
            etree.SubElement(
                record, nspath(nsmap['dc'], 'subject')).text = tag.tag_name

        etree.SubElement(
            record, nspath(
                nsmap['dc'], 'format')).text = str(self.data_formats)

        abs_url = '%s%s' % (gen_website_url(), self.get_absolute_url())
        etree.SubElement(record, nspath(nsmap['dct'], 'references'),
                         scheme='WWW:LINK-1.0-http--link').text = abs_url

        for link in self.url_set.all():
            etree.SubElement(
                record, nspath(nsmap['dct'], 'references'),
                scheme='WWW:DOWNLOAD-1.0-http--download').text = link.url

        etree.SubElement(record, nspath(
            nsmap['dct'], 'modified')).text = str(self.last_updated)
        etree.SubElement(record, nspath(
            nsmap['dct'], 'abstract')).text = self.description

        etree.SubElement(record, nspath(
            nsmap['dc'], 'date')).text = str(self.created)
        etree.SubElement(record, nspath(
            nsmap['dc'], 'creator')).text = str(self.csw_creator)

        etree.SubElement(record, nspath(
            nsmap['dc'], 'coverage')).text = self.area_of_interest

        try:
            geom = loads(self.wkt_geometry)
            bounds = geom.envelope.bounds
            dimensions = str(geom.envelope._ndim)

            bbox = etree.SubElement(record, nspath(
                nsmap['ows'], 'BoundingBox'), dimensions=dimensions)

            if self.csw_crs is not None:
                bbox.attrib['crs'] = self.csw_crs

            etree.SubElement(bbox, nspath(
                nsmap['ows'], 'LowerCorner')).text = '%s %s' % (
                    bounds[1], bounds[0])
            etree.SubElement(bbox, nspath(
                nsmap['ows'], 'UpperCorner')).text = '%s %s' % (
                    bounds[3], bounds[2])
        except Exception:
            # We can safely ignore geom issues
            pass

        return etree.tostring(record)

    def gen_csw_anytext(self):
        xml = etree.fromstring(self.csw_xml)
        return ' '.join([value.strip() for value in xml.xpath('//text()')])

    def get_absolute_url(self):
        slug = slugify(self.name)
        return "/opendata/resource/%i/%s" % (self.id, slug)


def gen_website_url():
    if not settings.SITEHOST:
        raise RuntimeError('settings.SITEHOST is not set')
    if not settings.SITEPORT:
        raise RuntimeError('settings.SITEPORT is not set')

    scheme = 'http'
    port = ':%d' % settings.SITEPORT

    if settings.SITEPORT == 443:
        scheme = 'https'
    if settings.SITEPORT == 80:
        port = ''
    return '%s://%s%s' % (scheme, settings.SITEHOST, port)
