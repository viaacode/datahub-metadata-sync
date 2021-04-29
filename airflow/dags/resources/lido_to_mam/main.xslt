<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:lido="http://www.lido-schema.org" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:oai="http://www.openarchives.org/OAI/2.0/" exclude-result-prefixes="xs dc lido">

    <xsl:output method="xml" indent="yes" />

    <!-- template declarations -->
    <!-- catch unmatched elements -->
    <xsl:template match="*">
        <xsl:message terminate="no">
            WARNING: Unmatched element:
            <xsl:value-of select="name()" />
        </xsl:message>

        <xsl:apply-templates />
    </xsl:template>

    <xsl:template match="oai:record" name="main">
        <MediaHAVEN_external_metadata version="1.0" name="VIAA Datamodel">
            <MDProperties>
                <!-- dc_identifier_localid -->
                <dc_identifier_localids type="list">
                    <PersistenteURI_Record>
                        <xsl:value-of select="oai:metadata/lido:lido/lido:lidoRecID[@lido:type='purl']/text()" />
                    </PersistenteURI_Record>
                    <PersistenteURI_Work>
                        <xsl:value-of select="oai:metadata/lido:lido/lido:objectPublishedID[@lido:type='purl']/text()" />
                    </PersistenteURI_Work>
                </dc_identifier_localids>

                <!-- dc_title -->
                <xsl:for-each select="oai:metadata/lido:lido/lido:descriptiveMetadata/lido:objectIdentificationWrap/lido:titleWrap/lido:titleSet/lido:appellationValue[@lido:pref='preferred']">
                    <xsl:if test="position() = 1">
                        <dc_title>
                            <xsl:value-of select="." />
                        </dc_title>
                    </xsl:if>
                </xsl:for-each>

                <!-- dc_titles -->
<!--                 <dc_titles type="list">
                    <xsl:for-each select="oai:metadata/lido:lido/lido:descriptiveMetadata/lido:objectIdentificationWrap/lido:titleWrap/lido:titleSet/lido:appellationValue[@lido:pref='alternate']">
                        <alternatief>
                            <xsl:value-of select="." />
                        </alternatief>
                    </xsl:for-each>
                </dc_titles> -->

                <!-- dc_coverages -->
                <dc_coverages type="list">
                    <tijd >
                    <xsl:value-of select="oai:metadata/lido:lido/lido:descriptiveMetadata/lido:eventWrap/lido:eventSet/lido:event[lido:eventType/lido:term/text() = 'production']/lido:eventDate/lido:displayDate" />
                    </tijd >
                </dc_coverages>

                <!-- dc_creators -->

                <dc_creators type="list">
                    <xsl:for-each select="oai:metadata/lido:lido/lido:descriptiveMetadata/lido:eventWrap/lido:eventSet/lido:event[lido:eventType/lido:term/text() = 'production']/lido:eventActor/lido:actorInRole/lido:actor/lido:nameActorSet/lido:appellationValue[@lido:pref='preferred']">
                        <Maker>
                            <xsl:value-of select="." />
                        </Maker>
                    </xsl:for-each>

                </dc_creators>


                <!-- dc_subjects-->
                <dc_subjects type="list">
                    <xsl:for-each select="oai:metadata/lido:lido/lido:descriptiveMetadata/lido:objectClassificationWrap/lido:objectWorkTypeWrap/lido:objectWorkType/lido:term[@lido:pref='preferred']">
                        <Trefwoord>
                            <xsl:value-of select="." />
                        </Trefwoord>
                    </xsl:for-each>
                    <xsl:for-each select="oai:metadata/lido:lido/lido:descriptiveMetadata/lido:objectClassificationWrap/lido:classificationWrap/lido:classification[*]/lido:term[@lido:pref='preferred']">
                        <Trefwoord>
                            <xsl:value-of select="." />
                        </Trefwoord>
                    </xsl:for-each>
                </dc_subjects>

            </MDProperties>
        </MediaHAVEN_external_metadata>
    </xsl:template>


</xsl:stylesheet>
