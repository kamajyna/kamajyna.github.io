<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:atom="http://www.w3.org/2005/Atom">
  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <title><xsl:value-of select="/atom:feed/atom:title"/> - RSS 피드</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"/>
        <style type="text/css">
          body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }
          .notice { background: #e8f4fd; border-left: 4px solid #3b82f6; padding: 15px; margin-bottom: 30px; border-radius: 6px; color: #1e3a8a; font-size: 15px; }
          .header { background: #fff; padding: 40px 30px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 30px; text-align: center; }
          .header h1 { margin: 0 0 10px 0; color: #111827; font-size: 28px; }
          .header p { margin: 0; color: #6b7280; font-size: 16px; }
          .header a { display: inline-block; margin-top: 20px; padding: 8px 16px; background-color: #f3f4f6; color: #374151; text-decoration: none; border-radius: 6px; font-weight: 500; transition: background-color 0.2s; }
          .header a:hover { background-color: #e5e7eb; }
          .article { background: #fff; padding: 25px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; transition: transform 0.2s, box-shadow 0.2s; border: 1px solid #f3f4f6; }
          .article:hover { transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
          .article h2 { margin: 0 0 10px 0; font-size: 20px; line-height: 1.4; }
          .article h2 a { color: #111827; text-decoration: none; }
          .article h2 a:hover { color: #3b82f6; }
          .meta { font-size: 14px; color: #6b7280; margin-bottom: 10px; }
        </style>
      </head>
      <body>
        <div class="notice">
          <strong>💡 이것은 RSS 피드입니다.</strong> 이 페이지의 주소(URL)를 복사하여 RSS 리더(예: Feedly)에 추가하시면 새 글을 편하게 구독하실 수 있습니다.
        </div>
        
        <div class="header">
          <h1><xsl:value-of select="/atom:feed/atom:title"/></h1>
          <p><xsl:value-of select="/atom:feed/atom:subtitle"/></p>
          <a href="{/atom:feed/atom:link[@rel='alternate']/@href}">← 블로그로 돌아가기</a>
        </div>

        <xsl:for-each select="/atom:feed/atom:entry">
          <div class="article">
            <h2>
              <a href="{atom:link[@rel='alternate']/@href}" target="_blank">
                <xsl:value-of select="atom:title"/>
              </a>
            </h2>
            <div class="meta">
              발행일: <xsl:value-of select="substring(atom:published, 1, 10)"/>
            </div>
          </div>
        </xsl:for-each>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
