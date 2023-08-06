<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output encoding="utf-8"/>
<xsl:output method="text"/>

<xsl:strip-space elements="*" />

<xsl:template match="para">
<xsl:apply-templates />
<xsl:text>&#10;&#10;</xsl:text>
</xsl:template>

<xsl:template match="parameternamelist">
<xsl:for-each select="parametername">
:param <xsl:value-of select="text()" />
<xsl:if test="position() != last()">
<xsl:text>,</xsl:text>
</xsl:if>
</xsl:for-each>
<xsl:text>: </xsl:text>
<xsl:for-each select="parameterdescription">
<xsl:apply-templates />
</xsl:for-each>
</xsl:template>

<xsl:template match="simplesect[@kind='return']">
:return: <xsl:value-of select=".//text()"/>
<xsl:text>&#10;</xsl:text>
</xsl:template>

<xsl:template match="simplesect[@kind='see']">
See also <xsl:value-of select=".//text()"/>
</xsl:template>

<xsl:template match="sp">
<xsl:text> </xsl:text>
</xsl:template>

<xsl:template match="programlisting">
<xsl:text>::&#10;</xsl:text>
<xsl:for-each select="codeline">
<xsl:apply-templates />
<xsl:text>&#10;</xsl:text>
</xsl:for-each>
</xsl:template>

<xsl:template match="/">
<dox>
<xsl:for-each select=".//memberdef[@kind='function']">
<function>
<xsl:attribute name="name"><xsl:apply-templates select="name"/></xsl:attribute>
<xsl:for-each select="briefdescription"><xsl:apply-templates /></xsl:for-each>
<xsl:apply-templates select="detaileddescription" />
</function>
</xsl:for-each>
</dox>
</xsl:template>

</xsl:stylesheet>
